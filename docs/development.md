# Development

Use GBDK-2020 4.5.0, Python 3.12, and Make. `make GBDK=/path/to/gbdk` builds from the checked-in C graphics. `PYTHON` defaults to `python3` and can point to a virtual environment. `GBDK` defaults to `/opt/gbdk`; set it as a Make argument or environment variable. The music renderer reads the same environment variable.

Install optional dependencies as described in the README. Then run:

```sh
make check GBDK=/path/to/gbdk PYTHON=.venv/bin/python
.venv/bin/python tools/build_art.py --check
.venv/bin/python tools/render_teaser.py --check-only
```

The campaign planner branches controller-earned emulator states to find routes, then performs a second linear replay from blank SRAM without loading states or writing running-game RAM. Local earned saves and snapshots stay in ignored `build/`; do not commit them.

Independent expansion checks:

```sh
GBDK=/path/to/gbdk .venv/bin/python tools/check_expansion_save.py
.venv/bin/python tools/check_expansion_runtime.py
.venv/bin/python tools/build_campaign.py --check
.venv/bin/python tools/check_campaign.py
```

The save harness compiles the exact production save source and injects explicitly labeled cartridge fixtures before boot. It checks migration, resume fields, CRC recovery, sequence wrap, reset, and legacy-byte preservation; it does not claim fixtures were earned by gameplay. Runtime probes and the campaign planner use controller inputs. The original `critic_play.py` and v1 reports are historical tools tied to the original release, and should be consulted under the v1.0.0 tag. Subjective enjoyment and first-player timing still need human assessment.

## Assets and media

`make assets PYTHON=.venv/bin/python` regenerates C graphics and previews from bundled paintings/font data. `tools/build_art.py --check` decodes C data and validates palettes, tiles, sprites, font coverage, and seams. See [art.md](art.md).

`GBDK=/path/to/gbdk .venv/bin/python tools/render_music.py` compiles a harness against the production sequencer and captures the emulated APU; see [soundtrack.md](soundtrack.md).

`tools/render_teaser.py` replays the campaign recording on its matching ROM. A changed ROM needs a new passing recording before capturing a teaser. Screenshots show actual ROM pixels with nearest-neighbor scaling.

## Runtime organization

Bank 0 hosts startup, the main loop, and shared primitives; 1–2 graphics/title; 3 levels; 4 gameplay; 5 menus; 6 saves; 7 APU; 8–15 panoramas; 16–23 per-world campaign data. See [design.md](design.md), [routes.json](routes.json), and [art.md](art.md) before changing data contracts.

The Long Dawn uses CRC-protected 192-byte SRAM slots at `A200` and `A300`, plus a committed generation marker at `A3F0`–`A3F3`. Original Moonwake v1 slots at `A100`/`A180` and Signal Bloom slots remain untouched. Migration carries forward old unlocks and first-section discoveries but clears times/ranks for the longer courses. Each stage stores nine seal bits and the active section/checkpoint; a 32-bit counter tracks active journey time. Compiler changes can change bytes even without gameplay changes.
