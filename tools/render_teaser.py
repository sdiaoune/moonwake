"""Render an honest teaser from a fresh replay of verified joypad inputs.

The ROM must match dist/verified-inputs.json. The recording is replayed from
blank cartridge RAM, without snapshots, memory writes, or custom game inputs.
Frames are captured at 160 x 144 and enlarged threefold with nearest sampling.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = ROOT / "dist/moonwake.gbc"
TRACE_PATH = ROOT / "dist/verified-inputs.json"
OUTPUT_DIRECTORY = ROOT / "docs/screenshots"
GIF_PATH = OUTPUT_DIRECTORY / "moonwake-teaser.gif"
MANIFEST_PATH = OUTPUT_DIRECTORY / "teaser-manifest.json"
TARGET_STAGES = (0, 3, 6, 9)
STAGE_LABELS = {
    0: "Lantern Quay",
    3: "Lotus After Rain",
    6: "Brass Moonworks",
    9: "Whale in the Sky",
}
NATIVE_SIZE = (160, 144)
DISPLAY_SIZE = (480, 432)
EMULATOR_FPS = 60
FRAME_STRIDE = 3
GIF_FRAME_MS = 50
TITLE_START = 120
TITLE_FRAMES = 48
GAMEPLAY_FRAMES = 120
ALLOWED_BUTTONS = frozenset(("a", "b", "start", "select", "up", "down", "left", "right"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_verified_source() -> tuple[bytes, bytes, bytes, dict]:
    rom_bytes = ROM_PATH.read_bytes()
    symbol_bytes = ROM_PATH.with_suffix(".sym").read_bytes()
    trace_bytes = TRACE_PATH.read_bytes()
    recording = json.loads(trace_bytes)
    actual_hash = sha256(rom_bytes)
    if recording.get("rom_sha256") != actual_hash:
        raise ValueError(
            "The controller recording belongs to a different ROM. "
            f"Recording: {recording.get('rom_sha256')}; ROM: {actual_hash}. "
            "Finish the final controller verification before rendering."
        )
    inputs = recording.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("The verified recording contains no controller inputs.")
    total_frames = 0
    for entry in inputs:
        if not isinstance(entry, list) or len(entry) != 2:
            raise ValueError(f"Malformed controller entry: {entry!r}")
        count, buttons = entry
        if type(count) is not int or count <= 0:
            raise ValueError(f"Invalid frame count: {count!r}")
        if not isinstance(buttons, list) or any(button not in ALLOWED_BUTTONS for button in buttons):
            raise ValueError(f"Invalid joypad buttons: {buttons!r}")
        total_frames += count
    if recording.get("frames") != total_frames:
        raise ValueError("The recorded frame total does not match the controller entries.")
    return rom_bytes, symbol_bytes, trace_bytes, recording


def load_tester(snapshot_directory: Path):
    # Snapshot inputs and symbols prevent a concurrent rebuild from changing
    # the capture halfway through. This copies files, never emulator state.
    spec = importlib.util.spec_from_file_location("moonwake_teaser_playtest", ROOT / "tools/playtest.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the native controller tester.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROM = snapshot_directory / "moonwake.gbc"
    symbols = {}
    for line in module.ROM.with_suffix(".sym").read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and ":" in parts[0]:
            bank, address = parts[0].split(":")
            symbols[parts[1]] = (int(bank, 16), int(address, 16))
    module.SYMS = symbols
    return module.Tester, symbols


def capture_frame(tester) -> Image.Image:
    frame = tester.p.screen.image.copy().convert("RGB")
    if frame.size != NATIVE_SIZE:
        raise ValueError(f"Unexpected native frame size: {frame.size!r}")
    frame = frame.resize(DISPLAY_SIZE, Image.Resampling.NEAREST)
    return frame.quantize(colors=256, dither=Image.Dither.NONE)


def clip(label: str, frame_start: int, frame_count: int, state: dict) -> dict:
    return {
        "label": label,
        "source_start_frame": frame_start,
        "source_end_frame": frame_start + frame_count - 1,
        "source_frame_count": frame_count,
        "sampled_source_frames": [],
        "start_state": state,
        "images": [],
    }


def capture(recording: dict, tester_class, symbols: dict) -> tuple[list[Image.Image], list[dict], dict]:
    tester = tester_class()
    clips = []
    current_clip = None
    seen_stages = set()
    captured_boss = False
    try:
        for count, buttons in recording["inputs"]:
            for _ in range(count):
                tester.tick(1, buttons)
                state = tester.state()
                frame_number = tester.frames
                if current_clip is not None and frame_number > current_clip["source_end_frame"]:
                    clips.append(current_clip)
                    print(f"Captured {current_clip['label']} at source frame {current_clip['source_start_frame']}", flush=True)
                    current_clip = None

                if current_clip is None:
                    if frame_number == TITLE_START:
                        if state["game_mode"] != 0:
                            raise AssertionError("The recorded title window is not the title screen.")
                        current_clip = clip("Title", frame_number, TITLE_FRAMES, state)
                    elif state["game_mode"] == 1:
                        stage_id = state["stage_id"]
                        # Start once the recording approaches its first upper
                        # route, rather than spending the excerpt standing at
                        # spawn. Input remains exactly the verified recording.
                        if stage_id in TARGET_STAGES and stage_id not in seen_stages and state["x"] >= 160:
                            current_clip = clip(STAGE_LABELS[stage_id], frame_number, GAMEPLAY_FRAMES, state)
                            seen_stages.add(stage_id)
                        elif stage_id == 11 and not captured_boss and state["x"] >= 1620 and tester.read("boss_hp"):
                            current_clip = clip("Heart of Moonwake: dream knot", frame_number, GAMEPLAY_FRAMES, state)
                            captured_boss = True

                if current_clip is not None and frame_number <= current_clip["source_end_frame"]:
                    current_clip["end_state"] = state
                    if current_clip["label"] != "Title":
                        if state["game_mode"] != 1 or state["stage_id"] != current_clip["start_state"]["stage_id"]:
                            raise AssertionError(f"The excerpt left its stage: {current_clip['label']}")
                    if (frame_number - current_clip["source_start_frame"]) % FRAME_STRIDE == 0:
                        current_clip["images"].append(capture_frame(tester))
                        current_clip["sampled_source_frames"].append(frame_number)

        if current_clip is not None:
            raise AssertionError(f"The recording ended before the {current_clip['label']} excerpt finished.")
        if seen_stages != set(TARGET_STAGES) or not captured_boss or len(clips) != 6:
            raise AssertionError("The fresh recording did not provide all six required excerpts.")
        final_state = tester.state()
        if not tester.read("completed") or final_state["game_mode"] != 6:
            raise AssertionError(f"The fresh controller replay did not reach the ending: {final_state!r}")
        seal_address = tester.p.memory
        # Read-only verification of the completion earned by this replay.
        if any(seal_address[symbols["_seal_bits"][1] + stage_id] != 7 for stage_id in range(12)):
            raise AssertionError("The fresh controller replay did not earn all 36 moon seals.")
        images = []
        metadata = []
        for excerpt in clips:
            images.extend(excerpt.pop("images"))
            excerpt["output_duration_ms"] = len(excerpt["sampled_source_frames"]) * GIF_FRAME_MS
            metadata.append(excerpt)
        return images, metadata, final_state
    finally:
        tester.close()


def render() -> None:
    rom_bytes, symbol_bytes, trace_bytes, recording = read_verified_source()
    with tempfile.TemporaryDirectory(prefix="moonwake-teaser-") as temporary:
        snapshot_directory = Path(temporary)
        (snapshot_directory / "moonwake.gbc").write_bytes(rom_bytes)
        (snapshot_directory / "moonwake.sym").write_bytes(symbol_bytes)
        tester_class, symbols = load_tester(snapshot_directory)
        frames, excerpts, final_state = capture(recording, tester_class, symbols)
        # Do not publish footage if the caller rebuilt the source during replay.
        if sha256(ROM_PATH.read_bytes()) != recording["rom_sha256"] or TRACE_PATH.read_bytes() != trace_bytes:
            raise RuntimeError("The ROM or controller recording changed during capture; rerun after verification.")
        temporary_gif = snapshot_directory / "moonwake-teaser.gif"
        frames[0].save(
            temporary_gif,
            save_all=True,
            append_images=frames[1:],
            duration=GIF_FRAME_MS,
            loop=0,
            disposal=2,
            optimize=False,
        )
        gif_bytes = temporary_gif.read_bytes()
        with Image.open(temporary_gif) as encoded_gif:
            encoded_frame_count = encoded_gif.n_frames
            encoded_duration_ms = 0
            for frame_index in range(encoded_frame_count):
                encoded_gif.seek(frame_index)
                encoded_duration_ms += encoded_gif.info.get("duration", 0)
        if encoded_duration_ms != len(frames) * GIF_FRAME_MS:
            raise RuntimeError("The encoded GIF duration differs from the native capture timeline.")
        manifest = {
            "game": "Moonwake",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "rom_sha256": recording["rom_sha256"],
            "symbols_sha256": sha256(symbol_bytes),
            "controller_recording": "dist/verified-inputs.json",
            "controller_recording_sha256": sha256(trace_bytes),
            "controller_replay_frames": recording["frames"],
            "provenance": "Fresh PyBoy CGB emulator; blank 8192-byte cartridge RAM; exact verified joypad inputs replayed linearly from power-on; no snapshots, memory writes, teleports, scripted substitutes, or composited gameplay.",
            "native_frame_size": list(NATIVE_SIZE),
            "output_frame_size": list(DISPLAY_SIZE),
            "scaling": "3x nearest neighbor",
            "emulator_frames_per_second": EMULATOR_FPS,
            "sample_stride_frames": FRAME_STRIDE,
            "gif_frame_duration_ms": GIF_FRAME_MS,
            "sampled_frame_count": len(frames),
            "gif_encoded_frame_count": encoded_frame_count,
            "gif_duration_ms": encoded_duration_ms,
            "gif_sha256": sha256(gif_bytes),
            "all_stages_completed_by_fresh_replay": True,
            "all_36_seals_earned_by_fresh_replay": True,
            "final_replay_state": final_state,
            "excerpts": excerpts,
        }
        OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        GIF_PATH.write_bytes(gif_bytes)
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Saved {GIF_PATH} ({len(frames)} frames; {len(frames) * GIF_FRAME_MS / 1000:.1f} seconds).", flush=True)
        print(f"ROM SHA-256: {recording['rom_sha256']}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Validate the matching ROM and input recording without replaying.")
    options = parser.parse_args()
    try:
        if options.check_only:
            _, _, _, recording = read_verified_source()
            print(f"Verified source SHA-256: {recording['rom_sha256']}")
        else:
            render()
    except (AssertionError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Teaser capture stopped: {error}\n")


if __name__ == "__main__":
    main()
