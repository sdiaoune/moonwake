"""Compile and exercise the production GBC save code in a native harness.

Fixtures are cartridge SRAM supplied before boot. The Python observer reads RAM
but never writes it. Joypad presses make the harness call production save/reset
functions; deliberately artificial states are not evidence of gameplay progress.
"""
from pathlib import Path
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

from pyboy import PyBoy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/critic-expansion-save"
GBDK = Path(os.environ.get("GBDK", "/opt/gbdk"))
OUT.mkdir(parents=True, exist_ok=True)
ROM = OUT / "save-probe.gbc"
SOURCE = ROOT / "src/save.c"

HARNESS = r'''
#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include <string.h>
#include "game.h"
uint8_t game_mode,stage_id,input,pressed,previous_input,frame;
uint8_t health,grounded,dash_charge,dash_timer,seal_count,stars,combo;
uint8_t unlocked,completed,save_valid,sound_on=1,map_selection,story_next;
uint8_t medal[LEVEL_COUNT];uint16_t seal_bits[LEVEL_COUNT],run_seal_bits;
uint8_t room_id,room_taken_bits[8],migrated_save,stage_clear_pending;
uint32_t journey_frames;
uint16_t best_frames[LEVEL_COUNT],deaths,stage_frames,camera_x,checkpoint_x;
int16_t player_x,player_y,velocity_x,velocity_y;
uint8_t title_selection,checkpoint_on,save_slot,current_rank,boss_hp;
volatile uint8_t harness_ready,harness_actions;
static void sample(uint8_t second){
 uint8_t i;
 unlocked=second?20:23;completed=second?0:1;stage_id=second?17:23;
 room_id=second?1:2;checkpoint_on=1;health=second?1:2;
 stage_clear_pending=second?0:1;
 stars=second?44:97;deaths=second?0x4567:0x3456;
 stage_frames=second?54321u:60000u;run_seal_bits=second?0x155:0x1ff;
 seal_count=second?5:9;sound_on=second?1:0;
 journey_frames=second?0x89abcdefUL:0x01020304UL;
 for(i=0;i<LEVEL_COUNT;i++){medal[i]=second?i%4:3;seal_bits[i]=second?(0x155u+i)&0x1ff:0x1ff;best_frames[i]=second?40000u+i:60000u-i;}
 for(i=0;i<8;i++)room_taken_bits[i]=second?0xa5u^i:0x5au+i;
}
void main(void){
 cpu_fast();health=3;save_read();harness_ready=1;
 while(1){vsync();input=joypad();pressed=input&~previous_input;previous_input=input;
  if(pressed&J_A){sample(0);save_write();harness_actions++;}
  if(pressed&J_B){sample(1);save_write();harness_actions++;}
  if(pressed&J_START){save_write();harness_actions++;}
  if(pressed&J_SELECT){save_reset();harness_actions++;}
 }
}
'''


def crc(data, end):
    c = 0xFFFF
    for b in data[1:end]:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x1021) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


def put16(data, at, value):
    data[at:at + 2] = value.to_bytes(2, "little")


def make_v1(sequence, *, complete=False, unlocked=7, sound=1, seed=0):
    b = bytearray(64)
    b[:3] = b"MW\x01"
    put16(b, 3, sequence)
    b[5:8] = bytes((unlocked, int(complete), sound))
    b[8:20] = bytes([3] * 12)
    b[20:32] = bytes((i + seed) & 7 for i in range(12))
    for i in range(12):
        put16(b, 32 + i * 2, 1000 + i)
    put16(b, 56, 321 + seed)
    b[58] = min(unlocked, 5)
    put16(b, 62, crc(b, 62))
    return b


def make_v2(sequence, *, unlocked=23, stage=23, room=2, health=2, seed=0, pending=0, complete=0):
    b = bytearray(192)
    b[:3] = b"MW\x02"
    put16(b, 3, sequence)
    b[5:13] = bytes((unlocked, complete, 1, stage, room, 1, health, 44 + seed))
    b[13] = pending
    put16(b, 14, 4321 + seed)
    put16(b, 16, 50000 + seed)
    put16(b, 18, 0x1FF)
    b[24:48] = bytes([3] * 24)
    for i in range(24):
        put16(b, 48 + i * 2, 0x1FF)
        put16(b, 96 + i * 2, 45000 + i)
    b[144:148] = (0x01020304 + seed).to_bytes(4, "little")
    b[152:160] = bytes(0xF0 ^ i for i in range(8))
    put16(b, 190, crc(b, 190))
    return b


