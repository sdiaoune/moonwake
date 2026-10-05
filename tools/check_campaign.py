"""Validate Moonwake's authored campaign and exploration route annotations.

These checks enforce the native content contract. They do not replace joypad
playtests or establish a measured first-player completion time.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES_PATH = ROOT / "docs/routes.json"
CAPS = {"platforms": 48, "pickups": 64, "enemies": 12}
BOSS_STAGES = {5: 1, 11: 2, 17: 3, 23: 4}


def platform_gap(a: dict, b: dict) -> int:
    """Gap between two static intervals, including reversed loop jumps."""
    if b["x"] >= a["x"] + a["w"]:
        return b["x"] - a["x"] - a["w"]
    if a["x"] >= b["x"] + b["w"]:
        return a["x"] - b["x"] - b["w"]
    return 0


def validate_campaign(data: dict) -> dict:
    errors = []
    risks = []
    stages = data.get("levels", [])
    room_count = 0
    total_length = 0
    total_seals = 0
    substantial_forks = 0
    movers = 0
    jellies = 0
    wind_rooms = 0
    new_main_shapes = {}

    def require(condition: bool, location: str, message: str) -> None:
        if not condition:
            errors.append(f"{location}: {message}")

    require(len(stages) == 24, "Campaign", "Expected 24 stages.")
    require(data.get("world_count") == 8, "Campaign", "Expected eight worlds.")
    require(data.get("rooms_per_stage") == 3, "Campaign", "Expected three continuous rooms per stage.")
    preservation = data.get("original_release", {})
    baselines = preservation.get("preserved_first_room_geometry", [])
    signature_fields = preservation.get("signature_fields", [])
    require(len(baselines) == 12 and bool(signature_fields), "Campaign", "Original twelve first-room preservation signatures are required.")
    for baseline in baselines:
        index = baseline["stage"]
        if index >= len(stages) or not stages[index].get("rooms"):
            continue
        first_room = stages[index]["rooms"][0]
        signature_data = {field: first_room[field] for field in signature_fields}
        signature = hashlib.sha256(json.dumps(signature_data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        require(signature == baseline["sha256"], f"Stage {index + 1}", "Preserved v1.0.0 first-room geometry differs from its release signature.")
    for stage_id, stage in enumerate(stages):
        label = f"Stage {stage_id + 1}"
        require(stage.get("id") == stage_id, label, "Stage id must match ordered index.")
        require(0 < len(stage.get("name", "")) <= 18, label, "Stage name exceeds native 18-character label.")
        require(75 <= stage.get("par_seconds", 0) <= 600, label, "Full-stage par must be useful and fit native frames.")
        rooms = stage.get("rooms", [])
        require(len(rooms) == 3, label, "Expected three complete room definitions.")
        require(stage.get("seal_count") == 9, label, "Expected nine optional seals per stage.")
        if not rooms:
            continue
        for field in ("length", "spawn_x", "spawn_y", "goal_x", "goal_y", "checkpoint_x", "checkpoint_y", "platforms", "pickups", "enemies", "main_route", "seal_routes"):
            require(stage.get(field) == rooms[0].get(field), label, f"Legacy room-zero field {field} differs from first room.")
        for room_id, room in enumerate(rooms):
            room_count += 1
            where = f"{label}, room {room_id + 1} ({room.get('name', '?')})"
            require(room.get("id") == stage_id and room.get("room_id") == room_id, where, "Room identity is inconsistent.")
            require(room.get("biome") == stage_id // 3, where, "World must contain exactly three stages.")
            require(0 < len(room.get("name", "")) <= 18, where, "Room name exceeds native label.")
            length = room.get("length", 0)
            total_length += length
            require(1536 <= length <= 1856 and length % 8 == 0, where, "Room length must be 1536–1856 tile-aligned pixels.")
            require(length * 16 < 32768, where, "Room overflows signed 4-bit fixed-point coordinates.")
            require(room.get("mechanic") in (0, 1, 2), where, "Unknown room wind mechanic.")
            require(room.get("boss") == (BOSS_STAGES.get(stage_id, 0) if room_id == 2 else 0), where, "Boss is in the wrong room or world finale.")
            intro = room.get("intro", [])
            require(len(intro) == 3 and all(isinstance(line, str) and len(line) <= 20 for line in intro), where, "Intro must have three lines of at most 20 characters.")
            if room.get("mechanic"):
                wind_rooms += 1
                require(any("WIND" in line for line in intro), where, "Wind must be signposted in the room intro.")
            require(bool(room.get("lesson")) and bool(room.get("movement_annotation")) and bool(room.get("encounter_annotation")), where, "Movement and encounter annotations are required.")
            for group, cap in CAPS.items():
                require(0 < len(room.get(group, [])) <= cap, where, f"{group} count exceeds {cap}.")
            platforms = room.get("platforms", [])
            pickups = room.get("pickups", [])
            enemies = room.get("enemies", [])
            if not platforms:
                continue
            for index, p in enumerate(platforms):
                place = f"{where}, platform {index}"
                require(p["kind"] in range(5), place, "Unknown platform type.")
                require(p["x"] % 8 == p["y"] % 8 == p["w"] % 8 == 0, place, "Platform coordinates and widths must align to tiles.")
                require(0 <= p["x"] and p["x"] + p["w"] <= length, place, "Platform lies beyond room bounds.")
                require(8 <= p["w"] <= 248 and 40 <= p["y"] <= 128, place, "Platform exceeds native width or playfield bounds.")
                if p["kind"] == 4:
                    movers += 1
                    require(24 <= p["w"] <= 40, place, "Moving ledge width must be 24–40 pixels.")
                    require(16 <= p["x"] and p["x"] + p["w"] + 16 <= length, place, "Mover oscillation leaves room bounds.")
                    stable_neighbours = [q for q in platforms if q["kind"] in (0, 1) and abs(q["y"] - p["y"]) <= 32 and platform_gap(p, q) <= 64]
                    require(len(stable_neighbours) >= 2, place, "Mover needs stable nearby launch and catch surfaces.")
            for index, p in enumerate(pickups):
                require(p["kind"] in range(3) and 0 <= p["x"] < length and 8 <= p["y"] <= 120, f"{where}, pickup {index}", "Invalid pickup type or position.")
            pickup_buckets = Counter(p["x"] // 64 for p in pickups)
            require(max(pickup_buckets.values(), default=0) <= 8, where, "A 64-pixel pickup bucket exceeds the engine's eight-entry capacity.")
            seal_indices = {i for i, p in enumerate(pickups) if p["kind"] == 2}
            total_seals += len(seal_indices)
            require(len(seal_indices) == 3, where, "Every room must have exactly three optional seals.")
            for index, e in enumerate(enemies):
                require(e["kind"] in range(4) and 0 <= e["range"] <= 64 and 16 <= e["x"] - e["range"] and e["x"] + e["range"] + 16 <= length and 16 <= e["y"] <= 112, f"{where}, enemy {index}", "Enemy patrol or sprite is outside room bounds.")
                jellies += e["kind"] == 3
            main = room.get("main_route", [])
            require(len(main) >= 8 and len(set(main)) == len(main) and all(0 <= i < len(platforms) for i in main), where, "Main path needs valid ordered unique platform indices.")
            if not main or any(i >= len(platforms) for i in main):
                continue
            for a_index, b_index in zip(main, main[1:]):
                a, b = platforms[a_index], platforms[b_index]
                dynamic_gap = platform_gap(a, b) + 16 * ((a["kind"] == 4) + (b["kind"] == 4))
                require(b["x"] >= a["x"], where, "Main path should flow forward.")
                transfer = any(encounter.get("kind") == "lantern_transfer" and encounter.get("platform_indices") == [a_index, b_index] for encounter in room.get("movement_encounters", []))
                require(dynamic_gap <= (104 if room.get("original_first_room") or transfer else 72) and a["y"] - b["y"] <= 32, where, f"Main transition {a_index}->{b_index} exceeds conservative jump geometry.")
                if not room.get("original_first_room"):
                    taught_spring = any(encounter.get("kind") == "spring_arc" and b_index in encounter.get("platform_indices", []) for encounter in room.get("movement_encounters", []))
                    require(b["kind"] != 3 and (b["kind"] != 2 or taught_spring), where, "New spring encounters need explicit teaching and stable catches; crumble belongs to optional paths.")
                    if b["kind"] in (2, 4) or transfer:
                        risks.append({"stage": stage_id, "room": room_id, "route": "main", "from": a_index, "to": b_index, "gap": dynamic_gap, "rise": a["y"] - b["y"], "reason": "Authored spring arc, moving ride, or lantern transfer with nearby stable catches."})
                elif b["kind"] in (2, 3) or dynamic_gap > 72:
                    risks.append({"stage": stage_id, "room": room_id, "route": "main", "from": a_index, "to": b_index, "gap": dynamic_gap, "rise": a["y"] - b["y"], "reason": "Preserved v1 timing-sensitive encounter; reverify in expanded engine."})
            final = platforms[main[-1]]
            require(final["kind"] == 0 and final["w"] >= 160 and final["x"] + final["w"] == length and final["y"] == room.get("goal_y"), where, "Goal needs a broad stable final catch shelf.")
            require(length - 64 <= room.get("goal_x", 0) <= length - 24, where, "Goal must be near the final catch shelf interior.")
            start = platforms[main[0]]
            require(start["x"] <= room.get("spawn_x", -1) <= start["x"] + start["w"] - 16 and room.get("spawn_y") + 16 == start["y"], where, "Spawn must rest on the initial platform.")
            cp_index = room.get("checkpoint_platform_index", -1)
            require(cp_index in main and platforms[cp_index]["kind"] in (0, 1), where, "Checkpoint requires a stable main-route surface.")
            if cp_index in main:
                cp = platforms[cp_index]
                require(cp["x"] + 16 <= room.get("checkpoint_x", -1) <= cp["x"] + cp["w"] - 16 and room.get("checkpoint_y") == cp["y"], where, "Checkpoint is too close to an edge or uses wrong feet height.")
                if room.get("boss"):
                    require(80 <= room["goal_x"] - room["checkpoint_x"] <= 320, where, "Boss checkpoint must be close to combat.")
                else:
                    require(.35 <= room["checkpoint_x"] / length <= .72, where, "Checkpoint is not useful around the middle of the room.")
            branches = room.get("seal_routes", [])
            require(len(branches) == 3 and {b.get("seal_pickup_index") for b in branches} == seal_indices, where, "All three seals require complete route annotations.")
            long_forks = 0
            for branch in branches:
                path = branch.get("platform_indices", [])
                entry = branch.get("entry_main_platform", -1)
                rejoin = branch.get("rejoin_main_platform", -1)
                require(path and all(0 <= i < len(platforms) for i in path) and entry in main and rejoin in main and rejoin > entry, where, "Discovery path has invalid platforms, entry, or forward rejoin.")
                if not path or any(i >= len(platforms) for i in path) or entry not in main or rejoin not in main:
                    continue
                seal_platform = branch.get("seal_platform_index", path[-1])
                require(seal_platform in path, where, "Seal surface is absent from discovery path.")
                if branch.get("route_style") != "grotto" and not room.get("original_first_room"):
                    for order, index in enumerate(path):
                        target = platforms[index]
                        overhangs = [platforms[k] for k in main + path[:order]
                                     if platforms[k]["y"] < target["y"]
                                     and platforms[k]["x"] <= target["x"]
                                     and platforms[k]["x"] + platforms[k]["w"] >= target["x"] + target["w"]]
                        require(not overhangs, where, f"Scenic surface {index} is completely occluded by a higher floor.")
                seal = pickups[branch["seal_pickup_index"]]
                landing = platforms[seal_platform]
                require(landing["x"] - 8 <= seal["x"] <= landing["x"] + landing["w"] and abs(seal["y"] + 24 - landing["y"]) <= 16, where, "Seal clue is not adjacent to its annotated surface.")
                sequence = [entry] + path + [rejoin]
                for a_index, b_index in zip(sequence, sequence[1:]):
                    a, b = platforms[a_index], platforms[b_index]
                    gap = platform_gap(a, b) + 16 * ((a["kind"] == 4) + (b["kind"] == 4))
                    rise = a["y"] - b["y"]
                    limit = 88 if a["kind"] == 2 else 56
                    require(rise <= limit and gap <= 104, where, f"Discovery transition {a_index}->{b_index} exceeds conservative geometry.")
                    if gap > 64 or rise > 40 or a["kind"] in (2, 3, 4) or b["kind"] == 4:
                        risks.append({"stage": stage_id, "room": room_id, "route": branch.get("seal"), "from": a_index, "to": b_index, "gap": gap, "rise": rise, "reason": "Needs controller verification with spring/crumble/mover timing or a long jump."})
                span = max(platforms[i]["x"] + platforms[i]["w"] for i in path) - min(platforms[i]["x"] for i in path)
                if len(path) >= 4 and span >= 280:
                    long_forks += 1
                if not room.get("original_first_room"):
                    require(bool(branch.get("landmark")) and bool(branch.get("clue")) and bool(branch.get("choice")) and bool(branch.get("return")), where, "New discovery paths need landmarks, clues, choices, and returns.")
            if not room.get("original_first_room"):
                require(room.get("exploration_focus") and len(room.get("landmarks", [])) >= 3 and long_forks >= 2, where, "Every new room needs two substantial discovery forks and a third pocket.")
                substantial_forks += long_forks
                shape = tuple((platforms[i]["x"], platforms[i]["y"], platforms[i]["w"], platforms[i]["kind"]) for i in main)
                require(shape not in new_main_shapes, where, f"Ground phrase duplicates {new_main_shapes.get(shape)}.")
                new_main_shapes[shape] = where
            for junction in room.get("junction_routes", []):
                sequence = [junction.get("from_platform", -1)] + junction.get("platform_indices", []) + [junction.get("to_platform", -1)]
                require(len(sequence) >= 3 and all(0 <= i < len(platforms) for i in sequence), where, "Roof junction needs valid entry, bridge, and exit surfaces.")
                if any(i < 0 or i >= len(platforms) for i in sequence):
                    continue
                require(junction.get("optional") and junction.get("clue") and junction.get("stable_catch_platform_indices"), where, "Roof junction needs readable clues and stable lower catches.")
                clues = junction.get("clue_pickup_indices", [])
                require(clues and all(0 <= i < len(pickups) and pickups[i]["kind"] != 2 for i in clues), where, "Roof junction clues must be valid optional stars/lanterns.")
                for a_index, b_index in zip(sequence, sequence[1:]):
                    a, b = platforms[a_index], platforms[b_index]
                    require(platform_gap(a, b) <= 72 and abs(a["y"] - b["y"]) <= 32, where, f"Roof junction transition {a_index}->{b_index} exceeds forgiving bidirectional geometry.")
            if room.get("boss"):
                arena = room.get("arena", {})
                require(arena.get("boss_type") == room["boss"] and arena.get("end_x") == length and arena.get("floor_y") == 128, where, "Boss arena annotation is incomplete.")
                require(all(pickups[i]["x"] < arena.get("start_x", 0) for i in seal_indices), where, "Boss seals must precede the combat apron.")
                require(all(e["x"] < arena.get("start_x", 0) for e in enemies), where, "Ordinary enemies must stay outside the boss apron.")
                floor = sorted((p["x"], p["x"] + p["w"]) for p in platforms if p["kind"] == 0 and p["y"] == 128 and p["x"] >= arena.get("start_x", length))
                require(bool(floor) and floor[0][0] == arena.get("start_x") and floor[-1][1] == length and all(a[1] == b[0] for a, b in zip(floor, floor[1:])), where, "Combat apron floor must be continuous.")
    require(room_count == 72 and total_seals == 216, "Campaign", "Expected 72 rooms and 216 optional seals.")
    require(movers > 0 and jellies > 0 and wind_rooms > 0, "Campaign", "Expansion must include movers, jelly encounters, and signposted wind.")
    if errors:
        raise ValueError("\n".join(errors))
    return {"stages": len(stages), "worlds": 8, "rooms": room_count, "seals": total_seals,
            "world_pixels": total_length, "new_substantial_forks": substantial_forks,
            "moving_platforms": movers, "jelly_encounters": jellies, "wind_rooms": wind_rooms,
            "controller_reachability_risks": risks,
            "duration_target_minutes": data.get("first_journey_target_minutes"),
            "duration_is_measured": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the complete geometry report including controller risks.")
    options = parser.parse_args()
    try:
        report = validate_campaign(json.loads(ROUTES_PATH.read_text()))
    except (KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, f"Campaign validation failed:\n{error}\n")
    if options.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Campaign valid: {report['stages']} stages, {report['rooms']} rooms, {report['seals']} seals, {report['world_pixels']} pixels.")
        print(f"Exploration: {report['new_substantial_forks']} substantial forks; {report['moving_platforms']} movers; {report['jelly_encounters']} jellies; {report['wind_rooms']} wind rooms.")
        print(f"Controller verification required for {len(report['controller_reachability_risks'])} timing-sensitive transitions; duration remains an unmeasured 60–90 minute first-player target.")


if __name__ == "__main__":
    main()
