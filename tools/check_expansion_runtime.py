"""Independent controller-only runtime critic for the expanded native ROM.

RAM observation is read-only. Branching native snapshots repeat probes/search
ordinary jumps; accepted input traces are replayed from blank SRAM separately.
"""
from pathlib import Path
import hashlib
import io
import json
import shutil
import statistics
import sys

from pyboy import PyBoy

ROOT = Path(__file__).resolve().parents[1]
if "--copy-hash" in sys.argv:
    key = sys.argv[sys.argv.index("--copy-hash") + 1]
    assert len(key) >= 12 and all(c in "0123456789abcdef" for c in key)
    OUT = ROOT / "build/critic-expansion-runtime" / key[:12]
    sha = hashlib.sha256((OUT / "moonwake.gbc").read_bytes()).hexdigest()
    assert sha.startswith(key)
else:
    sha = hashlib.sha256((ROOT / "dist/moonwake.gbc").read_bytes()).hexdigest()
    OUT = ROOT / "build/critic-expansion-runtime" / sha[:12]
    OUT.mkdir(parents=True, exist_ok=True)
    for source, target in (("dist/moonwake.gbc", "moonwake.gbc"), ("dist/moonwake.sym", "moonwake.sym"), ("docs/routes.json", "routes.json")):
        shutil.copy2(ROOT / source, OUT / target)
ROM = OUT / "moonwake.gbc"
assert len(ROM.read_bytes()) == 524288, "Integrated 512 KiB expansion required"
assert hashlib.sha256(ROM.read_bytes()).hexdigest() == sha
SYMS = {s[1]: (int(s[0].split(":")[0], 16), int(s[0].split(":")[1], 16))
        for line in ROM.with_suffix(".sym").read_text().splitlines()
        if len(s := line.split()) == 2 and ":" in s[0]}
ROUTES = json.loads((OUT / "routes.json").read_text())["levels"]


class Game:
    def __init__(self, data=None):
        self.ram = io.BytesIO(data if data is not None else bytes(8192))
        self.p = PyBoy(str(ROM), window="null", cgb=True, ram_file=self.ram, sound_emulated=True)
        self.p.set_emulation_speed(0)
        self.held = set()
        self.frames = 0
        self.trace = []
        self.observed = {}
        self.events = []
        self.timings = []
        self.p.hook_register(*SYMS["_draw_objects"], self.observe, None)
        for name in ("audio_tick", "game_tick", "physics", "world_tick", "camera_update", "hud_update"):
            if "_" + name in SYMS:
                self.p.hook_register(*SYMS["_" + name], lambda _, n=name: self.mark(n), None)

    def raw(self, name, width=1, signed=False):
        at = SYMS["_" + name][1]
        value = sum(self.p.memory[at + i] << (8 * i) for i in range(width))
        return value - (1 << (8 * width)) if signed and value >= 1 << (8 * width - 1) else value

    def read(self, name, width=1, signed=False):
        return self.observed.get(name, self.raw(name, width, signed))

    def pos(self):
        return self.read("player_x", 2, True) / 16, self.read("player_y", 2, True) / 16

    def mark(self, name):
        self.timings.append((name, self.p._cycles(), self.p.frame_count,
                             self.raw("stage_id"), self.raw("room_id"), self.raw("game_mode")))

    def observe(self, _):
        self.observed = {name: self.raw(name, width, signed) for name, width, signed in
                         (("player_x", 2, True), ("player_y", 2, True), ("velocity_x", 2, True),
                          ("velocity_y", 2, True), ("grounded", 1, False))}
        self.observed["observed_stage_id"] = self.raw("stage_id")
        self.observed["observed_room_id"] = self.raw("room_id")
        self.mark("draw_objects")
        self.events.append({**self.state(), "ppu_frame": self.p.frame_count})

    def state(self):
        s = {n: self.read(n) for n in ("game_mode", "stage_id", "room_id", "health", "grounded", "dash_charge", "dash_timer", "seal_count", "stars", "checkpoint_on", "boss_hp")}
        s.update({n: self.read(n, 2) for n in ("deaths", "stage_frames", "camera_x", "run_seal_bits")})
        s["journey_frames"] = self.read("journey_frames", 4)
        s["x"], s["y"] = self.pos()
        s["vx"] = self.read("velocity_x", 2, True) / 16
        s["vy"] = self.read("velocity_y", 2, True) / 16
        s["video_frame"] = self.frames
        return s

    def tick(self, frames=1, buttons=()):
        buttons = set(buttons)
        for b in self.held - buttons:
            self.p.button_release(b)
        for b in buttons - self.held:
            self.p.button_press(b)
        self.held = buttons
        self.p.tick(frames)
        self.frames += frames
        self.trace.append([frames, sorted(buttons)])

    def tap(self, button, wait=12):
        self.tick(3, [button])
        self.tick(wait)

    def shot(self, name):
        self.p.screen.image.save(OUT / (name + ".png"))

    def line(self, row):
        at = (0x9C00 if self.p.memory[0xFF40] & 0x40 else 0x9800) + row * 32
        return "".join(chr(self.p.memory[at + i]) for i in range(20)).rstrip()

    def checkpoint(self):
        data = io.BytesIO()
        self.p.save_state(data)
        return (data.getvalue(), self.held.copy(), self.frames, len(self.trace), dict(self.observed), len(self.events), len(self.timings))

    def rollback(self, s):
        self.p.load_state(io.BytesIO(s[0]))
        self.held, self.frames = s[1].copy(), s[2]
        self.trace, self.observed = self.trace[:s[3]], dict(s[4])
        self.events, self.timings = self.events[:s[5]], self.timings[:s[6]]

    def start(self):
        self.tick(180)
        self.tap("start", 120)
        if self.read("game_mode") == 5:
            self.tap("a", 90)
        assert self.read("game_mode") == 1

    def route(self):
        return ROUTES[self.read("stage_id")]["rooms"][self.read("room_id")]

    def platform(self, index):
        p = dict(self.route()["platforms"][index])
        at = SYMS["_platforms"][1] + index * 5
        p["x"] = self.p.memory[at] | self.p.memory[at + 1] << 8
        return p

    def current_platform(self):
        x, y = self.pos()
        for i in range(len(self.route()["platforms"])):
            p = self.platform(i)
            if x + 12 > p["x"] and x + 3 < p["x"] + p["w"] and abs(y + 16 - p["y"]) < 2:
                return i

    def walk(self, target, limit=200):
        death = self.read("deaths", 2)
        for _ in range(limit):
            x, _ = self.pos()
            vx = self.read("velocity_x", 2, True) / 16
            delta = target - x
            if abs(delta) < 2 and abs(vx) < .35 and self.read("grounded"):
                self.tick(2)
                return
            buttons = [] if abs(delta) < vx * vx * 1.4 + 1 and delta * vx >= 0 else ["right" if delta > 0 else "left"]
            self.tick(1, buttons)
            assert self.read("deaths", 2) == death, ("walk died", self.state())
        raise AssertionError(("walk timeout", target, self.state()))

    def jump(self, index, collect=None, allow_any_catch=False):
        p = self.platform(index)
        if not self.read("grounded") and self.current_platform() is None:
            for _ in range(60):
                self.tick(1)
                if self.read("grounded"):
                    break
        base = self.checkpoint()
        source = self.current_platform()
        targets = [p["x"] + p["w"] / 2 - 8, p["x"] + 8, p["x"] + p["w"] - 24]
        if collect is not None:
            targets.insert(0, self.route()["pickups"][collect]["x"] - 4)
        for target in targets:
            for hold in (24, 36, 14, 48):
                for dash_at in (-1, 10, 17, 5):
                    self.rollback(base)
                    death = self.read("deaths", 2)
                    if source is not None:
                        src = self.platform(source)
                        if src["kind"] not in (2, 3, 4) and abs(target - self.pos()[0]) > 80:
                            launch = max(src["x"] + 1, min(src["x"] + src["w"] - 17, target - 60 if target > self.pos()[0] else target + 60))
                            try:
                                self.walk(launch)
                            except AssertionError:
                                self.rollback(base)
                    self.tick(2)
                    air = False
                    for f in range(105):
                        x, _ = self.pos()
                        vx = self.read("velocity_x", 2, True) / 16
                        delta = target - x
                        buttons = ["a"] if f < hold else []
                        if abs(delta) > vx * vx * 1.25 + 1 or delta * vx < 0:
                            buttons.append("right" if delta > 0 else "left")
                        if f == dash_at:
                            buttons.append("b")
                        self.tick(1, buttons)
                        air |= not self.read("grounded")
                        if self.read("deaths", 2) != death or self.read("game_mode") != 1:
                            break
                        x, y = self.pos()
                        p = self.platform(index)
                        taken = collect is None or self.p.memory[SYMS["_pickup_taken"][1] + collect]
                        intended = x + 12 > p["x"] and x + 3 < p["x"] + p["w"] and abs(y + 16 - p["y"]) < 2 and (self.read("grounded") or p["kind"] == 2 and self.read("velocity_y", 2, True) < 0)
                        alternate = allow_any_catch and collect is not None and self.read("grounded")
                        if air and f > 5 and taken and (intended or alternate):
                            return
        self.rollback(base)
        self.shot("failed-jump")
        raise AssertionError(("critic jump search failed", index, collect, self.state(), p))

    def close(self):
        self.ram.seek(0)
        self.p.stop(ram_file=self.ram)
        return self.ram.getvalue()[:8192]