def fixture(*, a1=None, b1=None, a2=None, b2=None):
    # Signal Bloom-like sentinels and non-MW SRAM must survive byte-for-byte.
    data = bytearray((i * 37 + 13) & 255 for i in range(8192))
    data[:128] = bytes(128)
    marker = b"SB\x01ORIGINAL-SAVE-DATA"
    data[:len(marker)] = marker
    marker = b"SB\x01SECOND-SLOT!!!"
    data[0x80:0x80 + len(marker)] = marker
    for at, size, value in ((0x100, 64, a1), (0x180, 64, b1),
                            (0x200, 192, a2), (0x300, 192, b2)):
        data[at:at + size] = value if value is not None else bytes(size)
    return bytes(data)


def same_untouched(before, after):
    assert len(before) == len(after) == 8192
    changed = [i for i, (a, b) in enumerate(zip(before, after))
               if a != b and not (0x200 <= i < 0x2C0 or 0x300 <= i < 0x3C0 or 0x3F0 <= i < 0x3F4)]
    assert not changed, ("save wrote outside its two v2 slots and generation fence", changed[:10])
    return True


class Native:
    def __init__(self, data):
        self.ram = io.BytesIO(data)
        self.p = PyBoy(str(ROM), window="null", cgb=True, ram_file=self.ram)
        self.p.set_emulation_speed(0)
        self.p.tick(180)
        assert self.read("harness_ready") == 1

    def read(self, name, size=1):
        at = SYMS["_" + name][1]
        return sum(self.p.memory[at + i] << (8 * i) for i in range(size))

    def array(self, name, length, width=1):
        at = SYMS["_" + name][1]
        return [sum(self.p.memory[at + i * width + j] << (8 * j) for j in range(width))
                for i in range(length)]

    def state(self):
        s = {n: self.read(n) for n in ("unlocked", "completed", "sound_on", "stage_id", "room_id",
                                        "checkpoint_on", "health", "stars", "seal_count", "save_valid", "save_slot", "migrated_save", "stage_clear_pending")}
        s.update({n: self.read(n, 2) for n in ("deaths", "stage_frames", "run_seal_bits")})
        s["journey_frames"] = self.read("journey_frames", 4)
        s["medal"] = self.array("medal", 24)
        s["seal_bits"] = self.array("seal_bits", 24, 2)
        s["best_frames"] = self.array("best_frames", 24, 2)
        s["room_taken_bits"] = self.array("room_taken_bits", 8)
        return s

    def tap(self, button):
        before = self.read("harness_actions")
        self.p.button_press(button)
        self.p.tick(3)
        self.p.button_release(button)
        self.p.tick(30)
        assert self.read("harness_actions") == before + 1

    def close(self):
        self.ram.seek(0)
        self.p.stop(ram_file=self.ram)
        return self.ram.getvalue()[:8192]


def verify_sample(state, second=False):
    expected = dict(unlocked=20 if second else 23, completed=0 if second else 1,
                    sound_on=1 if second else 0, stage_id=17 if second else 23,
                    room_id=1 if second else 2, checkpoint_on=1, health=1 if second else 2,
                    stage_clear_pending=0 if second else 1,
                    stars=44 if second else 97, deaths=0x4567 if second else 0x3456,
                    stage_frames=54321 if second else 60000, run_seal_bits=0x155 if second else 0x1FF,
                    seal_count=5 if second else 9, journey_frames=0x89ABCDEF if second else 0x01020304,
                    medal=[i % 4 for i in range(24)] if second else [3] * 24,
                    seal_bits=[(0x155 + i) & 0x1FF for i in range(24)] if second else [0x1FF] * 24,
                    best_frames=[40000 + i for i in range(24)] if second else [60000 - i for i in range(24)],
                    room_taken_bits=[0xA5 ^ i for i in range(8)] if second else [0x5A + i for i in range(8)])
    for key, value in expected.items():
        assert state[key] == value, (key, state[key], value)
    assert state["save_valid"]


def check_slot(data, at):
    b = data[at:at + 192]
    assert b[:3] == b"MW\x02"
    assert int.from_bytes(b[190:192], "little") == crc(b, 190)
    return int.from_bytes(b[3:5], "little")


def boot_case(data):
    t = Native(data)
    state = t.state()
    result = t.close()
    same_untouched(data, result)
    return state, result


