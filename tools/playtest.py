"""Native campaign planner using only controller input and read-only observation.

Planning may branch emulator snapshots to search for a usable jump. The saved
recording is then replayed linearly from fresh cartridge RAM, without snapshots
or gameplay-memory writes, to verify all 24 stages, 72 rooms, and 216 seals.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil

from PIL import Image
from pyboy import PyBoy

ROOT = Path(__file__).resolve().parents[1]
ROUTES = json.loads((ROOT / "docs/routes.json").read_text())["levels"]
ROM = ROOT / "dist/moonwake.gbc"


def read_symbols(path: Path) -> dict:
    symbols = {}
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and ":" in parts[0]:
            bank, address = parts[0].split(":")
            symbols[parts[1]] = (int(bank, 16), int(address, 16))
    return symbols


SYMS = read_symbols(ROM.with_suffix(".sym"))


class Tester:
    def __init__(self, ram=None):
        self.ram = ram if ram is not None else io.BytesIO(bytes(8192))
        self.p = PyBoy(str(ROM), window="null", cgb=True, ram_file=self.ram, sound_emulated=True)
        self.p.set_emulation_speed(0)
        self.held = set()
        self.frames = 0
        self.trace = []
        self.observed = {}
        self.closed = False
        self.shots = []
        self.provenance = "controller-earned planning path; snapshot branching permitted"
        self.monitor_junction_clues = False
        self.clue_events = []
        self.seen_lanterns = set()
        self.last_combo = 0
        self.monitor_replay = False
        self.room_arrivals = []
        self.boss_events = []
        self.last_replay_identity = None
        self.last_replay_boss = None
        self.main_contacts = {}
        self.p.hook_register(*SYMS["_draw_objects"], self.observe, None)

    def raw(self, name, size=1, signed=False):
        address = SYMS["_" + name][1]
        value = sum(self.p.memory[address + i] << (i * 8) for i in range(size))
        if signed and value >= 1 << (size * 8 - 1):
            value -= 1 << (size * 8)
        return value

    def observe(self, _):
        self.observed = {name: self.raw(name, size, signed) for name, size, signed in (
            ("player_x", 2, True), ("player_y", 2, True),
            ("velocity_x", 2, True), ("velocity_y", 2, True), ("grounded", 1, False))}
        if self.monitor_junction_clues:
            combo = self.raw("combo")
            identity = self.identity()
            if combo > self.last_combo:
                x, y = self.pos()
                for junction in self.route().get("junction_routes", []):
                    for index in junction["clue_pickup_indices"]:
                        pickup = self.route()["pickups"][index]
                        if pickup["kind"] == 1 and x + 2 < pickup["x"] + 11 and x + 14 > pickup["x"] - 3 and y + 2 < pickup["y"] + 16 and y + 16 > pickup["y"] - 2:
                            key = (*identity, index)
                            self.seen_lanterns.add(key)
                            self.clue_events.append({"stage": identity[0], "room": identity[1], "pickup": index,
                                                     "video_frame": int(self.p.frame_count), "combo_before": self.last_combo,
                                                     "combo_after": combo, "position": [x, y]})
            self.last_combo = combo
        if self.monitor_replay and self.raw("game_mode") == 1:
            identity = self.identity()
            contacts = self.main_contacts.setdefault(identity, set())
            x, y = self.pos()
            for index in self.route()["main_route"]:
                platform = self.platform(index)
                landed = self.read("grounded") or platform["kind"] == 2 and self.read("velocity_y", 2, True) < 0
                if landed and abs(y + 16 - platform["y"]) < 2 and x + 12 > platform["x"] and x + 3 < platform["x"] + platform["w"]:
                    contacts.add(index)
            if identity != self.last_replay_identity:
                self.room_arrivals.append({"stage": identity[0], "room": identity[1],
                                           "video_frame": int(self.p.frame_count),
                                           "stage_frames": self.raw("stage_frames", 2),
                                           "stage_seals": self.raw("seal_count"), "deaths": self.raw("deaths", 2)})
                self.last_replay_identity = identity
            boss = self.route()["boss"]
            if boss:
                state = (*identity, self.raw("boss_hp"))
                if state != self.last_replay_boss:
                    self.boss_events.append({"stage": identity[0], "room": identity[1], "boss_type": boss,
                                             "hp": state[2], "video_frame": int(self.p.frame_count)})
                    self.last_replay_boss = state

    def read(self, name, size=1, signed=False):
        return self.observed.get(name, self.raw(name, size, signed))

    def pos(self):
        return self.read("player_x", 2, True) / 16, self.read("player_y", 2, True) / 16

    def route(self):
        return ROUTES[self.read("stage_id")]["rooms"][self.read("room_id")]

    def identity(self):
        return self.read("stage_id"), self.read("room_id")

    def state(self):
        return {"x": self.pos()[0], "y": self.pos()[1],
                "vx": self.read("velocity_x", 2, True) / 16,
                "vy": self.read("velocity_y", 2, True) / 16,
                **{name: self.read(name) for name in ("game_mode", "stage_id", "room_id", "health", "grounded", "dash_charge", "seal_count")},
                "deaths": self.read("deaths", 2), "camera": self.read("camera_x", 2)}

    def platform(self, index):
        platform = dict(self.route()["platforms"][index])
        # Native packed PlatformDef: uint16 x, uint8 y,w,kind. A mover's
        # collision position is the current RAM x, not its authored home x.
        address = SYMS["_platforms"][1] + index * 5
        platform["x"] = self.p.memory[address] | self.p.memory[address + 1] << 8
        return platform

    def tick(self, count=1, buttons=()):
        buttons = set(buttons)
        for button in self.held - buttons:
            self.p.button_release(button)
        for button in buttons - self.held:
            self.p.button_press(button)
        self.held = buttons
        self.p.tick(count)
        self.frames += count
        self.trace.append([count, sorted(buttons)])

    def tap(self, button, wait=12):
        self.tick(3, [button])
        self.tick(wait)

    def shot(self, name):
        directory = ROOT / "docs/screenshots"
        directory.mkdir(parents=True, exist_ok=True)
        native = directory / (name + "-native.png")
        enlarged = directory / (name + ".png")
        self.p.screen.image.save(native)
        self.p.screen.image.resize((800, 720), Image.Resampling.NEAREST).save(enlarged)
        self.shots.append({"name": name, "stage": self.read("stage_id"), "room": self.read("room_id"),
                           "frames": self.frames, "native": str(native.relative_to(ROOT)),
                           "native_sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
                           "enlarged": str(enlarged.relative_to(ROOT)), "provenance": self.provenance})

    def checkpoint(self):
        snapshot = io.BytesIO()
        self.p.save_state(snapshot)
        return snapshot.getvalue(), self.held.copy(), self.frames, len(self.trace), dict(self.observed), len(self.clue_events), self.last_combo

    def rollback(self, snapshot):
        self.p.load_state(io.BytesIO(snapshot[0]))
        self.held = snapshot[1].copy()
        self.frames = snapshot[2]
        self.trace = self.trace[:snapshot[3]]
        self.observed = dict(snapshot[4])
        self.clue_events = self.clue_events[:snapshot[5]]
        self.seen_lanterns = {(event["stage"], event["room"], event["pickup"]) for event in self.clue_events}
        self.last_combo = snapshot[6]

    def start(self):
        self.tick(180)
        self.shot("title")
        self.tap("start", 120)
        self.shot("story")
        self.tap("a", 90)
        assert self.read("game_mode") == 1, self.state()
        self.shot("harbor")

    def current_platform(self):
        x, y = self.pos()
        for index in range(len(self.route()["platforms"])):
            platform = self.platform(index)
            if x + 12 > platform["x"] and x + 3 < platform["x"] + platform["w"] and abs(y + 16 - platform["y"]) < 2:
                if self.read("grounded") or platform["kind"] == 2 and self.read("velocity_y", 2, True) < 0:
                    return index
        return None

    def walk(self, target, limit=220):
        death = self.read("deaths", 2)
        identity = self.identity()
        for _ in range(limit):
            x, _ = self.pos()
            velocity = self.read("velocity_x", 2, True) / 16
            destination = target() if callable(target) else target
            delta = destination - x
            if abs(delta) < 2 and abs(velocity) < .35 and self.read("grounded"):
                self.tick(2)
                return
            steer = [] if abs(delta) < velocity ** 2 * 1.4 + 1 and delta * velocity >= 0 else ["right" if delta > 0 else "left"]
            self.tick(1, steer)
            if self.read("deaths", 2) != death:
                raise AssertionError(("walk died", destination, self.state()))
            if self.read("game_mode") != 1 or self.identity() != identity:
                return
        raise AssertionError(("walk timeout", destination, self.state()))

    def jump(self, index, collect=None):
        route = self.route()
        identity = self.identity()
        authored = route["platforms"][index]
        if not self.read("grounded") and self.current_platform() is None:
            settle = self.checkpoint()
            death = self.read("deaths", 2)
            for _ in range(45):
                self.tick(1)
                if self.read("grounded") or self.read("deaths", 2) != death:
                    break
            if self.read("deaths", 2) != death:
                self.rollback(settle)
        base = self.checkpoint()
        source_index = self.current_platform()
        offsets = [authored["w"] / 2 - 8, 8, authored["w"] - 24]
        if collect is not None:
            offsets.insert(0, route["pickups"][collect]["x"] - authored["x"] - 4)
        source = self.platform(source_index) if source_index is not None else None
        can_drop = source is not None and source["kind"] == 1 and authored["y"] > source["y"]
        strategies = [(hold, dash, False) for hold in (24, 36, 14, 48, 1, 2, 3, 6, 0) for dash in (-1, 10, 17, 5, 0)]
        if can_drop:
            strategies = [(0, dash, True) for dash in (-1, -2, 5, 10)] + strategies
        for offset in offsets:
            for hold, dash_at, drop in strategies:
                self.rollback(base)
                death = self.read("deaths", 2)
                destination = self.platform(index)["x"] + offset
                if source_index is not None and self.platform(source_index)["kind"] not in (2, 3, 4):
                    source = self.platform(source_index)
                    x, _ = self.pos()
                    launch = x if abs(destination - x) <= 72 else max(source["x"] - 2, min(source["x"] + source["w"] - 16, destination - 52 if destination > x else destination + 52))
                    try:
                        self.walk(launch, 180)
                    except AssertionError:
                        self.rollback(base)
                self.tick(2)
                if drop:
                    drop_buttons = ["down", "a"]
                    if dash_at == -2:
                        drop_buttons.extend(["b", "right" if destination > self.pos()[0] else "left"])
                    self.tick(3, drop_buttons)
                airborne = drop
                for frame in range(130):
                    platform = self.platform(index)
                    target = platform["x"] + offset
                    x, _ = self.pos()
                    velocity = self.read("velocity_x", 2, True) / 16
                    delta = target - x
                    buttons = ["a"] if frame < hold and not drop else []
                    if (drop or airborne) and self.read("grounded"):
                        standing = self.current_platform()
                        if standing is not None and self.platform(standing)["kind"] == 1 and self.platform(standing)["y"] < platform["y"]:
                            # A returning roof can cross several one-way
                            # shelves. Release A between presses so each
                            # drop ignores only the shelf currently ridden.
                            buttons = []
                            if "a" not in self.held:
                                buttons.extend(["down", "a"])
                    if abs(delta) > velocity ** 2 * 1.25 + 1 or delta * velocity < 0:
                        buttons.append("right" if delta > 0 else "left")
                    if frame == dash_at:
                        buttons.append("b")
                    self.tick(1, buttons)
                    airborne |= not self.read("grounded")
                    if self.read("deaths", 2) != death or self.read("game_mode") != 1 or self.identity() != identity:
                        break
                    x, y = self.pos()
                    platform = self.platform(index)
                    taken = collect is None or ((*identity, collect) in self.seen_lanterns if route["pickups"][collect]["kind"] == 1 else self.p.memory[SYMS["_pickup_taken"][1] + collect])
                    landed = self.read("grounded") or platform["kind"] == 2 and self.read("velocity_y", 2, True) < 0
                    stable = platform["kind"] in (2, 4) or (abs(self.read("velocity_x", 2, True)) <= 12 and abs(target - x) <= 8)
                    if (airborne or hold == 0) and frame > 5 and x + 12 > platform["x"] and x + 3 < platform["x"] + platform["w"] and abs(y + 16 - platform["y"]) < 2 and taken and landed and stable:
                        if platform["kind"] not in (2, 4):
                            self.tick(3)
                            if self.read("deaths", 2) != death or self.identity() != identity:
                                break
                        return
        self.rollback(base)
        directory = ROOT / "build"
        directory.mkdir(exist_ok=True)
        (directory / "failed-state.bin").write_bytes(base[0])
        (directory / "failed-state.json").write_text(json.dumps({"held": list(base[1]), "frames": base[2], "observed": base[4], "trace": self.trace, "target_platform": index, "collect": collect, "stage": identity[0], "room": identity[1]}, indent=2))
        raise AssertionError(("cannot jump", identity, index, collect, self.state(), authored))

    def boss(self, prepared=False):
        route = self.route()
        boss_type = route["boss"]
        if not prepared:
            self.tick(10, ["right", "b"])
            self.tick(3, ["right"])
            self.walk(route["goal_x"] + 24)
        base = self.checkpoint()
        (ROOT / "build/boss-state.bin").write_bytes(base[0])
        (ROOT / "build/boss-state.json").write_text(json.dumps({"held": list(base[1]), "frames": base[2], "observed": base[4], "trace": self.trace, "boss_type": boss_type}, indent=2))
        self.shot(f"boss-{boss_type}")
        for hit in range(6 - self.read("boss_hp"), 6):
            base = self.checkpoint()
            hp = self.read("boss_hp")
            death = self.read("deaths", 2)
            health = self.read("health")
            success = False
            waits = (0, 15, 30, 45, 60, 75, 90, 8, 22, 38, 52, 68, 82, 98, 112, 124)
            dashes = (14, 10, 18, 22, -1, 6, 2, 26, 30, 34)
            strategies = [(loss, wait, dash) for loss in (0, 1) for wait in waits for dash in dashes]
            for allowed_loss, wait, dash_at in strategies:
                self.rollback(base)
                self.tick(wait)
                self.tick(2)
                for frame in range(110):
                    x, _ = self.pos()
                    target = self.read("boss_x", 2) + 4
                    velocity = self.read("velocity_x", 2, True) / 16
                    delta = target - x
                    buttons = ["a"] if frame < 36 else []
                    if abs(delta) > velocity ** 2 * 1.25 + 1 or delta * velocity < 0:
                        buttons.append("right" if delta > 0 else "left")
                    if frame == dash_at and not self.read("boss_guard"):
                        buttons.append("b")
                    self.tick(1, buttons)
                    if self.read("deaths", 2) != death:
                        break
                    if self.read("boss_hp") < hp:
                        if not self.read("boss_hp"):
                            success = True
                        else:
                            recoil = self.checkpoint()
                            for hold in (28, 40, 20, 0):
                                for dash in (-1, 38, 48, 25):
                                    self.rollback(recoil)
                                    target = route["goal_x"] + 24
                                    for recovery in range(110):
                                        x, _ = self.pos()
                                        velocity = self.read("velocity_x", 2, True) / 16
                                        delta = target - x
                                        retreat = ["a"] if recovery < hold else []
                                        if abs(delta) > velocity ** 2 * 1.25 + 1 or delta * velocity < 0:
                                            retreat.append("right" if delta > 0 else "left")
                                        if recovery == dash:
                                            retreat.append("b")
                                        self.tick(1, retreat)
                                        if self.read("deaths", 2) != death:
                                            break
                                        recovered = abs(target - self.pos()[0]) <= 12 and abs(self.read("velocity_x", 2, True)) <= 16
                                        if self.read("health") >= max(1, health - allowed_loss) and self.read("grounded") and recovered:
                                            success = True
                                            break
                                    if success:
                                        break
                                if success:
                                    break
                        if success:
                            self.shot(f"boss-{boss_type}-hit-{hit + 1}")
                        break
                if success:
                    break
            if not success:
                self.rollback(base)
                (ROOT / "build/boss-failed-state.bin").write_bytes(base[0])
                (ROOT / "build/boss-failed-state.json").write_text(json.dumps({"held": list(base[1]), "frames": base[2], "observed": base[4], "trace": self.trace, "boss_type": boss_type, "hp": hp}, indent=2))
                raise AssertionError(("boss hit failed", boss_type, hp, self.state()))
        assert not self.read("boss_hp"), self.state()

    def finish_room(self, require_seals=True):
        route = self.route()
        identity = self.identity()
        death = self.read("deaths", 2)
        clock_before = self.read("stage_frames", 2)
        for _ in range(320):
            if self.read("game_mode") == 3 or self.identity() != identity:
                break
            x, _ = self.pos()
            buttons = ["right"]
            near_enemy = any(enemy["kind"] != 2 and abs(enemy["x"] - x) < 55 and self.p.memory[SYMS["_enemy_alive"][1] + index] for index, enemy in enumerate(route["enemies"]))
            if near_enemy and self.read("dash_charge"):
                buttons.append("b")
            self.tick(1, buttons)
            if self.read("deaths", 2) != death:
                raise AssertionError(("room exit died", identity, self.state()))
        self.tick(15)
        if identity[1] < 2:
            assert self.read("game_mode") == 1 and self.identity() == (identity[0], identity[1] + 1), self.state()
            assert self.read("stage_frames", 2) >= clock_before, self.state()
            if require_seals:
                assert self.read("seal_count") == (identity[1] + 1) * 3, self.state()
            return
        assert self.read("game_mode") == 3, self.state()
        if require_seals:
            assert self.read("seal_count") == 9, self.state()
        self.clear_frames = self.read("stage_frames", 2)
        self.shot(f"stage-{identity[0] + 1}-clear")
        self.tap("a", 120)
        if self.read("game_mode") == 5:
            self.tap("a", 90)

    def finish(self):
        self.finish_room()

    def close(self):
        if self.closed:
            return
        self.ram.seek(0)
        self.p.stop(ram_file=self.ram)
        self.ram.seek(0)
        self.closed = True


def compressed_trace(trace):
    result = []
    for count, buttons in trace:
        if result and result[-1][1] == buttons:
            result[-1][0] += count
        else:
            result.append([count, buttons])
    return result


def completed_masks(tester):
    address = SYMS["_seal_bits"][1]
    return [tester.p.memory[address + index * 2] | tester.p.memory[address + index * 2 + 1] << 8 for index in range(24)]


def run(until_room=None, resume_progress=False):
    global ROM, SYMS
    production_rom = ROOT / "dist/moonwake.gbc"
    digest = hashlib.sha256(production_rom.read_bytes()).hexdigest()
    snapshot_directory = ROOT / "build/planner-source"
    snapshot_directory.mkdir(parents=True, exist_ok=True)
    for extension in ("gbc", "sym"):
        shutil.copy2(ROOT / f"dist/moonwake.{extension}", snapshot_directory / f"moonwake.{extension}")
    ROM = snapshot_directory / "moonwake.gbc"
    SYMS = read_symbols(ROM.with_suffix(".sym"))
    tester = Tester()
    results = []
    stage_results = []
    start_room = 0
    if resume_progress:
        prefix = json.loads((ROOT / "build/progress-inputs.json").read_text())
        assert prefix["rom_sha256"] == digest, "A planning prefix may resume only its exact ROM."
        for count, buttons in prefix["inputs"]:
            tester.tick(count, buttons)
        boundary = tuple(prefix["last_room"])
        results = json.loads((ROOT / "build/progress.json").read_text())
        assert (results[-1]["stage"], results[-1]["room"]) == boundary
        assert tester.identity() == boundary and tester.read("seal_count") == (boundary[1] + 1) * 3, tester.state()
        assert tester.frames == prefix["frames"], (tester.frames, prefix["frames"])
        tester.finish_room()
        start_room = boundary[0] * 3 + boundary[1] + 1
        for stage in ROUTES[:start_room // 3]:
            address = SYMS["_best_frames"][1] + stage["id"] * 2
            clear_frames = tester.p.memory[address] | tester.p.memory[address + 1] << 8
            stage_results.append({"id": stage["id"], "name": stage["name"], "seals": 9,
                                  "frames": clear_frames, "par_seconds": stage["par_seconds"], "deaths": 0})
        print(f"Fresh controller prefix resumed after stage {boundary[0] + 1}, room {boundary[1] + 1}.", flush=True)
    else:
        tester.start()
    try:
        for stage in ROUTES:
            if stage["id"] * 3 + 2 < start_room:
                continue
            assert tester.read("stage_id") == stage["id"], tester.state()
            for route in stage["rooms"]:
                if stage["id"] * 3 + route["room_id"] < start_room:
                    continue
                identity = (stage["id"], route["room_id"])
                assert tester.identity() == identity, tester.state()
                print(f"STAGE {stage['id'] + 1:02d} ROOM {route['room_id'] + 1}: {route['name']}", flush=True)
                if stage["id"] % 3 == 0 and route["room_id"] == 0:
                    tester.shot(f"world-{route['biome'] + 1}")
                if not route.get("original_first_room"):
                    tester.shot(f"room-{stage['id'] + 1:02d}-{route['room_id'] + 1}-opening")
                main = route["main_route"]
                branches = {branch["entry_main_platform"]: branch for branch in route["seal_routes"]}
                skip_to = -1
                for index in main:
                    if index < skip_to:
                        continue
                    if tester.current_platform() != index and not (route["platforms"][index]["kind"] == 3 and tester.p.memory[SYMS["_crumble"][1] + index] >= 40):
                        tester.jump(index)
                    if index in branches:
                        branch = branches[index]
                        seal_platform = branch.get("seal_platform_index", branch["platform_indices"][-1])
                        for branch_index in branch["platform_indices"]:
                            if route["platforms"][branch_index]["kind"] == 3 and tester.p.memory[SYMS["_crumble"][1] + branch_index] >= 40:
                                continue
                            tester.jump(branch_index, collect=branch["seal_pickup_index"] if branch_index == seal_platform else None)
                        tester.jump(branch["rejoin_main_platform"])
                        skip_to = branch["rejoin_main_platform"]
                if route["boss"]:
                    tester.boss()
                expected_seals = (route["room_id"] + 1) * 3
                assert tester.read("seal_count") == expected_seals, ("missing seal", identity, tester.state())
                frames = tester.read("stage_frames", 2)
                results.append({"stage": stage["id"], "room": route["room_id"], "name": route["name"], "stage_seals": expected_seals, "stage_frames": frames, "deaths": tester.read("deaths", 2), "boss_type": route["boss"]})
                (ROOT / "build/progress.json").write_text(json.dumps(results, indent=2) + "\n")
                (ROOT / "build/progress-inputs.json").write_text(json.dumps({"rom_sha256": digest, "frames": tester.frames, "last_room": identity, "inputs": compressed_trace(tester.trace)}, separators=(",", ":")) + "\n")
                tester.shot(f"room-{stage['id'] + 1:02d}-{route['room_id'] + 1}-verified")
                if until_room == identity:
                    print("Requested partial traversal completed.", flush=True)
                    return
                tester.finish_room()
            stage_results.append({"id": stage["id"], "name": stage["name"], "seals": 9, "frames": tester.clear_frames, "par_seconds": stage["par_seconds"], "deaths": tester.read("deaths", 2)})
        assert tester.read("game_mode") == 6 and tester.read("completed") and all(mask == 0x1FF for mask in completed_masks(tester)), tester.state()
        tester.shot("ending")
        trace = compressed_trace(tester.trace)
        artifact = {"rom_sha256": digest, "frames": tester.frames, "inputs": trace}
        (ROOT / "build/planned-inputs.json").write_text(json.dumps(artifact, separators=(",", ":")) + "\n")
        tester.close()
        (ROOT / "build/completed-test.sav").write_bytes(tester.ram.getvalue()[:8192])
        again = Tester(tester.ram)
        again.tick(180)
        assert again.read("completed") and again.read("unlocked") == 23 and all(mask == 0x1FF for mask in completed_masks(again)), again.state()
        again.close()
        linear = Tester()
        linear.provenance = "fresh blank-SRAM linear controller replay; no snapshots or gameplay-memory writes"
        pending_capture = None
        captured_rooms = set()
        for count, buttons in trace:
            linear.tick(count, buttons)
            if linear.frames == 180:
                linear.shot("linear-title")
            if linear.read("game_mode") == 1:
                identity = linear.identity()
                if identity not in captured_rooms:
                    if pending_capture is None or pending_capture[0] != identity:
                        pending_capture = (identity, linear.frames + 40)
                    if linear.frames >= pending_capture[1]:
                        linear.shot(f"linear-room-{identity[0] + 1:02d}-{identity[1] + 1}")
                        captured_rooms.add(identity)
                        pending_capture = None
        assert linear.read("completed") and linear.read("game_mode") == 6 and all(mask == 0x1FF for mask in completed_masks(linear)), linear.state()
        assert len(captured_rooms) == 72, ("missing fresh replay captures", len(captured_rooms))
        linear.shot("linear-ending")
        linear.close()
        (ROOT / "build/linear-earned.sav").write_bytes(linear.ram.getvalue()[:8192])
        if hashlib.sha256(production_rom.read_bytes()).hexdigest() != digest:
            raise RuntimeError("The production ROM changed during verification; evidence belongs to the snapshotted ROM.")
        (ROOT / "dist/verified-inputs.json").write_text(json.dumps(artifact, separators=(",", ":")) + "\n")
        capture_manifest = {"rom_sha256": digest, "fresh_linear_rooms_captured": 72,
                            "native_resolution": [160, 144], "scale_filter": "nearest",
                            "captures": tester.shots + linear.shots}
        (ROOT / "dist/capture-manifest.json").write_text(json.dumps(capture_manifest, indent=2) + "\n")
        report = {"rom_sha256": digest, "input_only": True, "linear_replay_passed": True,
                  "all_24_stages_completed": True, "all_72_rooms_completed": True,
                  "all_216_seals_collected": True, "saved_completion_restored": True,
                  "frames": artifact["frames"], "rooms": results, "stages": stage_results,
                  "all_four_boss_types_verified": sorted({room["boss_type"] for room in results if room["boss_type"]}),
                  "capture_manifest": "dist/capture-manifest.json",
                  "duration_is_first_player_measurement": False}
        (ROOT / "dist/playtest-report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key not in ("rooms", "stages")}, indent=2), flush=True)
    finally:
        tester.close()


def run_main_routes(resume_progress=False):
    """Exercise every main surface, including lanes scenic forks bypass."""
    global ROM, SYMS
    production_rom = ROOT / "dist/moonwake.gbc"
    digest = hashlib.sha256(production_rom.read_bytes()).hexdigest()
    source = ROOT / "build/main-route-source"
    source.mkdir(parents=True, exist_ok=True)
    for extension in ("gbc", "sym"):
        shutil.copy2(ROOT / f"dist/moonwake.{extension}", source / f"moonwake.{extension}")
    ROM = source / "moonwake.gbc"
    SYMS = read_symbols(ROM.with_suffix(".sym"))
    tester = Tester()
    # Main-lane probes do not overwrite the all-seal capture manifest.
    tester.shot = lambda name: None
    results = []
    start_room = 0
    try:
        if resume_progress:
            prefix = json.loads((ROOT / "build/main-progress-inputs.json").read_text())
            assert prefix["rom_sha256"] == digest, "A planning prefix may resume only its exact ROM."
            for count, buttons in prefix["inputs"]:
                tester.tick(count, buttons)
            boundary = tuple(prefix["last_room"])
            results = json.loads((ROOT / "build/main-progress.json").read_text())
            assert tester.identity() == boundary and tester.frames == prefix["frames"], tester.state()
            tester.finish_room(require_seals=False)
            start_room = boundary[0] * 3 + boundary[1] + 1
        else:
            tester.start()
        for stage in ROUTES:
            for route in stage["rooms"]:
                if stage["id"] * 3 + route["room_id"] < start_room:
                    continue
                identity = (stage["id"], route["room_id"])
                assert tester.identity() == identity, tester.state()
                print(f"MAIN STAGE {stage['id'] + 1:02d} ROOM {route['room_id'] + 1}: {route['name']}", flush=True)
                for index in route["main_route"]:
                    if tester.current_platform() != index:
                        tester.jump(index)
                if route["boss"]:
                    tester.boss()
                results.append({"stage": stage["id"], "room": route["room_id"],
                                "platform_indices": route["main_route"], "boss_type": route["boss"],
                                "deaths": tester.read("deaths", 2), "stage_frames": tester.read("stage_frames", 2)})
                (ROOT / "build/main-progress.json").write_text(json.dumps(results, indent=2) + "\n")
                prefix = {"rom_sha256": digest, "frames": tester.frames, "last_room": identity,
                          "inputs": compressed_trace(tester.trace)}
                (ROOT / "build/main-progress-inputs.json").write_text(json.dumps(prefix, separators=(",", ":")) + "\n")
                tester.finish_room(require_seals=False)
        assert tester.read("completed") and tester.read("game_mode") == 6, tester.state()
        artifact = {"rom_sha256": digest, "frames": tester.frames,
                    "inputs": compressed_trace(tester.trace)}
        linear = Tester()
        linear.shot = lambda name: None
        linear.monitor_replay = True
        try:
            for count, buttons in artifact["inputs"]:
                linear.tick(count, buttons)
            assert linear.read("completed") and linear.read("game_mode") == 6, linear.state()
            assert linear.read("deaths", 2) == tester.read("deaths", 2), linear.state()
            missing = [(stage["id"], room["room_id"], sorted(set(room["main_route"]) - linear.main_contacts.get((stage["id"], room["room_id"]), set())))
                       for stage in ROUTES for room in stage["rooms"]
                       if set(room["main_route"]) - linear.main_contacts.get((stage["id"], room["room_id"]), set())]
            assert not missing, ("missing native main-surface contacts", missing)
        finally:
            linear.close()
        assert hashlib.sha256(production_rom.read_bytes()).hexdigest() == digest, "The production ROM changed during main-route verification."
        (ROOT / "dist/main-route-inputs.json").write_text(json.dumps(artifact, separators=(",", ":")) + "\n")
        report = {"rom_sha256": digest, "input_only": True, "linear_replay_passed": True,
                  "all_72_main_routes_verified": len(results) == 72,
                  "all_four_boss_types_verified": sorted({room["boss_type"] for room in results if room["boss_type"]}),
                  "deaths": tester.read("deaths", 2), "frames": tester.frames, "rooms": results,
                  "fresh_native_main_surface_contacts": [
                      {"stage": identity[0], "room": identity[1], "platform_indices": sorted(indices)}
                      for identity, indices in sorted(linear.main_contacts.items())]}
        (ROOT / "dist/main-route-report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key not in ("rooms", "fresh_native_main_surface_contacts")}, indent=2), flush=True)
    finally:
        tester.close()


def replay_reference(path, main_only=False):
    """Validate old input on current hardware state; regenerate every finding."""
    global ROM, SYMS
    production_rom = ROOT / "dist/moonwake.gbc"
    digest = hashlib.sha256(production_rom.read_bytes()).hexdigest()
    reference = json.loads(Path(path).read_text())
    source = ROOT / "build/reference-replay-source"
    source.mkdir(parents=True, exist_ok=True)
    for extension in ("gbc", "sym"):
        shutil.copy2(ROOT / f"dist/moonwake.{extension}", source / f"moonwake.{extension}")
    ROM = source / "moonwake.gbc"
    SYMS = read_symbols(ROM.with_suffix(".sym"))
    tester = Tester()
    tester.monitor_replay = True
    tester.provenance = "fresh blank-SRAM linear replay of existing controller input on this ROM; no snapshots or gameplay-memory writes"
    stages = []
    captured = set()
    pending = None
    try:
        for count, buttons in reference["inputs"]:
            tester.tick(count, buttons)
            if tester.frames == 180 and not main_only:
                tester.shot("linear-title")
            if tester.read("game_mode") == 1:
                identity = tester.identity()
                if identity not in captured:
                    if pending is None or pending[0] != identity:
                        pending = (identity, tester.frames + 40)
                    if tester.frames >= pending[1]:
                        if not main_only:
                            tester.shot(f"linear-room-{identity[0] + 1:02d}-{identity[1] + 1}")
                        captured.add(identity)
                        pending = None
            if tester.read("game_mode") == 3 and tester.read("room_id") == 2 and tester.read("stage_clear_pending") and tester.read("stage_id") not in {stage["id"] for stage in stages}:
                stage_id = tester.read("stage_id")
                stages.append({"id": stage_id, "name": ROUTES[stage_id]["name"],
                               "seals": tester.read("seal_count"), "frames": tester.read("stage_frames", 2),
                               "rank": tester.read("current_rank"), "par_seconds": ROUTES[stage_id]["par_seconds"],
                               "deaths": tester.read("deaths", 2)})
                print(f"REPLAY STAGE {stage_id + 1:02d}: {stages[-1]['seals']} seals, rank {stages[-1]['rank']}", flush=True)
        assert tester.read("completed") and tester.read("game_mode") == 6, tester.state()
        assert len(tester.room_arrivals) == 72 and len(stages) == 24 and len(captured) == 72, (len(tester.room_arrivals), len(stages), len(captured))
        bosses = {event["boss_type"] for event in tester.boss_events if event["hp"] == 0}
        assert bosses == {1, 2, 3, 4}, tester.boss_events
        if main_only:
            missing = [(stage["id"], room["room_id"], sorted(set(room["main_route"]) - tester.main_contacts.get((stage["id"], room["room_id"]), set())))
                       for stage in ROUTES for room in stage["rooms"]
                       if set(room["main_route"]) - tester.main_contacts.get((stage["id"], room["room_id"]), set())]
            assert not missing, ("missing native main-surface contacts", missing)
        rooms = []
        for arrival in tester.room_arrivals:
            stage_id, room_id = arrival["stage"], arrival["room"]
            if room_id < 2:
                end = next(event for event in tester.room_arrivals if event["stage"] == stage_id and event["room"] == room_id + 1)
                frames, seals = end["stage_frames"], end["stage_seals"]
            else:
                end = next(stage for stage in stages if stage["id"] == stage_id)
                frames, seals = end["frames"], end["seals"]
            rooms.append({"stage": stage_id, "room": room_id, "name": ROUTES[stage_id]["rooms"][room_id]["name"],
                          "stage_frames": frames, "stage_seals": seals, "deaths": end["deaths"],
                          "boss_type": ROUTES[stage_id]["rooms"][room_id]["boss"]})
        if not main_only:
            assert all(room["stage_seals"] == (room["room"] + 1) * 3 for room in rooms), rooms
            assert all(mask == 0x1FF for mask in completed_masks(tester)), completed_masks(tester)
            assert all(stage["rank"] == 3 for stage in stages), stages
            tester.shot("linear-ending")
        deaths = tester.read("deaths", 2)
        tester.close()
        again = Tester(tester.ram)
        try:
            again.tick(180)
            assert again.read("completed") and again.read("unlocked") == 23, again.state()
            if not main_only:
                assert all(mask == 0x1FF for mask in completed_masks(again)), completed_masks(again)
        finally:
            again.close()
        assert hashlib.sha256(production_rom.read_bytes()).hexdigest() == digest, "ROM changed during linear replay."
        artifact = {"rom_sha256": digest, "frames": tester.frames, "inputs": compressed_trace(tester.trace),
                    "input_origin_rom_sha256": reference["rom_sha256"],
                    "proof_provenance": "Actual fresh blank-SRAM linear replay on this exact ROM; observations regenerated."}
        report = {"rom_sha256": digest, "input_only": True, "linear_replay_passed": True,
                  "all_24_stages_completed": True, "all_72_rooms_completed": True,
                  "all_four_boss_types_verified": sorted(bosses), "saved_completion_restored": True,
                  "frames": tester.frames, "deaths": deaths, "rooms": rooms, "stages": stages,
                  "input_origin_rom_sha256": reference["rom_sha256"], "duration_is_first_player_measurement": False}
        if main_only:
            report["all_72_main_routes_verified"] = True
            stem = "main-route"
        else:
            report["all_216_seals_collected"] = True
            report["all_24_s_ranks_verified"] = True
            report["capture_manifest"] = "dist/capture-manifest.json"
            stem = "playtest"
            manifest = {"rom_sha256": digest, "fresh_linear_rooms_captured": 72,
                        "native_resolution": [160, 144], "scale_filter": "nearest", "captures": tester.shots}
            (ROOT / "dist/capture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            (ROOT / "build/linear-earned.sav").write_bytes(tester.ram.getvalue()[:8192])
        filename = "main-route-inputs.json" if main_only else "verified-inputs.json"
        (ROOT / "dist" / filename).write_text(json.dumps(artifact, separators=(",", ":")) + "\n")
        (ROOT / "dist" / f"{stem}-report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key not in ("rooms", "stages")}, indent=2), flush=True)
    finally:
        tester.close()


def run_junction_routes():
    """Visit new roof links both ways and activate every added clue."""
    global ROM, SYMS
    digest = hashlib.sha256((ROOT / "dist/moonwake.gbc").read_bytes()).hexdigest()
    reference = json.loads((ROOT / "dist/verified-inputs.json").read_text())
    assert reference["rom_sha256"] == digest, "Matching final campaign input is required before junction probes."
    source = ROOT / "build/junction-source"
    source.mkdir(parents=True, exist_ok=True)
    for extension in ("gbc", "sym"):
        shutil.copy2(ROOT / f"dist/moonwake.{extension}", source / f"moonwake.{extension}")
    ROM = source / "moonwake.gbc"
    SYMS = read_symbols(ROM.with_suffix(".sym"))
    recordings, results = [], []
    for identity in ((18, 1), (21, 1), (23, 1)):
        tester = Tester()
        tester.shot = lambda name: None
        try:
            for count, buttons in reference["inputs"]:
                tester.tick(count, buttons)
                if tester.read("game_mode") == 1 and tester.identity() == identity and tester.pos()[0] < 128 and tester.current_platform() == 0:
                    break
            assert tester.identity() == identity and tester.current_platform() == 0, tester.state()
            tester.monitor_junction_clues = True
            tester.last_combo = tester.read("combo")
            route = tester.route()
            junction = route["junction_routes"][0]
            stars = [index for index in junction["clue_pickup_indices"] if route["pickups"][index]["kind"] == 0]
            lantern = next(index for index in junction["clue_pickup_indices"] if route["pickups"][index]["kind"] == 1)
            visits = []

            def hop(index, collect=None, direction=None):
                tester.jump(index, collect)
                if index in junction["platform_indices"]:
                    visits.append({"platform": index, "direction": direction, "video_frame": tester.frames,
                                   "position": list(tester.pos()), "actual_platform_x": tester.platform(index)["x"]})

            print(f"JUNCTION {route['name']}: forward, clues, next seal, reverse", flush=True)
            if identity == (18, 1):
                for index in (1, 2, 3):
                    hop(index)
                hop(24, stars[0], "forward")
                hop(15, lantern)
                branch = route["seal_routes"][1]
                for index in (16, 17, 18, 19):
                    hop(index, branch["seal_pickup_index"] if index == 19 else None)
                for index in (18, 17, 16, 15):
                    hop(index)
                hop(24, direction="reverse")
                hop(3)
            elif identity == (21, 1):
                hop(1)
                first = route["seal_routes"][0]
                for index in (11, 12, 13, 14, 15):
                    hop(index, first["seal_pickup_index"] if index == 15 else None)
                hop(14)
                hop(24, stars[0], "forward")
                hop(24, lantern, "lantern")
                hop(25, stars[1], "forward")
                branch = route["seal_routes"][1]
                for index in (16, 17, 18, 19):
                    hop(index, branch["seal_pickup_index"] if index == 19 else None)
                for index in (18, 17, 16):
                    hop(index)
                hop(25, direction="reverse")
                hop(24, direction="reverse")
                hop(14)
            else:
                for index in (1, 2, 3, 4):
                    hop(index)
                branch = route["seal_routes"][1]
                for index in (16, 17, 18, 19):
                    hop(index, branch["seal_pickup_index"] if index == 19 else None)
                hop(24, lantern, "forward")
                hop(24, stars[0], "star")
                hop(20)
                hop(24, direction="reverse")
                hop(19)
            assert all(tester.p.memory[SYMS["_pickup_taken"][1] + index] for index in stars), ("star clue missing", identity)
            assert (*identity, lantern) in tester.seen_lanterns, ("lantern activation missing", identity)
            artifact = {"rom_sha256": digest, "stage": identity[0], "room": identity[1],
                        "frames": tester.frames, "inputs": compressed_trace(tester.trace)}
            linear = Tester()
            linear.monitor_junction_clues = True
            fresh_visits = []
            visit_cursor = 0
            try:
                for count, buttons in artifact["inputs"]:
                    remaining = count
                    while remaining:
                        next_visit = visits[visit_cursor] if visit_cursor < len(visits) else None
                        chunk = min(remaining, next_visit["video_frame"] - linear.frames) if next_visit else remaining
                        if chunk:
                            linear.tick(chunk, buttons)
                            remaining -= chunk
                        if next_visit and linear.frames == next_visit["video_frame"]:
                            index = next_visit["platform"]
                            platform = linear.platform(index)
                            x, y = linear.pos()
                            assert linear.identity() == identity and linear.read("grounded"), linear.state()
                            assert abs(y + 16 - platform["y"]) < 2 and x + 12 > platform["x"] and x + 3 < platform["x"] + platform["w"], ("fresh bridge contact missing", index, linear.state())
                            fresh_visits.append({"platform": index, "direction": next_visit["direction"],
                                                 "video_frame": linear.frames, "position": [x, y],
                                                 "actual_platform_x": platform["x"]})
                            visit_cursor += 1
                assert linear.identity() == identity and linear.read("deaths", 2) == tester.read("deaths", 2), linear.state()
                assert all(linear.p.memory[SYMS["_pickup_taken"][1] + index] for index in stars), identity
                assert (*identity, lantern) in linear.seen_lanterns, ("fresh lantern activation missing", identity)
                assert linear.p.memory[SYMS["_pickup_taken"][1] + branch["seal_pickup_index"]], ("following seal missing", identity)
                assert len(fresh_visits) == len(visits), ("missing fresh bridge visits", identity)
                linear.provenance = "fresh blank-SRAM linear junction/clue replay; no snapshots or gameplay-memory writes"
                linear.shot(f"junction-{identity[0] + 1:02d}-{identity[1] + 1}-verified")
                results.append({"stage": identity[0], "room": identity[1], "name": route["name"],
                                "bridge_visits": fresh_visits, "clue_pickup_indices": junction["clue_pickup_indices"],
                                "fresh_lantern_events": linear.clue_events, "following_seal": branch["seal_pickup_index"],
                                "linear_replay_passed": True, "deaths": linear.read("deaths", 2), "captures": linear.shots})
            finally:
                linear.close()
            recordings.append(artifact)
        finally:
            tester.close()
    assert hashlib.sha256((ROOT / "dist/moonwake.gbc").read_bytes()).hexdigest() == digest, "ROM changed during junction proof."
    report = {"rom_sha256": digest, "input_only": True, "all_three_junctions_verified": True,
              "all_four_bridges_bidirectional": True, "all_seven_clues_activated": True, "probes": results}
    (ROOT / "dist/junction-inputs.json").write_text(json.dumps({"rom_sha256": digest, "recordings": recordings}, separators=(",", ":")) + "\n")
    (ROOT / "dist/junction-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "probes"}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--until-room", help="Stop after a controller-earned zero-based STAGE:ROOM for focused debugging.")
    parser.add_argument("--resume-progress", action="store_true", help="Replay the exact-ROM accepted prefix fresh, then plan after its latest verified room.")
    parser.add_argument("--main-only", action="store_true", help="Verify every main-route surface in a second campaign and fresh linear replay.")
    parser.add_argument("--replay-reference", help="Replay a prior recording fresh on the current ROM and regenerate native proof/captures.")
    parser.add_argument("--junction-only", action="store_true", help="Exercise every appended roof link in both directions and activate all clue pickups.")
    options = parser.parse_args()
    until_room = tuple(int(value) for value in options.until_room.split(":")) if options.until_room else None
    if options.junction_only:
        run_junction_routes()
    elif options.replay_reference:
        replay_reference(options.replay_reference, options.main_only)
    elif options.main_only:
        run_main_routes(options.resume_progress)
    else:
        run(until_room, options.resume_progress)


if __name__ == "__main__":
    main()
