# Moonwake research

Research date: October 4, 2026. Sources below are official manufacturer, publisher, or toolchain material. This document separates source observations from our design decisions; the sources do not certify this game's quality or physical-hardware compatibility.

## Chromatic is a pixel canvas

ModRetro describes Chromatic's display as a 160×144, 2.56-inch panel built around the original pixel size and coloration. That supports designing at native resolution with readable silhouettes and carefully chosen palette relationships, rather than drawing a larger image and shrinking it afterward. [ModRetro: Display — The Hard Way](https://modretro.com/blogs/blog/display-the-hard-way).

**Applied:** the playfield remains 160×144, backgrounds use native 8×8 tiles, and Kip has a cream silhouette and persimmon scarf against cooler scenery. Four deliberately different color stories replace the conventional grass/desert/ice sequence: saffron harbor, jade rain, violet celestial workshops, and a pearl dream whale. These are our creative choices, not ModRetro requirements.

ModRetro publishes cartridge compatibility guidance that distinguishes Game Boy, Game Boy Color, and Chromatic releases. The production target is a native CGB ROM, with emulator verification and a separate physical-cartridge verification step. [ModRetro: Chromatic Games — Color Coding and Compatibility](https://support.modretro.com/en_us/chromatic-games-color-coding-and-compatibility-SygymlOAWx).

## Teach with the first encounter

Nintendo's developers describe iterating the first Super Mario Bros. stage to teach unfamiliar players naturally. They planned alternative outcomes, including how the first mushroom would bounce back into the player's path, and repeatedly revised the opening. [Nintendo: Iwata Asks, “Adjusting the Map In A Daily Cycle”](https://iwataasks.nintendo.com/interviews/wii/nsmb/1/4/).

**Applied:** Lantern Quay begins with a broad safe dock, visible reachable stars, and a two-step optional seal climb. The first main gap is 24 pixels; the first enemy occupies a wide dock. Spring and crumble introductions appear on optional upper routes above recoverable ground. Intro text names only the new idea, then the level shows it.

The next interview chapter discusses players' trust in reward placement and avoiding arrangements that betray reasonable expectations. [Nintendo: Iwata Asks, “Applying A Single Idea To Both Land And Sky”](https://iwataasks.nintendo.com/interviews/wii/nsmb/1/5/).

**Applied:** ordinary stars sit over known landing surfaces. The ground route never requires a seal or a grind. Optional heights are visible from below, and most failures drop Kip onto a broad solid route. We test ground routes and seal routes separately because geometric reachability alone does not prove that a pickup trail feels trustworthy.

## Speed should invite another route

SEGA's official Sonic Origins manual describes multiple paths through stages, checkpoint posts, and replaying personal best times. Its Anniversary Mode also provides unlimited attempts. [SEGA: Sonic Origins Plus Online Manual](https://manuals.sega.com/origins/en/?pid=7).

**Applied:** Moonwake uses a forgiving ground path plus more expressive upper routes. Lantern contact refreshes the scarf dash, turning optional routes into an aerial rhythm rather than only a higher walkway. Checkpoints, unlimited retries, saved seals, and best ranks encourage practice. Those choices interpret the references; Moonwake uses original characters, environments, mechanics, and compositions.

SEGA also provides the original Game Gear Sonic the Hedgehog instruction manual in its official archive. This is a useful period reference for compact portable-game presentation, not an asset source. [SEGA: Game Gear Micro Manual Archive](https://www.sega.jp/ggmicro/manual.html), [Sonic the Hedgehog manual PDF](https://www.sega.jp/ggmicro/manual/pdf/SonicTheHedgehog.pdf).

## Native banking shapes content

GBDK's documentation recommends MBC5 for most projects, describes each ROM bank as 16 KiB, and explains that `BANKED` calls select the destination bank automatically. Constant data in a switchable bank is accessible only while that bank is active. [GBDK-2020: ROM/SRAM Banking and MBCs](https://gbdk.org/docs/api/docs_rombanking_mbcs.html).

**Applied:** level definitions, platforms, pickups, enemies, story lines, and par times reside together in bank 3. The banked loader copies the active level's data into caller-owned RAM. No ROM pointers escape the loader. Twelve stages use only 14–19 platforms, 25–37 pickups, and 3–8 enemies each, leaving space below the production caps. This is an implementation design; successful linking and runtime playtests are still necessary.

## What research cannot establish

The references guide the design. They cannot establish a 9/10 score, commercial sales, emulator correctness, or Chromatic hardware behavior. Independent review should inspect the compiled ROM, actual controller traces, readable screenshots, musical output, and the complete campaign. Physical hardware should be described as unverified until the cartridge is tested on the device.