def run():
    report = {"source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "harness_rom_sha256": hashlib.sha256(ROM.read_bytes()).hexdigest(),
              "evidence": "Compiled actual production save.c with GBDK; synthetic SRAM supplied before boot; observer reads only; joypad invokes save/reset.",
              "checks": {}, "defects": []}
    checks = report["checks"]
    base = fixture()
    blank, _ = boot_case(base)
    assert not blank["save_valid"] and not blank["unlocked"]
    checks["blank_safe_start"] = blank

    for complete in (False, True):
        old = make_v1(100, complete=complete, unlocked=11 if complete else 7, sound=0)
        newer = make_v1(101, complete=complete, unlocked=11 if complete else 8, sound=1, seed=1)
        data = fixture(a1=old, b1=newer)
        state, migrated = boot_case(data)
        assert state["save_valid"] and state["migrated_save"]
        assert state["unlocked"] == (12 if complete else 8) and not state["completed"]
        assert state["seal_bits"][:12] == list(newer[20:32]) and state["seal_bits"][12:] == [0] * 12
        assert state["medal"] == [0] * 24 and state["best_frames"] == [0] * 24
        assert state["room_id"] == 0 and not state["run_seal_bits"] and not state["journey_frames"] and not state["stage_clear_pending"]
        assert state["deaths"] == 322 and state["sound_on"] == 1
        checks["v1_completed_migration" if complete else "v1_partial_migration"] = state
        (OUT / ("migrated-complete.sav" if complete else "migrated-partial.sav")).write_bytes(migrated)
        resumed, _ = boot_case(migrated)
        assert not resumed["migrated_save"] and resumed["seal_bits"] == state["seal_bits"]

    wrapped, _ = boot_case(fixture(a1=make_v1(65535, unlocked=3), b1=make_v1(0, unlocked=6)))
    assert wrapped["unlocked"] == 6
    checks["v1_sequence_wrap"] = True
    wrapped, _ = boot_case(fixture(a2=make_v2(65535, seed=0), b2=make_v2(0, seed=1)))
    assert wrapped["stars"] == 45 and wrapped["save_slot"] == 1
    checks["v2_sequence_wrap"] = True
    older = make_v1(10, unlocked=3, sound=0)
    bad_newer = make_v1(11, unlocked=8, seed=1)
    bad_newer[20] ^= 1
    older_state, _ = boot_case(fixture(a1=older, b1=bad_newer))
    assert older_state["unlocked"] == 3 and older_state["sound_on"] == 0
    assert older_state["seal_bits"][:12] == list(older[20:32])
    checks["v1_newer_bad_crc_older_migrates"] = True
    older[20] ^= 1
    invalid_legacy, _ = boot_case(fixture(a1=older, b1=bad_newer))
    assert not invalid_legacy["save_valid"] and not invalid_legacy["migrated_save"]
    checks["both_v1_bad_SB_not_interpreted"] = True

    overwide = make_v2(2)
    put16(overwide, 18, 0xFFFF)
    put16(overwide, 48, 0xFFFF)
    overwide[24] = 255
    put16(overwide, 190, crc(overwide, 190))
    masked, _ = boot_case(fixture(a2=overwide))
    assert masked["run_seal_bits"] == 0x1FF and masked["seal_count"] == 9
    assert masked["seal_bits"][0] == 0x1FF and masked["medal"][0] == 0
    checks["nine_bit_seals_and_rank_bounds"] = True

    legacy_base = fixture(a1=make_v1(100, complete=True, unlocked=11), b1=make_v1(101, complete=True, unlocked=11))
    t = Native(legacy_base)
    t.tap("a")
    first = t.state()
    verify_sample(first)
    first_data = t.close()
    same_untouched(legacy_base, first_data)
    assert first_data[0x3F0:0x3F4] == b"MW2!"
    first_reboot, _ = boot_case(first_data)
    verify_sample(first_reboot)
    checks["nine_seals_long_clock_room2_roundtrip"] = first_reboot
    t = Native(first_data)
    t.tap("b")
    second = t.state()
    verify_sample(second, True)
    second_data = t.close()
    same_untouched(legacy_base, second_data)
    second_reboot, _ = boot_case(second_data)
    verify_sample(second_reboot, True)
    checks["midroom1_32bit_journey_roundtrip"] = second_reboot
    sequences = [(check_slot(second_data, at), at) for at in (0x200, 0x300)]
    latest = max(sequences)[1]
    prior = min(sequences)[1]
    damaged = bytearray(second_data)
    damaged[latest + 16] ^= 1
    fallback, _ = boot_case(bytes(damaged))
    verify_sample(fallback)
    checks["latest_crc_bad_prior_restored"] = fallback
    damaged[prior + 16] ^= 1
    fresh, _ = boot_case(bytes(damaged))
    assert not fresh["save_valid"] and not fresh["unlocked"] and not fresh["migrated_save"]
    checks["both_crc_bad_no_v1_resurrection"] = fresh

    # Stronger corruption than an ordinary torn payload: both magic bytes lost.
    header_bad = bytearray(second_data)
    header_bad[0x200] = header_bad[0x300] = 0
    state, _ = boot_case(bytes(header_bad))
    checks["both_magic_bad_with_valid_v1"] = state
    if state["migrated_save"]:
        report["defects"].append({"id": "legacy_resurrection_after_both_v2_magic_loss", "severity": "P2",
                                   "detail": "Both v2 leading magic bytes damaged, but v1 remains valid: boot migrates the old completed v1 playthrough instead of safe initial progress."})
    else:
        assert not state["save_valid"] and not state["unlocked"]
        checks["generation_fence_blocks_header_corruption_resurrection"] = True
    fence_lost = bytearray(header_bad)
    fence_lost[0x3F0:0x3F4] = bytes(4)
    joint_loss, _ = boot_case(bytes(fence_lost))
    assert joint_loss["migrated_save"] and joint_loss["unlocked"] == 12
    checks["joint_fence_and_both_magic_loss_is_indistinguishable_from_legacy_only"] = True

    t = Native(second_data)
    t.tap("select")
    reset = t.state()
    reset_data = t.close()
    same_untouched(legacy_base, reset_data)
    for key in ("unlocked", "completed", "stage_id", "room_id", "deaths", "run_seal_bits", "stage_frames", "journey_frames", "stage_clear_pending"):
        assert reset[key] == 0, (key, reset[key])
    assert reset["seal_bits"] == [0] * 24 and reset["best_frames"] == [0] * 24 and reset["medal"] == [0] * 24
    reset_reboot, _ = boot_case(reset_data)
    assert reset_reboot["save_valid"] and not reset_reboot["unlocked"] and not reset_reboot["migrated_save"]
    checks["reset_persists_legacy_and_SB_untouched"] = reset_reboot
    for name, data in (("written-room2.sav", first_data), ("written-room1.sav", second_data),
                       ("both-crc-bad.sav", bytes(damaged)), ("reset.sav", reset_data)):
        (OUT / name).write_bytes(data)
    checks["all_writes_inside_v2_slots_and_generation_fence_only"] = True
    for room, health in ((3, 2), (2, 0), (2, 4)):
        invalid, _ = boot_case(fixture(a1=make_v1(3, complete=True), a2=make_v2(10, room=room, health=health)))
        assert not invalid["save_valid"] and not invalid["migrated_save"]
    checks["CRC_valid_invalid_room_and_health_rejected"] = True
    pending_mid, _ = boot_case(fixture(a2=make_v2(4, unlocked=20, stage=17, pending=1)))
    assert pending_mid["stage_clear_pending"] == 1 and pending_mid["stage_id"] == 17
    checks["intermediate_clear_pending_roundtrip"] = True
    for args in (dict(pending=2, complete=1), dict(pending=1, room=1, complete=1),
                 dict(pending=1, unlocked=17, stage=17), dict(pending=1, complete=0)):
        bad_flag, _ = boot_case(fixture(a1=make_v1(3, complete=True), a2=make_v2(4, **args)))
        assert not bad_flag["save_valid"] and not bad_flag["migrated_save"]
    checks["invalid_pending_clear_flags_rejected_without_legacy_resurrection"] = True
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"source_sha256": report["source_sha256"], "harness_rom_sha256": report["harness_rom_sha256"],
                      "passed_checks": len(checks), "defects": report["defects"]}, indent=2))


if __name__ == "__main__":
    if not (GBDK / "bin/lcc").is_file():
        raise SystemExit(f"GBDK compiler missing at {GBDK / 'bin/lcc'}. Install GBDK or set GBDK to its installation directory.")
    shutil.copy2(SOURCE, OUT / "save-under-test.c")
    (OUT / "harness.c").write_text(HARNESS)
    subprocess.run([str(GBDK / "bin/lcc"), "-I" + str(ROOT / "src"), "-Wl-m", "-Wl-j",
                    "-Wm-yC", "-Wm-yt0x1B", "-Wm-ya1", "-Wm-yo8", "-Wm-ynSAVEPROBE", "-Wm-yS",
                    "-o", str(ROM), str(OUT / "harness.c"), str(OUT / "save-under-test.c")], check=True)
    assert SOURCE.read_bytes() == (OUT / "save-under-test.c").read_bytes(), "save.c changed while compiling; rerun"
    SYMS = {s[1]: (int(s[0].split(":")[0], 16), int(s[0].split(":")[1], 16))
            for line in ROM.with_suffix(".sym").read_text().splitlines()
            if len(s := line.split()) == 2 and ":" in s[0]}
    run()
