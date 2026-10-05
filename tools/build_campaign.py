"""Compile the canonical authored routes into native banked campaign data.

Edit docs/routes.json to change a room, then run this tool. --check verifies
that the checked-in C data still matches the canonical campaign exactly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_campaign import validate_campaign

ROOT = Path(__file__).resolve().parents[1]


def array(name: str, c_type: str, objects: list[dict], fields: tuple[str, ...]) -> list[str]:
    lines = [f"static const {c_type} {name}[] = {{"]
    for item in objects:
        values = ", ".join(f"{item[field]}u" for field in fields)
        lines.append(f"    {{{values}}},")
    return lines + ["};", ""]


def world_source(world: int, stages: list[dict]) -> str:
    rooms = [room for stage in stages for room in stage["rooms"]]
    lines = ["/* Generated from docs/routes.json by tools/build_campaign.py. */",
             f"/* {stages[0]['world_name']}: three stages, nine continuous rooms. */",
             f"#pragma bank {16 + world}", '#include "levels.h"', "#include <string.h>", ""]
    for index, room in enumerate(rooms):
        lines.append(f"/* Stage {room['id'] + 1}, room {room['room_id'] + 1}: {room['name']}. */")
        lines.extend(array(f"platforms_{index}", "PlatformDef", room["platforms"], ("x", "y", "w", "kind")))
        lines.extend(array(f"pickups_{index}", "PickupDef", room["pickups"], ("x", "y", "kind")))
        lines.extend(array(f"enemies_{index}", "EnemyDef", room["enemies"], ("x", "y", "range", "kind")))
    lines.append("static const LevelDef definitions[9] = {")
    for room in rooms:
        values = [room[field] for field in ("length", "spawn_x", "goal_x", "checkpoint_x", "biome", "spawn_y", "goal_y", "checkpoint_y", "boss")]
        values.extend(len(room[group]) for group in ("platforms", "pickups", "enemies"))
        values.append(room["mechanic"])
        lines.append("    {" + json.dumps(room["name"]) + ", " + ", ".join(f"{value}u" for value in values) + "},")
    lines.extend(["};", ""])
    for c_type, symbol in (("PlatformDef", "platforms"), ("PickupDef", "pickups"), ("EnemyDef", "enemies")):
        lines.extend([f"static const {c_type} * const {symbol}_sets[9] = {{",
                      "    " + ", ".join(f"{symbol}_{index}" for index in range(9)), "};", ""])
    lines.append("static const char intros[9][3][21] = {")
    for room in rooms:
        lines.append("    {" + ", ".join(json.dumps(line) for line in room["intro"]) + "},")
    lines.extend(["};", "", "static const uint16_t pars[3] = {",
                  "    " + ", ".join(f"{stage['par_seconds']}u" for stage in stages), "};", "",
                  "static uint8_t room_index(uint8_t local_stage, uint8_t room) {",
                  "    if (local_stage >= 3u) local_stage = 0u;",
                  "    if (room >= ROOMS_PER_STAGE) room = 0u;",
                  "    return local_stage * ROOMS_PER_STAGE + room;", "}", "",
                  f"void campaign_{world}_load(uint8_t local_stage, uint8_t room, LevelDef *out,",
                  "                       PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {",
                  "    uint8_t index = room_index(local_stage, room);",
                  "    memcpy(out, &definitions[index], sizeof(LevelDef));",
                  "    memcpy(plats, platforms_sets[index], (uint16_t)out->platform_count * sizeof(PlatformDef));",
                  "    memcpy(picks, pickups_sets[index], (uint16_t)out->pickup_count * sizeof(PickupDef));",
                  "    memcpy(enemies, enemies_sets[index], (uint16_t)out->enemy_count * sizeof(EnemyDef));", "}", "",
                  f"void campaign_{world}_info(uint8_t local_stage, LevelDef *out) BANKED {{",
                  "    memcpy(out, &definitions[room_index(local_stage, 0u)], sizeof(LevelDef));", "}", "",
                  f"void campaign_{world}_intro(uint8_t local_stage, uint8_t room, char *line1,",
                  "                        char *line2, char *line3) BANKED {",
                  "    uint8_t index = room_index(local_stage, room);",
                  "    strcpy(line1, intros[index][0]);",
                  "    strcpy(line2, intros[index][1]);",
                  "    strcpy(line3, intros[index][2]);", "}", "",
                  f"uint16_t campaign_{world}_par(uint8_t local_stage) BANKED {{",
                  "    if (local_stage >= 3u) local_stage = 0u;",
                  "    return pars[local_stage];", "}", ""])
    return "\n".join(lines)


def dispatch_lines(api: str, arguments: str, returns: bool = False) -> list[str]:
    lines = ["    if (id >= LEVEL_COUNT) id = 0u;", "    switch (id / 3u) {"]
    for world in range(8):
        invocation = f"campaign_{world}_{api}(id % 3u, {arguments})" if arguments else f"campaign_{world}_{api}(id % 3u)"
        if returns:
            lines.append(f"        case {world}u: return {invocation};")
        else:
            lines.append(f"        case {world}u: {invocation}; break;")
    lines.append("    }")
    if returns:
        lines.append("    return 0u;")
    return lines


def dispatcher_source() -> str:
    lines = ["/* Generated campaign dispatcher. Content stays in its active bank. */",
             "#pragma bank 3", '#include "levels.h"', "#include <string.h>", "",
             "void level_load(uint8_t id, LevelDef *out, PlatformDef *plats,",
             "                PickupDef *picks, EnemyDef *enemies) BANKED {",
             "    level_load_room(id, 0u, out, plats, picks, enemies);", "}", "",
             "void level_load_room(uint8_t id, uint8_t room, LevelDef *out,",
             "                     PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {",
             "    if (room >= ROOMS_PER_STAGE) room = 0u;"]
    lines.extend(dispatch_lines("load", "room, out, plats, picks, enemies"))
    lines.extend(["}", "", "void level_info(uint8_t id, LevelDef *out) BANKED {"])
    lines.extend(dispatch_lines("info", "out"))
    lines.extend(["}", "", "void level_intro(uint8_t id, char *line1, char *line2, char *line3) BANKED {",
                  "    level_intro_room(id, 0u, line1, line2, line3);", "}", "",
                  "void level_intro_room(uint8_t id, uint8_t room, char *line1,",
                  "                      char *line2, char *line3) BANKED {",
                  "    if (room >= ROOMS_PER_STAGE) room = 0u;"])
    lines.extend(dispatch_lines("intro", "room, line1, line2, line3"))
    lines.extend(["}", "", "uint16_t level_par(uint8_t id) BANKED {"])
    lines.extend(dispatch_lines("par", "", returns=True))
    lines.extend(["}", "", "void level_outro(char *line1, char *line2, char *line3) BANKED {",
                  '    strcpy(line1, "THE LONG DAWN RISES.");',
                  '    strcpy(line2, "THE SKY SEA SINGS.");',
                  '    strcpy(line3, "KIP BRINGS IT HOME.");', "}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate routes and verify exact generated native sources.")
    options = parser.parse_args()
    try:
        data = json.loads((ROOT / "docs/routes.json").read_text())
        report = validate_campaign(data)
        outputs = {ROOT / "src/levels.c": dispatcher_source()}
        for world in range(8):
            outputs[ROOT / f"src/campaign_{world}.c"] = world_source(world, data["levels"][world * 3:world * 3 + 3])
        for path, source in outputs.items():
            if options.check:
                if not path.exists() or path.read_text() != source:
                    raise ValueError(f"Generated content differs: {path}. Run tools/build_campaign.py.")
            else:
                path.write_text(source)
    except (KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, f"Campaign build failed:\n{error}\n")
    action = "Verified" if options.check else "Generated"
    print(f"{action} bank 3 dispatcher and eight campaign banks for {report['rooms']} authored rooms.")


if __name__ == "__main__":
    main()
