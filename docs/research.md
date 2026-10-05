# Research: per-game configs on Android PC emulation

Concise field notes for MoodyGamer recipes (`mg` engine consumes this store; this repo is **not** a GameHub fork). Claims cite public URLs. Do not invent settings.

## GameHub (stock GameSir / XiaoJi)

### Package names
| Product | Package | Notes / source |
|---|---|---|
| Stock GameHub | `com.xiaoji.egggame` | Play Store listing; Lite patches change this package. [Play Store](https://play.google.com/store/apps/details?id=com.xiaoji.egggame), [GameHub Lite patch](https://github.com/Producdevity/gamehub-lite/blob/master/patches/diffs/AndroidManifest.xml.patch) |
| GameHub Lite (base) | `gamehub.lite` | Side-by-side install. [gamehublite/gamehub-oss](https://github.com/gamehublite/gamehub-oss), [Producdevity/gamehub-lite](https://github.com/Producdevity/gamehub-lite) |
| Lite variants | `com.antutu.ABenchMark`, `com.antutu.benchmark.full`, `com.ludashi.aibench`, `com.tencent.ig`, … | Performance / spoof variants for some SoCs. [BannerHub release notes](https://github.com/The412Banner/BannerHub/releases/tag/v3.0.0), [Producdevity README](https://github.com/Producdevity/gamehub-lite) |

### Cloud / community configs (important)
- **Stock GameHub does not appear to ship a user-facing community config browser for Wine/Proton/DXVK settings.** Community sharing of *full* per-game Wine stacks is a third-party feature (BannerHub / BannerHub Lite), not documented as a stock GameHub cloud export. Steam **cloud saves** in GameHub 5.x are about save sync, not emulator settings. [Gadget Hacks on Steam cloud saves](https://android.gadgethacks.com/news/gamehub-50-reveals-steam-cloud-saves-that-actually-work/)
- Stock GameHub **does** pull server-side **Game Presets / executeScript** recommendations (GPU-aware execution context). GameHub Lite’s worker documents `POST /simulator/executeScript` as “Get Steam game configuration”, with privacy stripping, and Lite’s static API hosts `executeScript/generic` and `executeScript/qualcomm` presets when not proxied. [gamehub-lite-worker README](https://github.com/Producdevity/gamehub-lite-worker/blob/main/README.md), [gamehub-lite-api README](https://github.com/Producdevity/gamehub-lite-api/blob/main/README.md)
- Users report that Lite’s “Game Presets” can apply wrong settings vs official GameHub for some titles (e.g. Silksong) depending on proxy/preset coverage. [gamehublite/gamehub-oss#19](https://github.com/gamehublite/gamehub-oss/issues/19)

### Local storage / export feasibility (stock)
- BannerHub reverse-engineering (GameHub-based ReVanced) states per-game Wine settings live in **SharedPreferences** under keys like `pc_g_setting<gameId>`, and export/import writes JSON under `/sdcard/BannerHub/configs/`. Same keys are said to be shared with BannerHub Lite. [BannerHub COMMUNITY_CONFIG_REPORT.md](https://github.com/The412Banner/BannerHub/blob/main/COMMUNITY_CONFIG_REPORT.md), [BannerHub README](https://github.com/The412Banner/BannerHub/blob/main/README.md)
- Manifest for stock/Lite uses `android:allowBackup="true"` and `requestLegacyExternalStorage="true"` (compileSdk 35). Backup / SAF access may still be blocked by scoped storage and device policy; **reading another app’s private SharedPreferences without root or a same-signing fork is generally not feasible**. Treat direct SharedPreferences mutation of stock GameHub as high-risk / often impossible without a fork. [AndroidManifest patch](https://github.com/Producdevity/gamehub-lite/blob/master/patches/diffs/AndroidManifest.xml.patch)
- **Implication for `mg`:** prefer dry-run + documented apply paths (intents, user-confirmed UI, or user-exported JSON). Do not assume stock GameHub exposes a public import API.

### Intents
- GameHub Lite adds exported `GameDetailActivity` with action **`gamehub.lite.LAUNCH_GAME`**, extras such as `steamAppId` and `autoStartGame`. Documented in [gamehublite/gamehub-oss README](https://github.com/gamehublite/gamehub-oss). Stock GameHub does not document an equivalent open LAUNCH_GAME filter in public Lite sources (stock activity is not exported the same way in the Lite patch baseline).

### Open-source tools that read/write GameHub settings
| Project | What it does | Relation to stock |
|---|---|---|
| [BannerHub](https://github.com/The412Banner/BannerHub) | GameHub ReVanced: Export/Import Config, community browser, Component Manager | Fork/patch of GameHub APK — **not** stock |
| [bannerhub-game-configs](https://github.com/The412Banner/bannerhub-game-configs) | Public JSON store (~2.7k games, 15k+ uploads as of research date) via Cloudflare Worker | Companion to BannerHub |
| [GameHub Lite](https://github.com/Producdevity/gamehub-lite) | Telemetry/bloat strip, offline, package rename, LAUNCH_GAME | Patch set / educational fork |

Exported BannerHub JSON shape (meta + `settings` + `components`). Settings keys observed in the wild include `pc_ls_CONTAINER_LIST` (Proton/Wine), `pc_ls_DXVK`, `pc_ls_VK3k`, `pc_ls_GPU_DRIVER_`, `pc_set_constant_95` (FEX), `pc_set_constant_94` (Box64), `pc_ls_environment_variable`, `pc_ls_AUDIO_DRIVER`, `pc_ls_core_limit`, FEX/Box64 translator JSON blobs, resolution keys. Example LEGO Batman 3 uploads: [Lego_Batman_3](https://github.com/The412Banner/bannerhub-game-configs/tree/main/configs/Lego_Batman_3), [LEGOBatman3](https://github.com/The412Banner/bannerhub-game-configs/tree/main/configs/LEGOBatman3). Repo README says “Do not submit configs manually — they are managed by the app.” No SPDX licence listed on the configs repo at research time.

## Winlator and forks

### Config model
- **Container**: directory with `.container` JSON + Wine prefix. [Winlator Mintlify containers overview](https://brunodev85-winlator.mintlify.app/containers/overview)
- **Shortcut**: XDG `.desktop` with `[Extra Data]` overrides: `execArgs`, `screenSize`, `graphicsDriver`, `dxwrapper`, `dxwrapperConfig`, `audioDriver`, `forceFullscreen`, `box86Preset`, `box64Preset`, `wincomponents`, `envVars`, `controlsProfile`, `dinputMapperType`. [Winlator Mintlify shortcuts](https://brunodev85-winlator.mintlify.app/controls/shortcuts)
- Export of `.desktop` for frontends (Daijisho, etc.) is common in Cmod-family forks; some forks removed **import** of shortcuts. [Pipetto-crypto commit removing import](https://github.com/Pipetto-crypto/winlator/commit/514512c174dfc08b0aa13325cc7ce9507f762cc4), [Winlator101 shortcuts docs](https://github.com/K11MCH1/Winlator101/blob/main/docs/shortcuts.md)
- Some forks add container `.tzst` backup/restore and SharedPreferences settings JSON export/import. [RedMagic tuning PR example](https://github.com/piashmsuf-eng/winlator/pull/3)

### Sharing sites / lists
- Community Google Sheets (Winlator tracking / Gamefusion forks) — discussed on Reddit (access often blocked to bots; URLs still circulate in [r/EmulationOnAndroid](https://www.reddit.com/r/EmulationOnAndroid/), [r/Gamefusion](https://www.reddit.com/r/Gamefusion/)).
- [winlator.dev games list](https://winlator.dev/games-list/)
- [abhay-byte/mali-win-emu-list](https://github.com/abhay-byte/mali-win-emu-list) (Mali-focused, includes GameHub notes)

## GameNative

- Package / app id `app.gamenative`. Intent action **`app.gamenative.LAUNCH_GAME`**. [GameNative AndroidManifest](https://github.com/utkarshdalal/GameNative)
- **Export/Import Config**: pretty-printed container JSON via SAF. [PR #649](https://github.com/utkarshdalal/GameNative/pull/649), [ContainerConfigTransfer](https://github.com/utkarshdalal/GameNative/blob/master/app/src/main/java/app/gamenative/ui/util/ContainerConfigTransfer.kt)
- **Use known config** + auto-apply on launch for store-backed games (Steam/GOG/Epic/Amazon), GPU-aware. [PR #892](https://github.com/utkarshdalal/GameNative/pull/892)
- **In-app community config browser** (filter by device/GPU family). [PR #1782](https://github.com/utkarshdalal/GameNative/pull/1782)
- Public API surface includes `https://api.gamenative.app/api/best-config` (client uses Play Integrity / attestation — not a free anonymous dump). Compatibility page: [gamenative.app/compatibility](https://gamenative.app/compatibility/)
- Third-party helper: [andreisugu/gamenative-config-tools](https://github.com/andreisugu/gamenative-config-tools) converts EmuReady / report text → importable JSON.
- Licence: GPL-3.0. ~11k stars at research time.

## Mobox / Cassia / Horizon
- **Mobox**: Termux + Box64 + Wine; largely superseded / unmaintained relative to Winlator/GameHub. [olegos2/mobox](https://github.com/olegos2/mobox)
- **Cassia**: cancelled (2024). [Android Authority](https://www.androidauthority.com/cassia-app-emulator-cancelled-3451597/), [cassia-org](https://github.com/cassia-org)
- Horizon / other handheld OEMs: device-specific skins; treat configs as proprietary unless a public export format is documented.

## EmuReady (https://www.emuready.com)

### What it offers
- Community compatibility **listings** with device, SoC, emulator, performance label, notes, votes, and **emulator-specific custom fields** (for GameHub: Proton/Wine, DXVK, VKD3D, Turnip/driver, FEX/Box64, resolution, env vars, core/VRAM limits, Steam client, etc.).
- Example GameHub custom fields returned by `customFieldDefinitions.getByEmulator` for emulator id `09203574-33b7-4f56-85b1-851b51e0ab2a` include: `compatibility_layer`, `dxvk_version`, `vkd3d_version`, `gpu_driver`, `cpu_translator`, `translation_parameters`, `game_resolution`, `env_variables`, `command_line`, `audio_driver`, `cpu_core_limit`, `vram_limit`, `dx_wrapper`, `native_rendering_plus`, `steam_client_version`, `using_gamehub_lite`, …

### Public API
- Documented mobile/integration API: [emuready.com/docs/api](https://www.emuready.com/docs/api), OpenAPI at [api-docs/mobile-openapi.json](https://www.emuready.com/api-docs/mobile-openapi.json)
- Base: `/api/mobile/trpc/[procedure]` (GET queries with SuperJSON `input`, POST mutations). Public procedures include `listings.get`, `listings.byId`, `listings.byGame`, `games.get`, `emulators.get`, `customFieldDefinitions.getByEmulator`, `pcListings.get`, …
- Rate limits: “generous” without a key; free API keys for higher limits. Dataset dump requested but not shipped; weekly dump considered. [Issue #455](https://github.com/Producdevity/emuready/issues/455)
- `listings.getEmulatorConfig` exists but OpenAPI enum is limited to azahar / eden / gamenative — **not GameHub** at research time. Do not assume auto-downloadable GameHub launcher configs from that endpoint.

### Licence / terms for reuse
- Code: **GPL-3.0-or-later**. [Producdevity/EmuReady](https://github.com/Producdevity/EmuReady)
- OpenAPI `info.licence` also lists GPL-3.0-or-later.
- [Terms of Service](https://www.emuready.com/terms) (updated 2026-04-01): prohibit false content, spam, hacking, unauthorized **commercial** use; do not grant an explicit CC dump licence for listing content. **Practical guidance for this recipe store:** cite listing URLs, attribute authors, keep recipes CC-BY-4.0 with provenance, do not scrape aggressively, prefer API with attribution/`x-api-key`, and never copy private user data. When in doubt, ask in EmuReady Discord / GitHub.

## Other community databases
| Resource | Role |
|---|---|
| EmuReady | Structured reports + settings fields (closest ProtonDB analogue for Android handhelds) |
| BannerHub game-configs | Mass GameHub-fork JSON dumps by device/GPU |
| GameNative compatibility + best-config | Auto-apply known configs inside GameNative |
| Reddit megathreads / sheets | Free-form settings (fragile URLs, bot-blocked) |
| mali-win-emu-list | Mali-oriented GitHub list |
| Snapdragon 8 Elite threads | Anecdotal playable lists on r/EmulationOnAndroid (driver/version sensitive) |

## Closest projects to “recipe applied automatically per game”

| Project | Auto-apply? | Gap vs MoodyGamer goal |
|---|---|---|
| **GameNative** Use known config + community browser | Yes (in-app, store games) | Tied to GameNative; Attested API; not GameHub |
| **BannerHub** community configs | Manual Import / Browse | Requires BannerHub fork, not stock GameHub |
| **GameHub Game Presets** | Server-side presets | Opaque, not user-exportable as recipes; Lite coverage issues |
| **EmuReady + gamenative-config-tools** | Manual convert → Import | No CLI dry-run apply into GameHub; GameHub needs a write path |
| **Winlator .desktop sharing** | Manual | Fragmented across forks; no unified recipe schema |

**Remaining gap:** a **stock-GameHub-safe**, dry-run-first, sourced recipe store + CLI (`mg`) that looks up by title/exe/Steam/GameHub id, never invents settings, and only applies via confirmed, reversible paths. That is the MoodyGamer opportunity.

## LEGO Batman 3: Beyond Gotham (Steam AppID **313690**)

Public EmuReady GameHub listings (queried 2026-10-05 via `listings.get` / `listings.byId`):

| Listing | Device / SoC | Perf | Key settings (as reported) | URL |
|---|---|---|---|---|
| `a919806b-…` | AYN Thor Max / Snapdragon 8 Gen 2 | Great (~55 FPS) | GameHub v5.3.5, proton10.0-arm64x-2, Game Preset, turnip_v26.1.0_R4, dxvk-2.3.1-async, vkd3d-2.12, Fex_20250910, 1280×720, Pulse | [listing](https://www.emuready.com/listings/a919806b-a624-4e46-9a46-c2edd6def6de) |
| `7adcd729-…` | iQOO Neo 8 / Snapdragon 8+ Gen 1 | Great (30+) | GameHub 5.3.5, proton10.0-arm64x-2, Game Preset, turnip_v26.1.0_R3, dxvk-1.10.3-async, Fex-20260103, 1280×720 | [listing](https://www.emuready.com/listings/7adcd729-eae1-4a8d-9b27-d139eda5d1af) |
| `1bea2895-…` | AYN Thor Max / SD 8 Gen 2 | Great (~50 FPS) | **GameHub Lite** v5.1.3, proton10.0-arm64x-2, Extreme preset, turnip_v26.0.0_R8, dxvk-2.7.1-1-async, vkd3d-2.13, Fex_20260103, 7-core limit, 4 GB VRAM, BGRA8 | [listing](https://www.emuready.com/listings/1bea2895-f278-4cbb-aa02-5276fdfbd05c) |

BannerHub also has `configs/Lego_Batman_3/` and `configs/LEGOBatman3/` (different devices/GPUs; keys are GameHub SharedPreferences dumps). No well-sourced Winlator-specific public report with full settings was retrieved during this research pass (Reddit blocked automated fetch).

GameNative `api/game-runs` returned no playable counts for this title on Adreno 830 at query time.

## Gaps / opportunity
1. Stock GameHub lacks a documented import API; forks hold the export/import UX.
2. EmuReady has the best structured settings + public API, but no GameHub `getEmulatorConfig` download path and no CC dump licence.
3. BannerHub has volume but couples to a fork, has no clear SPDX on configs, and includes device-specific noise / tokens in meta.
4. GameNative already auto-applies recipes for *its* containers — closest UX, wrong host for “stock GameHub + recipes”.
5. Winlator formats are shareable (`.desktop` / `.container`) but fork-fragmented.
6. Opportunity: **moodygamer-recipes** as host-agnostic, schema-validated, sourced recipes + `mg` dry-run apply for GameHub (and later Winlator/GameNative), never inventing configs.

## Recommended recipe fields (derived)
From GameHub EmuReady custom fields + BannerHub `pc_ls_*` keys + Winlator Extra Data + GameNative container JSON:

- **Identifiers:** title, exe, steam_appid, gog_id, gamehub_id, emuready_game_id, aliases
- **Target:** app enum, package_name, app version range
- **Device:** manufacturer, model, soc, gpu, ram, android
- **Settings:** wine_or_proton, dx_wrapper, dxvk_version, vkd3d_version, cpu_translator, translator_preset / box64_preset / fex_preset, gpu_driver, resolution, surface_format, audio_driver, cpu_core_limit, vram_limit, env_vars, launch_args, native_rendering_plus, dinput_library, steam_client_version, offline_mode, auto_sync_cloud_saves, steam_input, components[], optional raw_host_keys / extra
- **Verification:** untested | community | verified | example; performance; fps; notes; known_issues
- **Provenance:** source_type, source_url, source_id, author, captured_at, license_note
- **schema_version**

## Sources
- https://play.google.com/store/apps/details?id=com.xiaoji.egggame
- https://github.com/Producdevity/gamehub-lite
- https://github.com/gamehublite/gamehub-oss
- https://github.com/Producdevity/gamehub-lite-worker
- https://github.com/Producdevity/gamehub-lite-api
- https://github.com/The412Banner/BannerHub
- https://github.com/The412Banner/BannerHub/blob/main/COMMUNITY_CONFIG_REPORT.md
- https://github.com/The412Banner/bannerhub-game-configs
- https://android.gadgethacks.com/news/gamehub-50-reveals-steam-cloud-saves-that-actually-work/
- https://github.com/gamehublite/gamehub-oss/issues/19
- https://brunodev85-winlator.mintlify.app/controls/shortcuts
- https://brunodev85-winlator.mintlify.app/containers/overview
- https://github.com/utkarshdalal/GameNative
- https://gamenative.app/compatibility/
- https://github.com/andreisugu/gamenative-config-tools
- https://www.emuready.com/docs/api
- https://www.emuready.com/api-docs/mobile-openapi.json
- https://www.emuready.com/terms
- https://github.com/Producdevity/EmuReady
- https://github.com/Producdevity/emuready/issues/455
- https://github.com/olegos2/mobox
- https://www.androidauthority.com/cassia-app-emulator-cancelled-3451597/
- https://store.steampowered.com/api/appdetails?appids=313690
- https://www.emuready.com/listings/a919806b-a624-4e46-9a46-c2edd6def6de
- https://www.emuready.com/listings/7adcd729-eae1-4a8d-9b27-d139eda5d1af
- https://www.emuready.com/listings/1bea2895-f278-4cbb-aa02-5276fdfbd05c
