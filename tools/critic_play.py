"""Independent controller-only critic probes; read RAM, never mutate it.

Copies ROM/symbols before testing so concurrent builds cannot alter evidence.
The movement cases use save-state branching only to repeat the same opening.
Campaign progression uses the actual joypad planner, no debug teleport.
"""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import statistics

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "dist/moonwake.gbc").stat().st_size != 262144:
    raise SystemExit("This historical critic targets v1.0.0. Use check_expansion_runtime.py and check_expansion_save.py for The Long Dawn.")
OUT = ROOT / ("build/critic-play-round2" if any(x in sys.argv for x in ("--ui", "--rank", "--lantern", "--arena", "--replay")) else "build/critic-play")
OUT.mkdir(parents=True, exist_ok=True)
for ext in ("gbc", "sym"):
    shutil.copy2(ROOT / f"dist/moonwake.{ext}", OUT / f"moonwake.{ext}")
spec = importlib.util.spec_from_file_location("moonwake_playtest", ROOT / "tools/playtest.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.ROM = OUT / "moonwake.gbc"
mod.SYMS = {s[1]: (int(s[0].split(":")[0], 16), int(s[0].split(":")[1], 16))
            for l in mod.ROM.with_suffix(".sym").read_text().splitlines()
            if len(s := l.split()) == 2 and ":" in s[0]}
mod.ROOT = OUT
(OUT / "build").mkdir(exist_ok=True)


class Critic(mod.Tester):
    def close(self):
        self.ram.seek(0)
        self.p.stop(ram_file=self.ram)
        self.ram.seek(0)

    def shot(self, name):
        d = OUT / "screenshots"
        d.mkdir(exist_ok=True)
        self.p.screen.image.save(d / (name + ".png"))

    def window_line(self, row):
        address = (0x9C00 if self.p.memory[0xFF40] & 0x40 else 0x9800) + row * 32
        return "".join(chr(self.p.memory[address + x]) for x in range(20)).rstrip()

    def settle(self):
        # The shared planner's landing proximity can fire on an ascending pass.
        # Wait for an actual stable floor before making another decision.
        self.tick(15)
        for _ in range(180):
            self.tick(1)
            if self.read("grounded") and abs(self.read("velocity_x", 2, True)) < 2:
                return
        raise AssertionError(("no stable landing", self.state(), self.raw("grounded"), self.raw("player_y", 2, True)))

    def direct_hop(self, index):
        p = mod.ROUTES[self.read("stage_id")]["platforms"][index]
        target = p["x"] + 16
        if target - self.pos()[0] > 160:
            # Approach only enough to put the broad landing within dash reach.
            goal = target - 144
            for _ in range(70):
                x, _ = self.pos()
                if x >= goal - 4:
                    break
                self.tick(1, ["right"])
            self.settle()
        base = self.checkpoint()
        for dash_at in (12, 6, 20, -1):
            self.rollback(base)
            self.tick(4)
            airborne = False
            for f in range(100):
                x, y = self.pos()
                buttons = ["a"] if f < 30 else []
                if x < target - 6:
                    buttons.append("right")
                if f == dash_at:
                    buttons.append("b")
                self.tick(1, buttons)
                airborne |= not self.read("grounded")
                x, y = self.pos()
                if airborne and self.read("grounded") and x + 12 > p["x"] and x + 3 < p["x"] + p["w"] and abs(y + 16 - p["y"]) < 2:
                    self.settle()
                    return
        self.rollback(base)
        raise AssertionError(("direct_hop failed", index, self.state()))


def run():
    report = {"rom_sha256": hashlib.sha256(mod.ROM.read_bytes()).hexdigest(),
              "evidence": "Joypad input only; RAM reads and repeatable opening snapshots.",
              "observations": {}}
    observations = report["observations"]
    t = Critic()
    t.start()
    base = t.checkpoint()
    observations["opening"] = t.state()
    f = t.read("stage_frames", 2)
    t.tick(120)
    observations["idle_cadence"] = {"emulator_frames": 120, "game_ticks": t.read("stage_frames", 2) - f}
    t.rollback(base)
    f = t.read("stage_frames", 2)
    t.tick(75, ["right"])
    observations["running_cadence"] = {"emulator_frames": 75, "game_ticks": t.read("stage_frames", 2) - f}
    t.rollback(base)

    for label, hold in (("tap_jump", 1), ("hold_jump", 30)):
        t.rollback(base)
        trajectory = []
        for f in range(65):
            t.tick(1, ["a"] if f < hold else [])
            trajectory.append(t.pos())
        observations[label] = {"min_top_y": min(y for x, y in trajectory),
                               "end": t.state()}
    t.rollback(base)
    t.tick(4, ["left", "b"])
    observations["left_dash_from_right_facing"] = t.state()
    t.tick(12)
    t.tick(4, ["left"])
    t.tick(4, ["right", "b"])
    observations["right_dash_from_left_facing"] = t.state()
    t.rollback(base)

    # Test pause -> atlas -> B before any game save exists.
    t.tick(30, ["right"])
    t.tap("start")
    observations["pre_atlas"] = t.state()
    t.tap("down")
    t.tap("a")
    t.shot("atlas-before-save")
    observations["atlas_before_save"] = {"state": t.state(),
                                          "lines": [t.window_line(i) for i in range(15)]}
    t.tap("b")
    t.shot("atlas-back-before-save")
    observations["atlas_back_before_save"] = t.state()
    t.rollback(base)

    r = mod.ROUTES[0]
    (OUT / "report-partial.json").write_text(json.dumps(report, indent=2) + "\n")
    branch = r["seal_routes"][0]
    for i in branch["platform_indices"]:
        t.jump(i, collect=branch["seal_pickup_index"] if i == branch["platform_indices"][-1] else None)
    t.shot("first-seal")
    observations["first_seal"] = t.state()
    t.jump(branch["rejoin_main_platform"])
    t.settle()
    for i in r["main_route"][2:5]:
        if t.current_platform() != i:
            t.jump(i)
            t.settle()
    t.walk(845)
    observations["at_checkpoint"] = {**t.state(), "checkpoint_on": t.read("checkpoint_on"), "stars": t.read("stars"), "stage_frames": t.read("stage_frames", 2)}
    t.shot("checkpoint")
    safe = t.checkpoint()
    before_death = t.read("deaths", 2)
    for _ in range(150):
        t.tick(1, ["left"])
        if t.read("deaths", 2) > before_death:
            break
    t.tick(15)
    observations["actual_pit_death_retry"] = {**t.state(), "checkpoint_on": t.read("checkpoint_on"), "stars": t.read("stars")}
    assert t.read("deaths", 2) == before_death + 1 and t.read("checkpoint_on") and t.read("seal_count") == 2
    t.rollback(safe)
    t.tap("select", 120)
    observations["select_checkpoint_retry"] = {**t.state(), "checkpoint_on": t.read("checkpoint_on"), "stars": t.read("stars")}
    assert t.read("deaths", 2) == before_death + 1 and t.read("checkpoint_on") and t.read("seal_count") == 2
    t.rollback(safe)
    t.tap("start")
    t.tap("down")
    t.tap("a")
    t.tap("b", 120)
    t.shot("atlas-back-after-save")
    observations["atlas_back_after_save"] = {**t.state(), "checkpoint_on": t.read("checkpoint_on"), "stars": t.read("stars"), "stage_frames": t.read("stage_frames", 2)}
    (OUT / "report-partial.json").write_text(json.dumps(report, indent=2) + "\n")
    # Finish the first-stage safe route as a direct playability check.
    try:
        for i in r["main_route"][r["main_route"].index(t.current_platform()) + 1:]:
            if t.current_platform() != i:
                t.direct_hop(i)
    except AssertionError as e:
        observations["planner_limitation"] = str(e)
        (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        t.close()
        print(json.dumps(report, indent=2))
        return
    t.walk(r["goal_x"] - 4, 230)
    t.tick(15)
    t.shot("first-clear")
    observations["first_clear"] = {"state": t.state(), "lines": [t.window_line(i) for i in range(13)]}
    assert t.read("game_mode") == 3
    trace = []
    for n, b in t.trace:
        if trace and trace[-1][1] == b:
            trace[-1][0] += n
        else:
            trace.append([n, b])
    (OUT / "inputs.json").write_text(json.dumps({"rom_sha256": report["rom_sha256"], "inputs": trace}, separators=(",", ":")) + "\n")
    t.close()
    earned = t.ram.getvalue()
    (OUT / "earned.sav").write_bytes(earned)
    reboot = Critic(t.ram)
    reboot.tick(180)
    observations["save_reboot"] = {**reboot.state(), "unlocked": reboot.read("unlocked"),
                                   "save_valid": reboot.read("save_valid"),
                                   "seal_bits_0": reboot.p.memory[mod.SYMS["_seal_bits"][1]],
                                   "medal_0": reboot.p.memory[mod.SYMS["_medal"][1]]}
    reboot.shot("continue-title")
    assert reboot.read("save_valid") and reboot.read("unlocked") == 1
    reboot.close()
    # Fault injection changes only copies of legitimately earned cartridge SRAM.
    # It never creates progress or touches running game RAM.
    slots = [(int.from_bytes(earned[a + 3:a + 5], "little"), a) for a in (0x100, 0x180) if earned[a:a + 2] == b"MW"]
    latest = max(slots)[1]
    damaged = bytearray(earned)
    damaged[latest + 5] ^= 1
    fallback = Critic(io.BytesIO(damaged))
    fallback.tick(180)
    observations["damaged_latest_save_fallback"] = {"save_valid": fallback.read("save_valid"), "unlocked": fallback.read("unlocked"), "seal_bits_0": fallback.p.memory[mod.SYMS["_seal_bits"][1]]}
    assert fallback.read("save_valid")
    fallback.close()
    damaged[0x100] = damaged[0x180] = 0
    rejected = Critic(io.BytesIO(damaged))
    rejected.tick(180)
    observations["both_save_signatures_invalid"] = {"save_valid": rejected.read("save_valid"), "unlocked": rejected.read("unlocked")}
    assert not rejected.read("save_valid") and not rejected.read("unlocked")
    rejected.close()
    linear = Critic()
    for n, b in trace:
        linear.tick(n, b)
    observations["fresh_linear_replay"] = linear.state()
    assert linear.read("game_mode") == 3 and linear.read("seal_count") == 2
    linear.close()
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def run_ui():
    report = {"rom_sha256": hashlib.sha256(mod.ROM.read_bytes()).hexdigest(),
              "evidence": "Joypad-only UI tests; legitimate prior earned save copied in emulator; no running RAM writes.",
              "checks": {}}
    checks = report["checks"]
    t = Critic()
    t.tick(180)
    t.tap("down")
    t.tap("down")
    t.tap("a", 30)
    t.shot("help")
    checks["help"] = {"mode": t.read("game_mode"), "lines": [t.window_line(i) for i in range(14)]}
    assert t.read("game_mode") == 7
    t.tap("b", 120)
    assert t.read("game_mode") == 0
    checks["help_back"] = True
    t.close()

    earned = (ROOT / "build/critic-play/earned.sav").read_bytes()
    t = Critic(io.BytesIO(earned))
    t.tick(180)
    assert t.read("unlocked") == 1 and t.read("save_valid")
    t.tap("down")
    t.tap("a", 30)
    assert t.read("game_mode") == 4
    t.tap("down")
    checks["atlas_earned_next_stage"] = {"selection": t.read("map_selection"), "lines": [t.window_line(i) for i in range(15)]}
    assert t.read("map_selection") == 1
    t.tap("b", 120)
    assert t.read("game_mode") == 0
    checks["title_atlas_back"] = True
    t.tap("b")
    checks["reset_first_press"] = {"unlocked": t.read("unlocked"), "seals": t.p.memory[mod.SYMS["_seal_bits"][1]], "prompt": t.window_line(3)}
    assert t.read("unlocked") == 1 and t.p.memory[mod.SYMS["_seal_bits"][1]] == 3
    t.tap("down")
    cancel_prompt = t.window_line(3)
    assert "A / START TO PLAY" in cancel_prompt
    t.tap("b")
    checks["navigation_cancels_reset"] = {"unlocked": t.read("unlocked"), "prompt_immediately_after_navigation": cancel_prompt, "prompt_after_new_first_B": t.window_line(3)}
    assert t.read("unlocked") == 1
    t.tap("b", 120)
    assert t.read("game_mode") == 5 and not t.read("unlocked")
    checks["reset_second_confirm"] = {"mode": t.read("game_mode"), "unlocked": t.read("unlocked"), "seals": t.p.memory[mod.SYMS["_seal_bits"][1]], "medal": t.p.memory[mod.SYMS["_medal"][1]]}
    assert not checks["reset_second_confirm"]["seals"] and not checks["reset_second_confirm"]["medal"]
    t.close()
    reset = Critic(t.ram)
    reset.tick(180)
    assert reset.read("save_valid") and not reset.read("unlocked")
    checks["reset_reboot"] = True
    reset.close()

    t = Critic(io.BytesIO(earned))
    t.tick(180)
    t.tap("down")
    t.tap("a", 30)
    t.tap("down")
    t.tap("a", 120)
    t.tap("a", 90)
    assert t.read("stage_id") == 1 and t.read("game_mode") == 1
    checks["started_next_stage"] = t.read("stage_id")
    t.close()
    continued = Critic(t.ram)
    continued.tick(180)
    checks["continue_after_next_stage_start"] = {"saved_stage": continued.read("stage_id"), "unlocked": continued.read("unlocked"), "latest_played_stage_restored": continued.read("stage_id") == 1}
    continued.close()

    t = Critic(io.BytesIO(earned))
    t.tick(180)
    t.tap("start", 120)
    t.tap("a", 90)
    t.tap("start")
    t.tap("down")
    t.tap("down")
    t.tap("a")
    checks["mute"] = {"sound_on": t.read("sound_on"), "audio_enabled": t.read("audio_enabled"), "apu_power": bool(t.p.memory[0xFF26] & 0x80), "line": t.window_line(6)}
    assert not t.read("sound_on") and not t.read("audio_enabled") and not t.p.memory[0xFF26] & 0x80
    step = t.read("audio_step")
    t.tick(120)
    checks["mute_score_paused"] = t.read("audio_step") == step
    assert checks["mute_score_paused"]
    t.tap("b", 60)
    t.tick(4, ["a"])
    t.tick(8)
    t.tick(4, ["b"])
    t.tick(20)
    assert not t.p.memory[0xFF26] & 0x80
    checks["sfx_stay_muted"] = True
    t.tap("start")
    t.tap("down")
    t.tap("down")
    t.tap("down")
    t.tap("a", 120)
    assert t.read("game_mode") == 0
    t.close()
    muted = Critic(t.ram)
    muted.tick(180)
    checks["mute_reboot"] = {"sound_on": muted.read("sound_on"), "audio_enabled": muted.read("audio_enabled"), "apu_power": bool(muted.p.memory[0xFF26] & 0x80)}
    assert not muted.read("sound_on") and not muted.p.memory[0xFF26] & 0x80
    muted.tap("start", 120)
    muted.tap("a", 90)
    muted.tap("start")
    muted.tap("down")
    muted.tap("down")
    muted.tap("a")
    checks["unmute"] = {"sound_on": muted.read("sound_on"), "audio_enabled": muted.read("audio_enabled"), "apu_power": bool(muted.p.memory[0xFF26] & 0x80), "line": muted.window_line(6)}
    assert muted.read("sound_on") and muted.read("audio_enabled") and muted.p.memory[0xFF26] & 0x80
    muted.close()
    (OUT / "ui-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def run_rank():
    t = Critic()
    t.start()
    r = mod.ROUTES[0]
    branches = {b["entry_main_platform"]: b for b in r["seal_routes"]}
    skip_to = -1
    for idx in r["main_route"]:
        if idx < skip_to:
            continue
        if t.current_platform() != idx:
            t.jump(idx)
            t.settle()
        if idx in branches:
            b = branches[idx]
            for j, bi in enumerate(b["platform_indices"]):
                t.jump(bi, collect=b["seal_pickup_index"] if j == len(b["platform_indices"]) - 1 else None)
            t.jump(b["rejoin_main_platform"])
            t.settle()
            skip_to = b["rejoin_main_platform"]
    t.walk(r["goal_x"] - 4, 230)
    t.tick(20)
    assert t.read("game_mode") == 3 and t.read("seal_count") == 3
    report = {"rom_sha256": hashlib.sha256(mod.ROM.read_bytes()).hexdigest(),
              "earned_allseal_run": t.state(),
              "earned_rank": t.read("current_rank"),
              "best_medal": t.p.memory[mod.SYMS["_medal"][1]],
              "seconds": t.read("stage_frames", 2) / 60}
    t.shot("earned-S-clear")
    assert t.read("current_rank") == 3
    t.close()
    (OUT / "earned-S.sav").write_bytes(t.ram.getvalue())
    replay = Critic(t.ram)
    replay.tick(180)
    replay.tap("start", 120)
    replay.tap("a", 90)
    report["replay_initial_seals"] = replay.read("seal_count")
    assert not replay.read("seal_count")
    for i in r["main_route"][1:]:
        replay.direct_hop(i)
    replay.walk(r["goal_x"] - 4, 230)
    replay.tick(20)
    report["replay_run"] = replay.state()
    report["replay_current_rank"] = replay.read("current_rank")
    report["replay_best_medal"] = replay.p.memory[mod.SYMS["_medal"][1]]
    report["replay_rank_line"] = replay.window_line(8)
    replay.shot("replay-B-best-S")
    assert replay.read("game_mode") == 3 and replay.read("seal_count") < 3
    assert replay.read("current_rank") == 1 and replay.p.memory[mod.SYMS["_medal"][1]] == 3
    replay.close()
    (OUT / "rank-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def run_lantern():
    class TouchCritic(Critic):
        def __init__(self, ram):
            self.touch_events = []
            self.last_combo = 0
            super().__init__(ram)

        def observe(self, _):
            super().observe(_)
            combo = self.read("combo")
            if combo > self.last_combo:
                self.touch_events.append({"frame": self.read("frame"), "combo": combo,
                                          "charge": self.read("dash_charge"),
                                          "x": self.pos()[0], "y": self.pos()[1],
                                          "seals": self.read("seal_count")})
            self.last_combo = combo

        def checkpoint(self):
            return super().checkpoint() + (len(self.touch_events), self.last_combo)

        def rollback(self, state):
            super().rollback(state[:5])
            self.touch_events = self.touch_events[:state[5]]
            self.last_combo = state[6]

    earned = (OUT / "earned-S.sav").read_bytes()
    t = TouchCritic(io.BytesIO(earned))
    t.tick(180)
    t.tap("down")
    t.tap("a", 30)
    t.tap("down")
    t.tap("a", 120)
    t.tap("a", 90)
    assert t.read("stage_id") == 1
    for i in mod.ROUTES[1]["main_route"][1:7]:
        t.jump(i)
        t.settle()
    t.jump(13)
    t.settle()
    t.walk(1167)
    for _ in range(256):
        if t.read("frame") == 240:
            break
        t.tick(1)
    combo_before = t.read("combo")
    t.tick(6, ["right", "b"])
    report = {"rom_sha256": hashlib.sha256(mod.ROM.read_bytes()).hexdigest(),
              "evidence": "Earned stage unlock, ordinary joypad traversal, read-only RAM observations.",
              "first_touch": {"frame": t.read("frame"), "combo_before": combo_before, "combo": t.read("combo"), "state": t.state()}}
    assert t.read("combo") > combo_before and t.read("dash_charge")
    t.tick(20, ["right"])
    t.tick(10, ["right", "b"])
    t.tick(40)
    t.tick(220)
    report["after_leaving_220_frames"] = {"frame": t.read("frame"), "combo": t.read("combo"), "state": t.state()}
    start = len(t.touch_events)
    t.jump(6)
    t.settle()
    t.jump(13)
    t.settle()
    t.walk(1167)
    combo_before = t.read("combo")
    t.tick(6, ["right", "b"])
    report["second_touch_after_return"] = {"frame": t.read("frame"), "combo_before": combo_before, "combo": t.read("combo"), "state": t.state()}
    report["return_contact_events"] = t.touch_events[start:]
    # Walking/jumping back can contact the lantern before the final dash.
    # Identify the actual refill event at its authored location.
    assert any(abs(e["x"] - 1184) < 20 and abs(e["y"] - 48) < 18 and e["charge"]
               for e in report["return_contact_events"])
    t.shot("lantern-return-after-wrap")
    t.close()
    (OUT / "lantern-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def run_arena():
    class Profile(Critic):
        def __init__(self):
            self.events = []
            self.motion = []
            super().__init__()
            for name in ("audio_tick", "game_tick", "physics", "world_tick", "camera_update", "hud_update"):
                self.p.hook_register(*mod.SYMS["_" + name], lambda _, n=name: self.mark(n), None)

        def mark(self, name):
            self.events.append((name, self.p._cycles(), self.p.frame_count))

        def observe(self, _):
            super().observe(_)
            self.mark("draw_objects")
            self.motion.append({"video_frame": self.p.frame_count, "stage_frames": self.read("stage_frames", 2), "x": self.pos()[0], "y": self.pos()[1], "vy": self.read("velocity_y", 2, True) / 16, "health": self.read("health"), "boss_hp": self.read("boss_hp"), "grounded": self.read("grounded"), "dash": self.read("dash_timer")})

    t = Profile()
    state = (ROOT / "build/boss-state.bin").read_bytes()
    metadata = json.loads((ROOT / "build/boss-state.json").read_text())
    report = {"rom_sha256": hashlib.sha256(mod.ROM.read_bytes()).hexdigest(), "evidence": "Profile of controller-earned boss arena snapshot; no RAM writes or teleport.", "cases": {}}
    verified = json.loads((ROOT / "dist/verified-inputs.json").read_text())
    assert verified["rom_sha256"] == report["rom_sha256"]
    elapsed = 0
    finale = []
    for frames, buttons in verified["inputs"]:
        if elapsed + frames > metadata["frames"]:
            finale.append((elapsed + frames - max(elapsed, metadata["frames"]), buttons))
        elapsed += frames
    cases = (("idle", [(120, [])]),
             ("run_right", [(45, ["right"])]),
             ("run_left", [(45, ["left"])]),
             ("ground_dash", [(40, ["right", "b"])]),
             ("ground_dash_left", [(40, ["left", "b"])]),
             ("held_jump", [(90, ["right", "a"])]),
             ("air_dash_then_recoil", [(12, ["right", "a"]), (3, ["right", "a", "b"]), (75, ["a"])]),
             ("air_dash_left_then_recoil", [(12, ["left", "a"]), (3, ["left", "a", "b"]), (75, ["a"])]),
             ("six_hit_earned_trace", finale))
    for name, actions in cases:
        n = sum(n for n, buttons in actions)
        t.p.load_state(io.BytesIO(state))
        t.held = set(metadata["held"])
        t.observed = dict(metadata["observed"])
        t.events = []
        t.motion = []
        before = t.state()
        f = t.read("stage_frames", 2)
        cycles = t.p._cycles()
        if name == "six_hit_earned_trace":
            n = 0
            for frames, buttons in actions:
                for _ in range(frames):
                    t.tick(1, buttons)
                    n += 1
                    if not t.read("boss_hp"):
                        break
                if not t.read("boss_hp"):
                    break
            assert not t.read("boss_hp") and not t.read("deaths", 2)
            t.shot("finale-six-hit-profile")
        else:
            for frames, buttons in actions:
                t.tick(frames, buttons)
        after = t.state()
        pairs = {}
        for a, b in zip(t.events, t.events[1:]):
            key = a[0] + " -> " + b[0]
            if key in ("audio_tick -> game_tick", "game_tick -> physics", "physics -> world_tick", "world_tick -> camera_update", "camera_update -> draw_objects", "draw_objects -> hud_update"):
                pairs.setdefault(key, []).append(b[1] - a[1])
        budget = (t.p._cycles() - cycles) / n
        timings = {key: {"calls": len(v), "mean_cycles": round(statistics.mean(v)), "mean_frame_share": round(statistics.mean(v) / budget, 3), "max_frame_share": round(max(v) / budget, 3)} for key, v in pairs.items()}
        changes = [v for i, v in enumerate(t.motion) if not i or any(v[k] != t.motion[i-1][k] for k in ("health", "boss_hp", "grounded"))]
        report["cases"][name] = {"emulator_frames": n, "game_ticks": t.read("stage_frames", 2) - f, "draw_calls": sum(e[0] == "draw_objects" for e in t.events), "before": before, "after": after, "profile": timings, "state_changes": changes}
    t.close()
    (OUT / "arena-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def run_replay():
    trace = json.loads((ROOT / "dist/verified-inputs.json").read_text())
    sha = hashlib.sha256(mod.ROM.read_bytes()).hexdigest()
    assert trace["rom_sha256"] == sha
    t = Critic()
    clears = []

    def clear(_):
        sid = t.raw("stage_id")
        clears.append({"stage_id": sid, "name": mod.ROUTES[sid]["name"],
                       "seals_this_run": t.raw("seal_count"),
                       "rank": t.raw("current_rank"),
                       "game_ticks": t.raw("stage_frames", 2),
                       "par_seconds": mod.ROUTES[sid]["par_seconds"],
                       "deaths": t.raw("deaths", 2),
                       "health": t.raw("health")})

    t.p.hook_register(*mod.SYMS["_ui_clear"], clear, None)
    for n, b in trace["inputs"]:
        t.tick(n, b)
    seal_addr = mod.SYMS["_seal_bits"][1]
    medal_addr = mod.SYMS["_medal"][1]
    report = {"rom_sha256": sha,
              "evidence": "Fresh blank SRAM; full saved joypad trace replayed linearly without save states, planner decisions, or running RAM writes.",
              "video_frames": t.frames, "clears": clears,
              "ending": t.state(), "completed": t.read("completed"),
              "seal_bits": [t.p.memory[seal_addr + i] for i in range(12)],
              "best_medals": [t.p.memory[medal_addr + i] for i in range(12)]}
    assert [c["stage_id"] for c in clears] == list(range(12))
    assert all(c["seals_this_run"] == 3 for c in clears)
    assert t.read("completed") and t.read("game_mode") == 6
    assert t.read("deaths", 2) == 0
    assert report["seal_bits"] == [7] * 12
    t.shot("final-linear-ending")
    t.close()
    earned = t.ram.getvalue()[:8192]
    (OUT / "final-linear-earned.sav").write_bytes(earned)
    reboot = Critic(io.BytesIO(earned))
    reboot.tick(180)
    report["completion_reboot"] = {"completed": reboot.read("completed"),
                                    "unlocked": reboot.read("unlocked"),
                                    "save_valid": reboot.read("save_valid"),
                                    "seals": [reboot.p.memory[seal_addr + i] for i in range(12)]}
    assert reboot.read("completed") and reboot.read("unlocked") == 11
    assert report["completion_reboot"]["seals"] == [7] * 12
    reboot.shot("final-completed-title")
    reboot.close()
    slots = [(int.from_bytes(earned[a + 3:a + 5], "little"), a)
             for a in (0x100, 0x180) if earned[a:a + 2] == b"MW"]
    assert len(slots) == 2
    latest = max(slots)[1]
    damaged = bytearray(earned)
    damaged[latest + 5] ^= 1
    fallback = Critic(io.BytesIO(damaged))
    fallback.tick(180)
    report["crc_latest_bad_falls_back"] = {"save_valid": fallback.read("save_valid"),
                                           "completed": fallback.read("completed"),
                                           "unlocked": fallback.read("unlocked"),
                                           "seals": [fallback.p.memory[seal_addr + i] for i in range(12)]}
    prior = min(slots)[1]
    assert fallback.read("save_valid") and fallback.read("completed") == earned[prior + 6]
    assert fallback.read("unlocked") == earned[prior + 5]
    assert report["crc_latest_bad_falls_back"]["seals"] == list(earned[prior + 20:prior + 32])
    fallback.close()
    damaged[0x100 + 5] ^= 2
    damaged[0x180 + 5] ^= 2
    invalid = Critic(io.BytesIO(damaged))
    invalid.tick(180)
    report["crc_both_bad_safe_start"] = {"save_valid": invalid.read("save_valid"),
                                          "completed": invalid.read("completed"),
                                          "unlocked": invalid.read("unlocked")}
    assert not invalid.read("save_valid") and not invalid.read("completed") and not invalid.read("unlocked")
    invalid.close()
    (OUT / "replay-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run_replay() if "--replay" in sys.argv else run_arena() if "--arena" in sys.argv else run_lantern() if "--lantern" in sys.argv else run_rank() if "--rank" in sys.argv else run_ui() if "--ui" in sys.argv else run()
