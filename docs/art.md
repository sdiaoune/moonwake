# Moonwake art: sky-sea postcards on native Game Boy Color

Moonwake's visual identity is Kip, a cream moon hare whose persimmon scarf echoes
comet tails, lantern tassels and whale flukes. Warm pearl highlights connect four
worlds: peach pagoda islands, a monumental celadon lotus, violet brass astronomy,
and a sleeping cyan sky whale. The hero is hand-authored at 16x16 with a persistent
one-pixel shadow silhouette, cream body and red scarf. All six poses use the same
readable face, ears and proportions. Dash compresses the body and lays the ears
back; running alternates two leg silhouettes; jumping tucks the legs.

The built-in imagegen tool produced the original key visual and four scenery
paintings. All five original PNGs are preserved in `assets/source`, together with
the exact prompt set in `imagegen-prompts.json`. These paintings are production
inputs and promotional art, not emulator screenshots. `tools/build_art.py` reduces
the panorama inputs once to 256x144, fits six local four-color RGB555 palettes,
shares flipped tile patterns and merges only the nearest patterns as necessary
to fit 304 scenery tiles. The title uses the whale source in a compact composition,
with hand-authored lettering and a quiet lower quarter for the menu. Sprites,
foreground tiles, HUD symbols and logo letters are authored as native pixel data.

Every final preview is decoded from the actual generated C arrays. No smoothed
scaling is used for native previews or enlarged galleries. Each 8x8 scenery tile
uses exactly one four-color palette. The final panorama edges have identical
pixel columns, and the validation checks the seam after encoding and decoding.

## Hardware layout

- Scene ROM banks 8..11; title bank 2; descriptors, fonts and sprites bank 1.
- Every world uses 304 patterns: 144 in background VRAM bank 0 tiles 112..255,
  160 in VRAM bank 1 tiles 96..255. The title uses 245 patterns.
- Background palettes 0..5 hold scenery, 6 foreground, 7 cream-on-indigo UI.
- All 96 sprite patterns live in sprite VRAM bank 1 tiles 0..95. Sprite attributes
  must include S_BANK. Hero 0..23, beetle 24..27, owl frames 28/29 and 30/31,
  lantern 32/33, seal 34/35, checkpoint 36/37, gate 38..41, wake 42/43,
  spark 44/45, heart 46/47, spring 48/49, thorn 50/51, boss 64..79, fire 80/81.
- Owl frames are 8x16, not 16x16. The hero, beetle and gate are 16x16 packed by
  vertical 8x16 pairs first, then the next column. Boss 32x32 uses the same
  column-major convention, two 8x16 pairs per column.
- Sprite palette 0: hero/heart; 1: beetle/thorn; 2: owlet; 3: lantern; 4: seal/spark/
  spring; 5: checkpoint/gate; 6: wake; 7: dreamwhale/fire.

`terrain_tiles[256]` is the default shared material. The backwards-compatible
`terrain_world_tiles[1024]` adds four 256-byte sets in bank 1; load the block at
`terrain_world_tiles + biome*256` into bank 0 tiles96..111. Warm harbor roof ribs,
monsoon leafstone, copper clockwork panels and pearl-cyan ribs give collision
surfaces their own identity. All sets retain a bright continuous top edge and the
same collision indices.0=left cap, 1=top, 2=right cap, 3=underside, 4=bottom,
5=one-way, 6=spring, 7=crumble, 8=broken crumble, 9=checkpoint, 10=lantern pedestal,
11=water, 12=star, 13..15=roof caps/middle. Floor bodies are deliberately simpler
than scenery so their shape is immediately legible during a fast dash.

Every font tile starts with a blank row 0 and has seven visible rows 1..7. This
prevents the emulator's first window scanline from clipping the tops of letters.
The HUD's `*`, `$`, `+`, `-`, `>`, `?` are explicitly authored.

The readable ASCII font foundation is preserved locally as
`assets/source/font-base.bin` (1024 bytes) from the user's prior Signal Bloom
project. Moonwake adds its own HUD symbols and punctuation, and shifts the
glyphs down one row for consistent native window rendering. The art generator
uses this bundled foundation and requires no files outside the Moonwake package.

## Evidence and candid art review

`assets/native/contact-sheet.png` shows all decoded panoramas and a 160x144
composition mock with a real hero and foreground tiles. These mock screens have
no game logic and are labelled by their filenames. `title-4x.png`,
`sprites-6x.png` and `terrain-6x.png` show the actual encoded pixels at integer
scales. Real gameplay captures belong under `docs/screenshots` and are produced
from the compiled ROM by the runtime owner.

The first art pass had flat rectangular sky bands and a generic rounded boss.
Review replaced those with organic scene paintings, local palette fitting and a
side-profile dreamwhale with curling fin, pearl belly and a luminous dream-knot
jewel. Foreground review replaced uniform grey surfaces with world-specific
material clusters. The tiny hero is expressive and very clear on dark water;
cream backgrounds require its outline to do more work. In highly detailed clock
architecture the 304-pattern ceiling reduces some tiny ornaments. This is an
honest hardware tradeoff: broad landmark shapes and readable play surfaces take
priority. A 9/10 goal should be assessed on the actual ROM by independent critics,
not inferred from the larger generated source paintings.

## Rebuild

From the project root, run `.venv/bin/python tools/build_art.py`.
The generator validates reserved VRAM slots, RGB555 color values, map lengths,
all decoded final pixels, sprite allocations, and seamless horizontal wrap.
Generation is deterministic and saves a per-world tile manifest.
