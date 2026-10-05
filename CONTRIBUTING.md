# Contributing to Moonwake

Open an issue with a reproducible bug, gameplay suggestion, or proposed feature. For bugs, include the ROM version, emulator or hardware, stage, and buttons that led to the problem. Keep cartridge saves and personal backups private.

Fork the repository, create a branch, and open a pull request describing the player-visible result and how you checked it. Contributions use the license applying to the files you modify: MIT for code/tools/docs, CC BY 4.0 for original art/music, and the existing license for third-party files.

Build with GBDK-2020 4.5.0. After engine or stage changes, run `make check` with test dependencies installed. After art changes, regenerate assets, run `tools/build_art.py --check`, and rebuild. See the [development guide](docs/development.md).

Keep the native 160 × 144 screen readable. Preserve four colors per tile, allocated palette/tile banks, clear collision edges, and a distinct hero silhouette. Routes should be reachable through normal controller input. Music should preserve the lead while effects borrow the countervoice.

Commit source and generated outputs together. Capture fresh evidence after behavior changes; existing recordings belong to the ROM hashes in their reports. Agent review scores are development feedback, not human playtest ratings.
