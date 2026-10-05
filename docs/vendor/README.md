# Browser emulator and runtime sources

Moonwake's native game does not depend on WasmBoy. The local browser preview uses the unmodified `wasmboy@0.7.1` npm UMD bundle. Its SHA-256 and the source/dependency archive hashes are recorded in `source-manifest.json`.

`wasmboy-0.7.1-source.tar.gz` contains the unmodified `core/`, `lib/`, and root build/configuration files from upstream commit `8e96bcb70969d943b1ffc4028b169c835098ce04` (tag `v0.7.1`). Demo media, documentation, and unrelated test games are not needed for building the emulator and are omitted. The GPL-3.0-or-later license is included both in this directory and the source archive.

`wasmboy-dependencies/` preserves the source packages and notices for the production dependencies pinned in upstream's lockfile: audiobuffer-to-wav, idb, raf, responsive-gamepad, and performance-now. Their licenses are included in the archives and extracted beside them. The emulator contains these components under their original licenses.

To rebuild the emulator, extract its source archive into a working directory, install the Node/npm toolchain compatible with that upstream release, then use its `package-lock.json` and `npm ci` / `npm run build`. The original core uses AssemblyScript 0.15.x; the library uses Rollup 0.66.x and the upstream build plugins. Older packages may require their contemporary Node environment. The game ROM build does not require Node or a browser-emulator rebuild. Dependency sources are also included locally for inspection and offline adaptation.

`gbdk-4.5.0-source.tar.gz` preserves the unmodified upstream GBDK runtime library code, headers, support/build files, and licenses used for the linked native runtime. Upstream examples and documentation are omitted. `gbdk-LICENSE_GPLV2_LE` retains the linking exception and `gbdk-LICENSE_SDCC` describes the toolchain components. These third-party terms are separate from Moonwake's MIT code and CC BY 4.0 assets.
