# Moonwake art: eight sky-sea postcards on native Game Boy Color

Moonwake's visual identity is Kip, a cream moon hare whose persimmon scarf echoes
comet tails, lantern tassels and whale flukes. Warm pearl highlights connect the
journey, while each world has its own landmark, silhouette and surface material.
The expansion keeps the original four panorama C files, title, font, palettes,
original sprite poses and first four terrain blocks byte-for-byte identical.
`assets/source/native-preservation.json` records their released hashes and makes
this guarantee part of every art rebuild.

| World | Landmark and invitation to explore | Foreground material |
| --- | --- | --- |
| Saffron Harbor | Peach pagodas on floating islands, a pearl moon | Warm roof ribs |
| Jade Monsoon | Cathedral-scale celadon lotus and bamboo isles | Leafstone |
| Violet Engines | Monumental astronomical clock, orbit bridges and gears | Copper clock panels |
| Moonwhale | Sleeping cyan sky whale and sweeping star paths | Pearl-cyan ribs |
| Ember Festival | Scarlet phoenix kite, ribbon tails and distant lantern bridge | Amber festival shingles |
| Pearl Observatory | Ivory shell sanctuary, telescope and tiny domed islands | Carved shell arches |
| Aurora Orchard | Twisting living branches, jewel pears and polar light ribbons | Interwoven orchard roots |
| Dawn Archive | Immense book cathedral and a glowing door inside a curled page | Layered parchment leaves |

The new landmarks are distinct places that reward a long journey and scenic
forks. They do not represent collision surfaces. All eight scenes reserve a quiet
dark lower quarter so platforms and the hero remain legible. Kip is hand-authored
at 16x16 with a persistent one-pixel shadow silhouette, cream body and red scarf.
All six poses retain the same readable face, ears and proportions. Dash compresses
the body and lays the ears back; running alternates two leg silhouettes; jumping
tucks the legs.

The built-in imagegen tool produced the original key visual and eight scenery
paintings. Original PNGs are preserved in `assets/source`, with exact prompt sets
in `imagegen-prompts.json` and `imagegen-expansion-prompts.json`. Each expansion
painting was a separate generation with its own composition; these are original
scenes rather than recolored variants. Paintings are production inputs, not
emulator screenshots. `tools/build_art.py` reduces the panorama inputs once to
256x144, fits six local four-color RGB555 palettes, shares flipped tile patterns
and merges only the nearest patterns as needed to fit 304 scenery tiles. New
scenes protect boundary and water patterns during merging, so seamless wrap and
quiet reflection ribbons survive that reduction. All fitting and merging are
deterministic, with no randomized quantization or display smoothing.

The title preserves the original whale composition and hand-authored lettering,
with a quiet lower quarter for menus. Sprites, foreground tiles, HUD symbols and
logo letters are authored as native pixel data.

## Hardware layout

- Scene ROM banks 8..15; title bank 2; descriptors, fonts, sprites, four boss blocks
  and eight foreground material sets in bank 1.
- Every world uses 304 patterns: 144 in background VRAM bank 0 tiles 112..255,
  160 in VRAM bank 1 tiles 96..255. The unchanged title uses 245 patterns.
- Background palettes 0..5 hold scenery, 6 foreground, 7 cream-on-indigo UI.
- All 96 shared sprite patterns live in sprite VRAM bank 1 tiles 0..95. Sprite
  attributes include S_BANK. Hero 0..23, beetle 24..27, owl frames 28/29 and 30/31,
  lantern 32/33, seal 34/35, checkpoint 36/37, gate 38..41, wake 42/43,
  spark 44/45, heart 46/47, spring 48/49, thorn 50/51, moving platform 52/53,
  jelly 54/55 with pulse frame 56/57, boss 64..79, fire 80/81.
- Owl, moving-platform segment and jelly frames are 8x16. The hero, beetle and
  gate are 16x16 packed by vertical 8x16 pairs first, then the next column.
  Boss 32x32 uses the same column-major convention, two 8x16 pairs per column.
- Sprite palette 0: hero/heart; 1: beetle/thorn; 2: owlet/jelly; 3: lantern;
  4: seal/spark/spring; 5: checkpoint/gate/moving platform; 6: wake;
  7: boss/fire. Moving segments retain a continuous cream top and dark underside.

`terrain_tiles[256]` is the default shared material. The backwards-compatible
`terrain_world_tiles[2048]` contains eight 256-byte blocks; load the block at
`terrain_world_tiles + biome*256` into bank 0 tiles 96..111. Every set has a bright
continuous top edge and the same collision indices: 0 left cap, 1 top, 2 right cap,
3 underside, 4 bottom, 5 one-way, 6 spring, 7 crumble, 8 broken crumble,
9 checkpoint, 10 lantern pedestal, 11 water, 12 star, 13..15 roof caps/middle.
Floor bodies are simpler than scenery so their shape reads during a fast dash.

`const unsigned char boss_tiles[4][256]` contains Rainbell Warden, Comet Manta,
Prism Sentinel and Dreamwhale, in that order. The Warden is a suspended shrine bell
with a rain crown and clapper; the Manta has swept pointed wings and a forked comet
tail; the Sentinel has a faceted core and detached orbit brackets. Dreamwhale is
the unchanged original side-profile creature with curling fin, pearl belly and
dream-knot jewel. Each block is native 32x32, four colors including transparency.
The runtime copies a selected block into sprite slots 64..79 from ROM0. The shared
sprite set also retains the original Dreamwhale in those slots for compatibility.

Every font tile starts with a blank row 0 and has seven visible rows 1..7, preventing
first-window-scanline clipping. The HUD's `*`, `$`, `+`, `-`, `>`, `?` are explicitly
authored. The readable ASCII foundation is bundled as
`assets/source/font-base.bin` and requires no files outside the Moonwake package.

## Evidence and candid art review

`assets/native/contact-sheet.png` shows all eight decoded panoramas and a 160x144
composition mock with the real hero and foreground tiles. These mock screens have
no game logic and are labelled by filename. `title-4x.png`, `sprites-6x.png`,
`bosses-8x.png` and `terrain-6x.png` show actual encoded pixels at integer scales.
Real gameplay captures belong under `docs/screenshots` and come from the compiled
ROM. Source paintings are never presented as hardware screenshots.

The native scenery retains each broad landmark and stays within the original
hardware allocation. The 304-pattern ceiling softens tiny windows, leaves and page
ornaments; the elaborate Dawn Archive loses more fine detail than the shell
observatory. This is a visible tradeoff. Broad silhouettes and readable play
surfaces take priority. The quiet lower water and Kip's outline keep the new
palettes readable. Bosses use deliberately distinct native silhouettes rather
than scaled paintings. Art quality should be assessed on the actual ROM by
independent critics, not inferred from source paintings or a requested score.

## Rebuild and validation

From the project root, run `python3 tools/build_art.py` with NumPy and Pillow
available. No external source images or prior project paths are required.

The generator validates the exact decoded pixels of eight panorama C arrays,
horizontal wrap seams, reserved VRAM slots, tile-map lengths, four colors per
tile, RGB555 palette values, boss order and column-major bytes, all eight distinct
terrain blocks, moving-platform/jelly slots, and preservation hashes for original
scenes, title, font, terrain and sprites. `assets/native/manifest.json` records
per-world tile allocations and every merge. Each panorama is 256x144 and 304 tiles;
the title remains 160x144 and 245 tiles. Repeated runs in the same Python/Pillow
runtime produce identical encoded C bytes and decoded assets.
