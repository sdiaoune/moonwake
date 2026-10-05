# Moonwake campaign design

Kip is a small moon hare with a bright comet scarf. The sky sea has fallen asleep, and its wishes have tangled inside a dream whale. Kip crosses a lantern harbor, a rain garden, and a celestial workshop to loosen the knot. The ending is a dawn song, not a conquest: the whale wakes, the sky sea glows, and Kip brings a little of the light home.

The recognizable image is a cream hare dashing between warm floating lanterns over a giant midnight whale. The '90s influence lives in direct movement, distinct worlds, secret upper paths, memorable melody, and strong pixels. The modern part is how readily the player can retry, explore, and improve.

## Player rhythm

A held jump travels higher than a tapped jump. B turns Kip's scarf into a short horizontal dash. Ground contact or touching a hanging lantern restores the dash. Enemies can be bounced on; a dash lets skilled players keep their speed. The ground route is legible and generous, while the three optional moon seals ask the player to look upward and choose a more expressive line.

The campaign never gates progress on seals. Every stage has a checkpoint around its center, unlimited retries, and a clear broad final landing. Seal collection and saved time ranks supply replay goals without forcing the first playthrough to become a collection chore. S-rank pars are calibrated to a controller-only all-seal campaign, with roughly one-third extra time for a good practiced run. They range from 26 to 42 seconds, including the finale; they are tuning targets, not human speedrun records.

## The twelve stages

| Stage | World | Distinct phrase | Length | Par |
|---|---|---|---:|---:|
| Lantern Quay | Saffron Harbor | Wide safe dock; first small gap; two-hop upper eaves | 1536 px | 26 s |
| Apricot Rooftops | Saffron Harbor | Ascending roof heights reverse into a descending courtyard | 1600 px | 29 s |
| Kitewake Causeway | Saffron Harbor | Broad runway, first lantern refresh, three-step kite chain | 1664 px | 27 s |
| Lotus After Rain | Jade Monsoon | Optional lotus springs lift Kip into pearl ledges | 1600 px | 33 s |
| Rainbell Canopy | Jade Monsoon | Brittle upper leaves fall onto forgiving lower boughs | 1664 px | 28 s |
| Glasswater Run | Jade Monsoon | A flowing rise-and-fall riverbank wave with a long aerial ribbon | 1728 px | 28 s |
| Brass Moonworks | Violet Engines | A low/high gear rhythm, a brass spring, and a workshop rest | 1600 px | 28 s |
| Pendulum Steps | Violet Engines | Four ascending steps, a flat upper bridge, and a descending answer | 1664 px | 30 s |
| Sleepwheel Express | Violet Engines | Runway and raised gear alternate; crumble chains reward commitment | 1760 px | 27 s |
| Whale in the Sky | Moonwhale | A scenic breath; the harbor's familiar jumps become a whale spine | 1600 px | 27 s |
| Stardrift Current | Moonwhale | Mirrored ground waves and the most expressive rising lantern chain | 1760 px | 30 s |
| Heart of Moonwake | Moonwhale | Familiar roof phrase, three final pearl seals, then the dream knot | 1760 px | 42 s |

The whole campaign spans 19,936 world pixels. Each stage contains exactly three seals. Stage names fit the 18-character native label, and story vignettes use three lines of at most 20 characters each.

## Geometry and encounter rules

The native view is 160×144. Solid floor surfaces are usually y128; raised ground routes move in 16-pixel steps. Most main-route gaps are 24–48 pixels, with broad landings of at least 96 pixels. Late Stardrift Current stretches one gap to 96 pixels and places a lantern in the crossing. Glasswater Run brings an introduced spring onto the main route. Pendulum Steps and Sleepwheel Express add brittle main ledges above solid catch shelves. Earlier spring and crumble lessons remain optional and forgiving.

The first stage waits until x496 for its first beetle. Beetles patrol within broad individual landings. Owls appear on upper routes after a safe introduction to the relevant movement idea. The final boss arena has continuous floor from x1400 to x1760 at y128, no ordinary foes or pickups after x1400, and a goal at x1712. All three final seals precede the arena. The engine owns the six-hit boss and gate behavior.

The checkpoint is placed in the interior of a main landing, never at a gap, beneath a forced spring, or on an upper branch. Goal feet and checkpoint feet match the corresponding platform surface. Spawn y is a top-left coordinate. Enemy and pickup y values are top-left coordinates. Platform widths are in pixels, not tiles.

## Why seals feel different

Early harbor seals are small roof climbs that teach the player to notice height. Kite seals introduce lantern contact. Lotus seals start with springs. Canopy seals cross crumbling leaves. Moonworks seals join those ideas to a stricter jumping rhythm. Whale in the Sky relaxes the difficulty deliberately; Stardrift Current brings back the most expressive dash chains. The final stage gives all seals before the boss so exploration cannot demand repeated boss attempts.

Every branch has an entry main platform, its own platform-index path, a seal pickup index, and a rejoin landing recorded in `routes.json`. Most upper jumps rise 16–32 pixels. The optional path can be abandoned by falling back to the solid route; the player's achievement is choosing a beautiful line, not paying for a mistake with a lengthy reset.

## Native data interface

`levels.h` follows the production contract's `LevelDef`, `PlatformDef`, `PickupDef`, and `EnemyDef` field layout. The level loader, story helpers, and par-time helper use the GBDK `BANKED` convention; their source and constants reside in bank 3.

`level_load(id, out, plats, picks, enemies)` copies only the active counts. Invalid ids resolve to stage zero. The caller owns the destination storage and should respect the level counts. `level_intro(id, a, b, c)` and `level_outro(a, b, c)` write NUL-terminated story lines into three caller buffers of at least 21 bytes. `level_par(id)` returns seconds.

`routes.json` is a full independent record of every platform, pickup, and enemy plus lesson/beat annotations. `main_route` and `safe_platform_indices` identify the campaign path; the late brittle segments have separate solid catch shelves. `seal_routes` identify optional upper branches. This lets controller playtests verify the ROM against the authored campaign without modifying player state to simulate success.

## Review and tuning

Static authoring validation checks twelve stages, three seals per stage, tile-grid platform coordinates, all production caps, safe-route gaps and rises, checkpoint placement, final landing width, and goal placement. Those checks establish geometry consistency, not fun or runtime reachability.

Controller playtests must cover each main route, representative seal paths, spring and crumble behavior, checkpoint retries, saved collection, and the boss gate. A critic should look for repeated patterns, ambiguous landing edges, unfair owls, dash input friction, and seals that ask for unnecessary backtracking. The intended score is high, but the review must record actual shortcomings. If a branch is frustrating, adjust its lantern or landing before raising its score.
