# Development

Use GBDK-2020 4.5.0, Python 3.12, and Make. `make GBDK=/path/to/gbdk` builds from the checked-in C graphics. `PYTHON` defaults to `python3` and can point to a virtual environment. `GBDK` defaults to `/opt/gbdk`; set it as a Make argument or environment variable. The music renderer reads the same environment variable.

Install optional dependencies as described in the README. Then run:

```sh
make check GBDK=/path/to/gbdk PYTHON=.venv/bin/python
.venv/bin/python tools/build_art.py --check
.venv/bin/python tools/render_teaser.py --check-only
```

The campaign planner branches controller-earned emulator states to find routes, then performs a second linear replay from blank SRAM without loading states or writing running-game RAM. Local earned saves and snapshots stay in ignored `build/`; do not commit them.

Optional critic probes, in dependency order:

```sh
.venv/bin/python tools/critic_play.py
.venv/bin/python tools/critic_play.py --ui
.venv/bin/python tools/critic_play.py --rank
.venv/bin/python tools/critic_play.py --lantern
.venv/bin/python tools/critic_play.py --arena
.venv/bin/python tools/critic_play.py --replay
```

Run the base critic before `--ui`, `--rank` before `--lantern`, and the campaign check before `--arena`. `--replay` checks the distributed controller recording and save recovery. These are technical checks; aesthetics and player enjoyment require human assessment.

## Assets and media

`make assets PYTHON=.venv/bin/python` regenerates C graphics and previews from bundled paintings/font data. `tools/build_art.py --check` decodes C data and validates palettes, tiles, sprites, font coverage, and seams. See [art.md](art.md).

`GBDK=/path/to/gbdk .venv/bin/python tools/render_music.py` compiles a harness against the production sequencer and captures the emulated APU; see [soundtrack.md](soundtrack.md).

`tools/render_teaser.py` replays the campaign recording on its matching ROM. A changed ROM needs a new passing recording before capturing a teaser. Screenshots show actual ROM pixels with nearest-neighbor scaling.

## Runtime organization

Bank 0 hosts startup, the main loop, and shared primitives; 1–2 graphics/title; 3 levels; 4 gameplay; 5 menus; 6 saves; 7 APU; 8–11 panoramas. See [design.md](design.md), [routes.json](routes.json), and [art.md](art.md) before changing data contracts.

Moonwake uses two CRC-protected 64-byte SRAM slots at `A100` and `A180`, with a dedicated signature. The release was rebuilt on macOS ARM64 with GBDK 4.5.0 and matched the installed ROM byte-for-byte. Compiler changes can change bytes even without gameplay changes.
