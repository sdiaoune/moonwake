# Licensing and third-party notices

## Moonwake

Copyright © 2026 sdiaoune. Native game code, tools, and documentation are MIT licensed; see `LICENSE`.

Original artwork, sprite/font/tile data (including C-encoded data), musical compositions and score data, PNG/GIF screenshots, and WAV captures are CC BY 4.0; see `LICENSE-ASSETS`. This includes `assets/`, `docs/screenshots/`, `docs/audio/`, graphic data in `src/art_data.c`, `src/title_art.c`, and `src/world_*.c`, and original music data in `src/music.c`. Sequencer and rendering code remain MIT. Suggested attribution: **Moonwake by sdiaoune — https://github.com/sdiaoune/moonwake — CC BY 4.0**. Identify modifications when sharing adaptations.

Scene paintings were generated with OpenAI image generation and converted into native tiles by the included pipeline. Prompts and source paintings are included. The font foundation originates in the creator's Signal Bloom project. See `docs/art.md`.

## WasmBoy 0.7.1

`docs/vendor/wasmboy.js` is by Aaron Turner and the WasmBoy contributors, licensed **GPL-3.0-or-later**. Its license is in `docs/vendor/wasmboy-LICENSE`; this emulator is not covered by Moonwake's MIT license. The bundle is byte-identical to `dist/wasmboy.wasm.umd.js` from npm `wasmboy@0.7.1`.

Upstream: https://github.com/torch2424/wasmboy/tree/v0.7.1

Commit: `8e96bcb70969d943b1ffc4028b169c835098ce04`.

Corresponding emulator source/build files are in `docs/vendor/wasmboy-0.7.1-source.tar.gz`; production dependency sources are in `docs/vendor/wasmboy-dependencies/`. See `docs/vendor/README.md` for provenance and rebuilding. Unrelated upstream demo media and test ROMs are excluded.

## GBDK-2020 / SDCC runtime

Moonwake is compiled with GBDK-2020 4.5.0 and links its standard runtime libraries. Their GPL v2 license includes a linking exception permitting separately licensed executables. Notices are preserved in `docs/vendor/gbdk-LICENSE_GPLV2_LE` and `docs/vendor/gbdk-LICENSE_SDCC`.

Source/release: https://github.com/gbdk-2020/gbdk-2020/tree/4.5.0

Runtime sources are included in `docs/vendor/gbdk-4.5.0-source.tar.gz`. Compiler binaries are not distributed here. Platform names and boot-header identification data retain their respective owners' rights; no Nintendo or ModRetro affiliation is implied.