def compact(trace):
    out = []
    for n, buttons in trace:
        if out and out[-1][1] == buttons:
            out[-1][0] += n
        else:
            out.append([n, buttons])
    return out


def opening():
    report = {"rom_sha256": sha, "evidence": "Blank SRAM, read-only observers, actual joypad input; snapshots repeat probes/search jumps. No gameplay RAM writes.", "checks": {}}
    c = report["checks"]
    t = Game()
    t.start()
    base = t.checkpoint()
    for name, buttons, n in (("idle", [], 120), ("run", ["right"], 75)):
        t.rollback(base)
        f = t.read("stage_frames", 2)
        t.tick(n, buttons)
        c[name + "_cadence"] = {"video_frames": n, "game_ticks": t.read("stage_frames", 2) - f}
    for label, hold in (("tap_jump", 1), ("held_jump", 30)):
        t.rollback(base)
        ys = []
        for f in range(65):
            t.tick(1, ["a"] if f < hold else [])
            ys.append(t.pos()[1])
        c[label] = {"height_px": 112 - min(ys), "end": t.state()}
    t.rollback(base)
    t.tick(4, ["left", "b"])
    c["left_dash"] = t.state()
    assert c["left_dash"]["vx"] < 0
    t.tick(15)
    t.tick(4, ["left"])
    t.tick(4, ["right", "b"])
    c["right_dash"] = t.state()
    assert c["right_dash"]["vx"] > 0
    t.rollback(base)
    # First earned roof seal provides a real one-way ledge for drop-through.
    branch = t.route()["seal_routes"][0]
    for i in branch["platform_indices"]:
        t.jump(i, branch["seal_pickup_index"] if i == branch["seal_platform_index"] else None)
    c["first_earned_seal"] = t.state()
    seal = t.checkpoint()
    before = t.pos()[1]
    t.tick(1, ["down", "a"])
    t.tick(20)
    c["drop_through"] = t.state()
    assert t.pos()[1] > before + 8 and t.read("deaths", 2) == 0
    t.shot("drop-through-catch")
    t.rollback(seal)
    t.jump(branch["rejoin_main_platform"])
    # Complete the remaining opening roof routes through actual controller play.
    r = t.route()
    branches = {b["entry_main_platform"]: b for b in r["seal_routes"][1:]}
    skip = branch["rejoin_main_platform"]
    checkpoint_probe = None
    for i in r["main_route"]:
        if i < skip:
            continue
        if t.current_platform() != i:
            t.jump(i)
        if i in branches:
            b = branches[i]
            for bi in b["platform_indices"]:
                t.jump(bi, b["seal_pickup_index"] if bi == b["seal_platform_index"] else None)
            t.jump(b["rejoin_main_platform"])
            skip = b["rejoin_main_platform"]
        if i == 4:
            t.walk(845)
            checkpoint_probe = t.checkpoint()
    assert t.read("seal_count") == 3 and t.read("run_seal_bits", 2) == 7
    before_transition = t.state()
    for _ in range(240):
        if t.read("room_id") == 1:
            break
        t.tick(1, ["right"])
    assert t.read("room_id") == 1
    # Room id changes before asset upload and the transactional save complete.
    # Wait for ordinary play after the transition, rather than power cutting
    # inside its banked load/save operations.
    t.tick(30)
    c["room0_to_room1"] = {"before": before_transition, "after": t.state()}
    assert t.read("seal_count") == 3 and t.read("run_seal_bits", 2) == 7
    assert t.read("stage_frames", 2) >= before_transition["stage_frames"]
    # Durable room-start save must restore the new room and retained discoveries.
    trace = compact(t.trace)
    earned = t.close()
    (OUT / "earned-room1.sav").write_bytes(earned)
    reboot = Game(earned)
    reboot.tick(180)
    c["room1_reboot_title"] = reboot.state()
    assert reboot.read("room_id") == 1 and reboot.read("seal_count") == 3
    reboot.tap("start", 90)
    c["room1_continue"] = reboot.state()
    assert reboot.read("game_mode") == 1 and reboot.read("room_id") == 1 and reboot.read("run_seal_bits", 2) == 7
    reboot.close()
    linear = Game()
    for n, buttons in trace:
        linear.tick(n, buttons)
    assert linear.read("room_id") == 1 and linear.read("seal_count") == 3 and linear.read("deaths", 2) == 0
    c["fresh_linear_opening"] = linear.state()
    linear.close()
    # Repeat checkpoint probes from an actually earned in-game snapshot.
    t = Game()
    t.rollback(checkpoint_probe)
    before = t.state()
    t.tap("start")
    paused = t.state()
    t.tick(180)
    assert t.read("stage_frames", 2) == paused["stage_frames"] and t.pos() == (paused["x"], paused["y"])
    t.tap("down")
    t.tap("a")
    assert t.read("game_mode") == 4
    t.tick(100)
    t.tap("b")
    c["pause_atlas_back"] = {"before": before, "after": t.state()}
    assert t.read("game_mode") == 1 and t.read("checkpoint_on") and t.read("seal_count") == before["seal_count"]
    t.rollback(checkpoint_probe)
    death = t.read("deaths", 2)
    for _ in range(170):
        t.tick(1, ["left"])
        if t.read("deaths", 2) > death:
            break
    t.tick(15)
    c["genuine_pit_checkpoint_recovery"] = t.state()
    assert t.read("deaths", 2) == death + 1 and t.read("checkpoint_on") and t.read("seal_count") == before["seal_count"]
    t.rollback(checkpoint_probe)
    t.tap("select", 90)
    c["select_checkpoint_recovery"] = t.state()
    assert t.read("deaths", 2) == death + 1 and t.read("seal_count") == before["seal_count"]
    t.rollback(checkpoint_probe)
    t.tap("start")
    t.tap("down")
    t.tap("down")
    t.tap("a")
    assert not t.read("sound_on") and not t.p.memory[0xFF26] & 0x80
    t.tap("b")
    t.tick(4, ["a"])
    t.tick(4, ["b"])
    assert not t.p.memory[0xFF26] & 0x80
    t.tap("start")
    t.tap("down")
    t.tap("down")
    t.tap("down")
    t.tap("a", 90)
    assert t.read("game_mode") == 0
    muted_data = t.close()
    muted = Game(muted_data)
    muted.tick(180)
    assert not muted.read("sound_on") and not muted.p.memory[0xFF26] & 0x80
    c["mute_SFX_title_save_reboot"] = True
    muted.close()
    (OUT / "opening-inputs.json").write_text(json.dumps({"rom_sha256": sha, "inputs": trace}, separators=(",", ":")) + "\n")
    (OUT / "opening-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"rom_sha256": sha, "checks": list(c), "output": str(OUT)}, indent=2))


def three_rooms():
    prefix = json.loads((OUT / "opening-inputs.json").read_text())
    assert prefix["rom_sha256"] == sha
    t = Game()
    for n, buttons in prefix["inputs"]:
        t.tick(n, buttons)
    assert t.read("room_id") == 1 and t.read("seal_count") == 3
    report = {"rom_sha256": sha, "evidence": "Blank-save opening followed by controller-searched exploration, then fresh linear replay; no running RAM writes.", "rooms": []}
    for room in (1, 2):
        r = t.route()
        branches = {b["entry_main_platform"]: b for b in r["seal_routes"]}
        skip = -1
        for index in r["main_route"]:
            if index < skip:
                continue
            if t.current_platform() != index:
                t.jump(index)
            if index in branches:
                b = branches[index]
                for bi in b["platform_indices"]:
                    t.jump(bi, b["seal_pickup_index"] if bi == b["seal_platform_index"] else None, allow_any_catch=True)
                t.jump(b["rejoin_main_platform"])
                skip = b["rejoin_main_platform"]
        assert t.read("seal_count") == (room + 1) * 3
        assert t.read("run_seal_bits", 2) == (1 << ((room + 1) * 3)) - 1
        before = t.state()
        for _ in range(240):
            if t.read("room_id") != room or t.read("game_mode") == 3:
                break
            t.tick(1, ["right"])
        t.tick(30)
        report["rooms"].append({"room": room, "before_exit": before, "after_exit": t.state()})
    assert t.read("game_mode") == 3 and t.read("seal_count") == 9
    report["first_full_stage_clear"] = t.state()
    report["current_rank"] = t.read("current_rank")
    report["clear_lines"] = [t.line(i) for i in range(13)]
    t.shot("first-nine-seal-clear")
    trace = compact(t.trace)
    earned = t.close()
    (OUT / "earned-stage0-nine-seals.sav").write_bytes(earned)
    reboot = Game(earned)
    reboot.tick(180)
    report["clear_reboot_title"] = reboot.state()
    reboot.tap("start", 90)
    report["clear_reboot_continue"] = reboot.state()
    if "_stage_clear_pending" in SYMS:
        assert reboot.read("stage_id") == 1 and reboot.read("room_id") == 0
        assert reboot.read("seal_count") == 0 and reboot.read("run_seal_bits", 2) == 0
        report["continue_after_clear_advances_to_next_stage"] = True
    else:
        report["continue_after_clear_advances_to_next_stage"] = False
    reboot.close()
    linear = Game()
    for n, buttons in trace:
        linear.tick(n, buttons)
    report["fresh_linear_full_stage"] = linear.state()
    assert linear.read("game_mode") == 3 and linear.read("seal_count") == 9 and not linear.read("deaths", 2)
    linear.close()
    (OUT / "three-room-inputs.json").write_text(json.dumps({"rom_sha256": sha, "inputs": trace}, separators=(",", ":")) + "\n")
    (OUT / "three-room-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"rom_sha256": sha, "all_three_rooms": True, "nine_seals": True, "fresh_linear": True, "continue_after_clear": report["clear_reboot_continue"]}, indent=2))


def menu_checks():
    """Use earned progress for destructive reset and replay-menu probes."""
    data = (OUT / "earned-stage0-nine-seals.sav").read_bytes()
    t = Game(data)
    t.tick(180)
    before = t.read("unlocked")
    assert before >= 1
    t.tap("b")
    assert t.line(3).strip() == "B AGAIN: NEW GAME"
    t.tap("down")
    assert "A / START TO PLAY" in t.line(3)
    t.tap("b")
    assert t.read("game_mode") == 0 and t.read("unlocked") == before
    t.tap("up")
    assert "A / START TO PLAY" in t.line(3)
    t.tap("down")
    t.tap("down")
    t.tap("a")
    assert t.read("game_mode") == 7
    help_lines = [t.line(i) for i in range(14)]
    assert any("DOWN+A DROP LEDGES" in line for line in help_lines)
    t.tap("b", 90)
    assert t.read("game_mode") == 0
    t.tap("b")
    assert t.read("game_mode") == 0 and t.read("unlocked") == before
    t.tap("b", 90)
    assert t.read("game_mode") == 5 and t.read("stage_id") == 0 and t.read("unlocked") == 0
    assert not t.read("completed") and not t.read("run_seal_bits", 2)
    reset = t.close()
    reboot = Game(reset)
    reboot.tick(180)
    assert reboot.read("unlocked") == 0 and reboot.read("stage_id") == 0
    reboot.close()
    result = {"rom_sha256": sha, "evidence": "Joypad-only menu probes using a controller-earned first-stage save; reset is isolated in emulator SRAM.",
              "reset_navigation_cancellation": True, "first_B_only_arms_reset": True,
              "two_B_confirms_reset_and_reboot": True, "help_drop_instruction_and_back": True,
              "help_lines": help_lines}
    (OUT / "menu-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def phase_state(t):
    """Only exported game state is sampled; no guessed private addresses."""
    result = {n: t.raw(n, width) for n, width in
              (("stage_frames", 2), ("journey_frames", 4), ("player_x", 2),
               ("player_y", 2), ("boss_x", 2), ("boss_hp", 1), ("boss_guard", 1))}
    for name, count in (("platforms", 240), ("enemy_alive", 12), ("crumble", 48), ("pickup_taken", 64)):
        at = SYMS["_" + name][1]
        result[name] = hashlib.sha256(bytes(t.p.memory[at:at + count])).hexdigest()
    return result


def completed_replay_checks():
    trace_path = Path(sys.argv[sys.argv.index("--trace") + 1]) if "--trace" in sys.argv else ROOT / "dist/verified-inputs.json"
    record = json.loads(trace_path.read_text())
    assert record["rom_sha256"] == sha, "Completed SRAM must come from the matching verified campaign"
    if "--save" in sys.argv:
        save_path = Path(sys.argv[sys.argv.index("--save") + 1])
        seed = save_path.read_bytes()
    else:
        # Public proof contains controller inputs, not cartridge save bytes.
        # Recreate the earned state by actually replaying the matching ROM
        # from blank SRAM, then power cycle through a separate emulator.
        campaign = Game()
        for n, buttons in record["inputs"]:
            campaign.tick(n, buttons)
        masks_at = SYMS["_seal_bits"][1]
        masks = [campaign.p.memory[masks_at + i * 2] | campaign.p.memory[masks_at + i * 2 + 1] << 8 for i in range(24)]
        assert campaign.read("game_mode") == 6 and campaign.read("completed") and campaign.read("stage_clear_pending")
        assert all(m == 0x1FF for m in masks) and not campaign.read("deaths", 2)
        seed = campaign.close()
        save_path = OUT / "final-campaign-earned.sav"
        save_path.write_bytes(seed)
    t = Game(seed)
    t.tick(180)
    assert t.read("completed") and t.read("stage_id") == 23 and t.read("stage_clear_pending")
    t.tap("start", 90)
    assert t.read("game_mode") == 6
    t.shot("earned-completion-continue-ending")
    t.tap("a")
    assert t.read("game_mode") == 4
    pages = [t.read("map_selection") // 6 + 1]
    for _ in range(3):
        t.tap("left")
        pages.append(t.read("map_selection") // 6 + 1)
    assert pages == [4, 3, 2, 1]
    for _ in range(t.read("map_selection")):
        t.tap("up")
    assert t.read("map_selection") == 0
    best_rank = t.p.memory[SYMS["_medal"][1]]
    permanent = t.p.memory[SYMS["_seal_bits"][1]] | t.p.memory[SYMS["_seal_bits"][1] + 1] << 8
    assert best_rank == 3 and permanent == 0x1FF
    t.tap("a", 90)
    assert t.read("game_mode") == 5 and t.read("stage_id") == 0
    t.tap("a", 90)
    assert t.read("game_mode") == 1 and t.read("completed") and not t.read("stage_clear_pending")
    assert t.read("seal_count") == 0 and t.read("run_seal_bits", 2) == 0
    # Save an active replay after a completed campaign. Continue must resume
    # that room rather than treating completed=1 as another ending request.
    t.tap("start")
    for _ in range(3):
        t.tap("down")
    t.tap("a", 90)
    assert t.read("game_mode") == 0
    preparation = compact(t.trace)
    data = t.close()
    (OUT / "earned-active-replay.sav").write_bytes(data)
    (OUT / "replay-preparation-inputs.json").write_text(json.dumps({"rom_sha256": sha,
        "initial_SRAM": "final-campaign-earned.sav", "initial_SRAM_provenance": "Matched fresh-linear completed campaign",
        "inputs": preparation}, separators=(",", ":")) + "\n")
    t = Game(data)
    t.tick(180)
    t.tap("start", 90)
    assert t.read("game_mode") == 1 and t.read("stage_id") == 0 and t.read("room_id") == 0
    assert t.read("completed") and not t.read("stage_clear_pending")
    before_rank = t.p.memory[SYMS["_medal"][1]]
    for room in range(3):
        assert t.read("room_id") == room
        for index in t.route()["main_route"]:
            if t.current_platform() != index:
                t.jump(index)
        for _ in range(240):
            if t.read("room_id") != room or t.read("game_mode") == 3:
                break
            t.tick(1, ["right"])
        t.tick(30)
    assert t.read("game_mode") == 3 and t.read("seal_count") < 9
    assert t.read("current_rank") == 1 and t.p.memory[SYMS["_medal"][1]] == before_rank == 3
    t.shot("earned-B-replay-retains-best-S")
    t.tap("b")
    assert t.read("game_mode") == 4
    t.tap("b")
    assert t.read("game_mode") == 3 and t.read("current_rank") == 1
    result = {"rom_sha256": sha, "earned_save": str(save_path), "campaign_input_trace": str(trace_path),
              "completion_SRAM_regenerated_from_blank_linear_trace": "--save" not in sys.argv,
              "evidence": "Matched final controller-earned campaign SRAM; all replay/menu actions use joypad; snapshots only search ordinary main-route jumps.",
              "final_clear_continue_ending": True, "earned_atlas_pages": pages,
              "completed_active_replay_continue_resumes_room": True,
              "current_B_preserves_best_S": True, "clear_atlas_back_preserves_current_B": True,
              "replay_clear": t.state()}
    accepted = compact(t.trace)
    linear = Game(data)
    for n, buttons in accepted:
        linear.tick(n, buttons)
    assert linear.read("game_mode") == 3 and linear.read("current_rank") == 1
    assert linear.p.memory[SYMS["_medal"][1]] == 3 and not linear.read("deaths", 2)
    result["fresh_linear_earned_SRAM_B_replay"] = True
    linear.close()
    (OUT / "completed-replay-inputs.json").write_text(json.dumps({"rom_sha256": sha,
        "initial_SRAM": "earned-active-replay.sav", "initial_SRAM_provenance": "Actual completed campaign followed by controller Atlas replay/save-to-title",
        "inputs": accepted}, separators=(",", ":")) + "\n")
    t.close()
    (OUT / "completed-replay-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def rank_checks():
    record = json.loads((OUT / "three-room-inputs.json").read_text())
    assert record["rom_sha256"] == sha
    par = ROUTES[0]["par_seconds"]
    report = {"rom_sha256": sha, "par_seconds": par,
              "evidence": "Two fresh blank-SRAM linear controller traces earn all nine seals; the slower run waits safely at spawn in actual PLAY. No game-memory writes or snapshots.", "checks": {}}
    # Complete native hazard periods keep the ordinary accepted route useful
    # after the real idle wait; the clock still exceeds the displayed par.
    over_par_idle = ((par * 60 + 767) // 768) * 768
    for label, idle in (("fast_all_nine_S", 0), ("over_par_all_nine_A", over_par_idle)):
        t = Game()
        inserted = False
        for n, buttons in record["inputs"]:
            t.tick(n, buttons)
            if not inserted and t.read("game_mode") == 1 and t.read("stage_frames", 2) > 30:
                if idle:
                    assert t.pos()[0] < 30 and t.read("grounded")
                    t.tick(idle)
                inserted = True
        rank = 3 if not idle else 2
        assert inserted and t.read("game_mode") == 3 and t.read("seal_count") == 9
        assert t.read("run_seal_bits", 2) == 0x1FF and t.read("current_rank") == rank
        assert t.p.memory[SYMS["_medal"][1]] == rank and not t.read("deaths", 2)
        report["checks"][label] = {"rank": rank, "clear_ticks": t.read("stage_frames", 2), "state": t.state()}
        (OUT / (label + "-inputs.json")).write_text(json.dumps({"rom_sha256": sha, "inputs": compact(t.trace)}, separators=(",", ":")) + "\n")
        t.shot(label)
        t.close()
    (OUT / "rank-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def network_probes():
    """Earn the new roof junction entries through a complete recorded path."""
    trace_path = Path(sys.argv[sys.argv.index("--trace") + 1]) if "--trace" in sys.argv else ROOT / "dist/verified-inputs.json"
    record = json.loads(trace_path.read_text())
    assert record["rom_sha256"] == sha
    plans = {(18, 1): {"entry": 3, "path": [24, 15, 16, 17, 18, 19], "seal": 32, "bridge": [24]},
             (21, 1): {"entry": 15, "path": [14, 24, 25, 16, 17, 18, 19], "seal": 34, "bridge": [24, 25]},
             (23, 1): {"entry": 19, "path": [24, 20, 21, 22, 23], "seal": 37, "bridge": [24]}}
    t = Game()
    snapshots = {}
    for n, buttons in record["inputs"]:
        for _ in range(n):
            t.tick(1, buttons)
            identity = (t.raw("stage_id"), t.raw("room_id"))
            if identity not in plans or identity in snapshots or t.read("game_mode") != 1:
                continue
            if (t.observed.get("observed_stage_id"), t.observed.get("observed_room_id")) != identity:
                continue
            plan = plans[identity]
            required = 31 if identity == (23, 1) else 15
            if t.current_platform() == plan["entry"] and t.read("grounded") and t.read("run_seal_bits", 2) & required == required:
                snapshots[identity] = (t.checkpoint(), compact(t.trace))
                print("Earned roof-network entry: " + str(identity), flush=True)
    t.close()
    assert len(snapshots) == len(plans), ("missing recorded junction entry", list(snapshots))
    checks = {}
    for identity, (snapshot, prefix) in snapshots.items():
        probe = Game()
        probe.rollback(snapshot)
        probe.trace = [list(item) for item in prefix]
        plan = plans[identity]
        for index in plan["path"]:
            probe.jump(index, plan["seal"] if index == plan["path"][-1] else None)
            if index in plan["bridge"]:
                probe.shot("network-%d-%d-bridge%d" % (*identity, index))
        assert probe.p.memory[SYMS["_pickup_taken"][1] + plan["seal"]]
        accepted = compact(probe.trace)
        end = probe.state()
        probe.close()
        linear = Game()
        for n, buttons in accepted:
            linear.tick(n, buttons)
        assert linear.read("run_seal_bits", 2) == end["run_seal_bits"]
        assert linear.read("deaths", 2) == end["deaths"] == 0
        assert (linear.read("stage_id"), linear.read("room_id")) == identity
        linear.close()
        key = "%d:%d" % identity
        checks[key] = {"actual_bridge_contacts": plan["bridge"], "continued_scenic_fork": True,
                       "target_seal_earned": True, "fresh_blank_linear_replay": True, "end": end}
        (OUT / ("network-%d-%d-inputs.json" % identity)).write_text(json.dumps({"rom_sha256": sha, "inputs": accepted}, separators=(",", ":")) + "\n")
    result = {"rom_sha256": sha, "trace": str(trace_path),
              "evidence": "Recorded controller path earns every entry; native snapshot jump search discards failed branches; accepted bridge route replays from blank SRAM; no game-memory writes.",
              "checks": checks}
    (OUT / "network-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def campaign_probes():
    """Capture probes only after reaching their states with a linear input trace."""
    trace_path = Path(sys.argv[sys.argv.index("--trace") + 1]) if "--trace" in sys.argv else ROOT / "dist/verified-inputs.json"
    record = json.loads(trace_path.read_text())
    assert record["rom_sha256"] == sha
    t = Game()
    snapshots = {}
    tells = {}
    for n, buttons in record["inputs"]:
        # Observe each display refresh here: compressed input chunks can span
        # a brief mover landing, which must not be mistaken for no contact.
        for _ in range(n):
            t.tick(1, buttons)
            if t.read("game_mode") != 1:
                continue
            if (t.observed.get("observed_stage_id"), t.observed.get("observed_room_id")) != (t.raw("stage_id"), t.raw("room_id")):
                # Room ids update before banked art/save work and before the
                # next post-physics observation. Never capture stale positions
                # from the previous room against the new room's metadata.
                continue
            r = t.route()
            index = t.current_platform()
            key = None
            if index is not None and r["platforms"][index]["kind"] == 4 and t.read("grounded"):
                key = "moving_ledge"
            elif r["mechanic"] and t.read("stage_id") >= 12 and t.pos()[0] > 700 and t.read("grounded"):
                key = "later_wind_room"
            elif r["boss"] and t.pos()[0] > r["arena"]["start_x"] and t.read("boss_hp"):
                key = "boss_%d_phase_%d" % (r["boss"], 2 if t.read("boss_hp") <= 3 else 1)
            if key is not None and key not in snapshots:
                snapshots[key] = t.checkpoint()
                t.shot("probe-" + key)
                print("Controller-earned probe: " + key, flush=True)
            if r["boss"] and t.read("boss_hp"):
                sprites = [(t.p.memory[a], t.p.memory[a + 1], t.p.memory[a + 2], t.p.memory[a + 3] & 7)
                           for a in range(0xFE00, 0xFEA0, 4)]
                visible_boss = [s for s in sprites if 64 <= s[2] < 80 and 0 < s[0] < 160 and 0 < s[1] < 168]
                if visible_boss and any(s[3] == 3 for s in visible_boss):
                    name = "boss_%d_warm_tell" % r["boss"]
                    if name not in tells:
                        tells[name] = {"first_stage_frame": t.read("stage_frames", 2), "visible_video_samples": 0}
                        t.shot(name)
                    tells[name]["visible_video_samples"] += 1
    terminal = t.state()
    t.close()
    checks = {}
    for key, snapshot in snapshots.items():
        probe = Game()
        probe.rollback(snapshot)
        identity = (probe.read("stage_id"), probe.read("room_id"))
        # A display boundary can fall inside save-on-seal work. Hold Start
        # through that bounded transaction so its edge reaches the next
        # actual joypad poll rather than releasing it while code is busy.
        probe.tick(8, ["start"])
        probe.tick(12)
        assert probe.read("game_mode") == 2, (key, probe.state())
        paused = phase_state(probe)
        phase_mark = len(probe.timings)
        probe.tick(240)
        assert phase_state(probe) == paused, ("pause advances hazard phase", key)
        probe.tap("down")
        probe.tap("a")
        assert probe.read("game_mode") == 4
        atlas = phase_state(probe)
        probe.tick(120)
        assert phase_state(probe) == atlas, ("atlas advances hazard phase", key)
        assert not any(e[0] in ("physics", "world_tick") for e in probe.timings[phase_mark:])
        probe.tap("b", 1)
        assert probe.read("game_mode") == 1
        assert (probe.read("stage_id"), probe.read("room_id")) == identity
        checks[key] = {"pause_240_and_atlas_120_freeze": True,
                       "physics_or_world_calls_during_pause_and_atlas": 0,
                       "resume_play": True, "resume_state": probe.state()}
        probe.close()
    fatal_hit = {"reproduced": False}
    # Real projectiles offer a reproducible harmful contact without synthetic
    # health writes. Repeat an earned second-phase arena and stop on death.
    for key in ("boss_2_phase_2", "boss_4_phase_2", "boss_1_phase_2"):
        if key not in snapshots or fatal_hit["reproduced"]:
            continue
        probe = Game()
        probe.rollback(snapshots[key])
        death = probe.read("deaths", 2)
        seals = probe.read("run_seal_bits", 2)
        damage = []
        last_health = probe.read("health")
        for _ in range(800):
            before = probe.state()
            probe.tick(1)
            if probe.read("health") != last_health:
                damage.append({"before": before, "after": probe.state()})
                last_health = probe.read("health")
            if probe.read("deaths", 2) > death:
                # A health decrement followed by a checkpoint refill with
                # feet on the arena floor distinguishes this from a pit.
                if before["health"] == 1 and before["grounded"] and before["y"] <= 112:
                    probe.tick(12)
                    assert probe.read("game_mode") == 1 and probe.read("health") == 3
                    assert probe.read("boss_hp") == 6 and probe.read("run_seal_bits", 2) == seals
                    checkpoint = probe.route()["checkpoint_x"] if probe.read("checkpoint_on") else probe.route()["spawn_x"]
                    assert abs(probe.pos()[0] - checkpoint) < 2
                    fatal_hit = {"reproduced": True, "arena": key, "damage_events": damage,
                                 "checkpoint_and_seal_recovery": True, "end": probe.state(),
                                 "goal_overlap_stale_coordinate_edge_reproduced": False}
                break
        probe.close()
    result = {"rom_sha256": sha, "trace": str(trace_path),
              "evidence": "Fresh blank-SRAM linear controller path earns every snapshot. Independent pause/Atlas probes branch those native snapshots; no game-memory writes.",
              "checks": checks, "linear_terminal": terminal,
              "warm_tell_visible_OAM_samples": tells,
              "actual_fatal_harmful_contact": fatal_hit,
              "private_projectile_timers_observed": False}
    (OUT / "campaign-probes-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def profile():
    trace_path = Path(sys.argv[sys.argv.index("--trace") + 1]) if "--trace" in sys.argv else ROOT / "dist/verified-inputs.json"
    record = json.loads(trace_path.read_text())
    assert record["rom_sha256"] == sha, "Trace and copied ROM hashes must match"
    t = Game()
    clears = []
    t.p.hook_register(*SYMS["_ui_clear"], lambda _: clears.append({"stage": t.raw("stage_id"), "room": t.raw("room_id"), "seals": t.raw("seal_count"), "rank": t.raw("current_rank"), "ticks": t.raw("stage_frames", 2), "deaths": t.raw("deaths", 2)}), None)
    for n, buttons in record["inputs"]:
        t.tick(n, buttons)
    rooms = {}
    phases = ("audio_tick -> game_tick", "game_tick -> physics", "physics -> world_tick", "world_tick -> camera_update", "camera_update -> draw_objects", "draw_objects -> hud_update")
    for e in t.timings:
        if e[0] == "physics" and e[5] == 1:
            key = f"{e[3]}:{e[4]}"
            rooms.setdefault(key, {"physics_frames": [], "pairs": {}})["physics_frames"].append(e[2])
    for a, b in zip(t.timings, t.timings[1:]):
        key = f"{a[3]}:{a[4]}"
        phase = a[0] + " -> " + b[0]
        if key in rooms and a[3:6] == b[3:6] and a[5] == 1 and phase in phases:
            rooms[key]["pairs"].setdefault(phase, []).append(b[1] - a[1])
    result = {}
    for key, data in rooms.items():
        frames = data["physics_frames"]
        n = frames[-1] - frames[0] + 1
        result[key] = {"physics_ticks": len(frames), "video_frames_first_to_last_physics": n,
                       "cadence_percent": round(len(frames) * 100 / n, 2),
                       "phase_costs": {phase: {"calls": len(values), "mean_cycles": round(statistics.mean(values)),
                                                "mean_double_speed_frame_share": round(statistics.mean(values) / 140448, 3),
                                                "max_double_speed_frame_share": round(max(values) / 140448, 3)}
                                       for phase, values in data["pairs"].items()}}
    arenas = {}
    arena_started = set()
    for event in t.events:
        route = ROUTES[event["stage_id"]]["rooms"][event["room_id"]]
        if route["boss"] and event["game_mode"] == 1 and event["boss_hp"]:
            key = str(route["boss"])
            if event["x"] >= route["arena"]["start_x"]:
                arena_started.add(key)
            # Include retreats after first arena entry, so movement out of
            # the annotated apron does not masquerade as dropped frames.
            if key in arena_started:
                arenas.setdefault(key, []).append(event)
    arena_result = {}
    for key, events in arenas.items():
        video = events[-1]["ppu_frame"] - events[0]["ppu_frame"] + 1
        arena_result[key] = {"post_physics_draw_ticks": len(events), "video_frames": video,
                             "cadence_percent": round(len(events) * 100 / video, 2),
                             "dash_ticks": sum(bool(e["dash_timer"]) for e in events),
                             "phase2_ticks": sum(e["boss_hp"] <= 3 for e in events)}
    report = {"rom_sha256": sha, "trace": str(trace_path), "evidence": "Fresh blank SRAM, linear joypad trace, read-only symbol/CPU-cycle hooks; room loading and menus excluded from first-to-last-physics cadence.",
              "video_frames": t.frames, "clears": clears, "final_state": t.state(), "rooms": result,
              "active_boss_arena_segments": arena_result}
    at = SYMS["_seal_bits"][1]
    masks = [t.p.memory[at + i * 2] | t.p.memory[at + i * 2 + 1] << 8 for i in range(24)]
    full = len(clears) == 24 and len(result) == 72 and t.read("game_mode") == 6 and t.read("completed") and all(m == 0x1FF for m in masks)
    if "--require-complete" in sys.argv:
        assert full and not t.read("deaths", 2), ("independent full replay failed", t.state(), masks, len(clears), len(result))
    report["independent_full_campaign_passed"] = bool(full)
    report["permanent_seal_words"] = masks
    t.close()
    report_name = "campaign-profile-report.json" if len(clears) > 1 else "profile-report.json"
    (OUT / report_name).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"rom_sha256": sha, "room_cadence": {k: [v["physics_ticks"], v["video_frames_first_to_last_physics"], v["cadence_percent"]] for k, v in result.items()}, "clears": clears}, indent=2))


def publish_reports():
    """Publish only complete evidence for the actual frozen release ROM."""
    assert hashlib.sha256((ROOT / "dist/moonwake.gbc").read_bytes()).hexdigest() == sha
    dest = ROOT / "dist"
    names = ("opening", "three-room", "menu", "rank", "campaign-profile", "campaign-probes", "completed-replay", "network")
    reports = {}
    for name in names:
        data = json.loads((OUT / (name + "-report.json")).read_text())
        assert data["rom_sha256"] == sha
        reports[name] = data
    assert reports["campaign-profile"]["independent_full_campaign_passed"]
    assert len(reports["campaign-probes"]["checks"]) == 10
    assert len(reports["network"]["checks"]) == 3
    assert reports["completed-replay"]["fresh_linear_earned_SRAM_B_replay"]
    mapping = {"opening-inputs.json": "critic-expansion-opening-inputs.json",
               "final-campaign-inputs.json": "critic-expansion-campaign-inputs.json",
               "three-room-inputs.json": "critic-expansion-three-room-inputs.json",
               "fast_all_nine_S-inputs.json": "critic-expansion-fast-S-inputs.json",
               "over_par_all_nine_A-inputs.json": "critic-expansion-over-par-A-inputs.json",
               "completed-replay-inputs.json": "critic-expansion-B-replay-inputs.json",
               "replay-preparation-inputs.json": "critic-expansion-replay-preparation-inputs.json",
               "network-18-1-inputs.json": "critic-expansion-network-18-1-inputs.json",
               "network-21-1-inputs.json": "critic-expansion-network-21-1-inputs.json",
               "network-23-1-inputs.json": "critic-expansion-network-23-1-inputs.json"}
    for source, target in mapping.items():
        data = json.loads((OUT / source).read_text())
        assert data["rom_sha256"] == sha
        if "initial_SRAM" in data:
            seed = data.pop("initial_SRAM")
            traces = ["dist/critic-expansion-campaign-inputs.json"]
            if seed == "earned-active-replay.sav":
                traces.append("dist/critic-expansion-replay-preparation-inputs.json")
            else:
                assert seed == "final-campaign-earned.sav"
            data["initial_SRAM_generation"] = {
                "start": "Blank 8192-byte SRAM",
                "controller_traces_before_this_boot": traces,
                "power_cycle_after_each_trace": True,
                "expected_SRAM_sha256": hashlib.sha256((OUT / seed).read_bytes()).hexdigest(),
                "save_bytes_omitted": True}
        (dest / target).write_text(json.dumps(data, separators=(",", ":")) + "\n")
    for name in ("stage0-earned", "campaign-earned", "active-replay"):
        # Only our obsolete publication copies are removed. Earned bytes
        # remain in the private hash-specific build evidence directory.
        (dest / ("critic-expansion-" + name + ".sav")).unlink(missing_ok=True)
    for name, data in reports.items():
        if "trace" in data:
            data["trace"] = "dist/critic-expansion-campaign-inputs.json"
        if "earned_save" in data:
            data.pop("earned_save")
            data["earned_save_provenance"] = "Save bytes omitted; regenerate from the published blank-SRAM campaign controller trace, then power cycle."
        if "campaign_input_trace" in data:
            data["campaign_input_trace"] = "dist/critic-expansion-campaign-inputs.json"
        if name == "opening":
            data["accepted_input_trace"] = "dist/critic-expansion-opening-inputs.json"
        if name == "three-room":
            data["accepted_input_trace"] = "dist/critic-expansion-three-room-inputs.json"
        if name == "rank":
            data["accepted_input_traces"] = ["dist/critic-expansion-fast-S-inputs.json", "dist/critic-expansion-over-par-A-inputs.json"]
        if name == "completed-replay":
            data["accepted_input_trace"] = "dist/critic-expansion-B-replay-inputs.json"
        if name == "network":
            data["accepted_input_traces"] = ["dist/critic-expansion-network-%d-1-inputs.json" % i for i in (18, 21, 23)]
        (dest / ("critic-expansion-" + name + "-report.json")).write_text(json.dumps(data, indent=2) + "\n")
    save = json.loads((ROOT / "build/critic-expansion-save/report.json").read_text())
    assert save["source_sha256"] == hashlib.sha256((ROOT / "src/save.c").read_bytes()).hexdigest()
    assert len(save["checks"]) == 20 and not save["defects"]
    save["production_rom_sha256"] = sha
    save["production_source"] = "src/save.c"
    save["reproducer"] = "tools/check_expansion_save.py"
    (dest / "critic-expansion-save-report.json").write_text(json.dumps(save, indent=2) + "\n")
    paths = [p for p in dest.glob("critic-expansion-*") if p.is_file() and p.name != "critic-expansion-provenance.json"]
    manifest = {"rom_sha256": sha, "native_save_source_sha256": save["source_sha256"],
                "runtime_reproducer": "tools/check_expansion_runtime.py", "save_reproducer": "tools/check_expansion_save.py",
                "evidence": "Actual native emulation with joypad inputs and read-only observers. Earned SRAM bytes stay private and are reproducible from campaign/preparation inputs and power cycles; synthetic fixtures are isolated in the save harness.",
                "save_bytes_omitted": True,
                "artifacts": {"dist/" + p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
    (dest / "critic-expansion-provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"rom_sha256": sha, "published_reports": len(reports) + 1, "controller_traces": len(mapping), "provenance": "dist/critic-expansion-provenance.json"}, indent=2))


if __name__ == "__main__":
    if "--publish" in sys.argv:
        publish_reports()
    elif "--profile" in sys.argv:
        profile()
    elif "--campaign-probes" in sys.argv:
        campaign_probes()
    elif "--menu" in sys.argv:
        menu_checks()
    elif "--completed-replay" in sys.argv:
        completed_replay_checks()
    elif "--ranks" in sys.argv:
        rank_checks()
    elif "--networks" in sys.argv:
        network_probes()
    elif "--three-rooms" in sys.argv:
        three_rooms()
    else:
        opening()
