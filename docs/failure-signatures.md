# Failure signatures

Patterns in GameHub's `log_pcengine_*.txt` and what they meant on 2026-10-04. These are the rules the diagnoser should start with.

Observed by Nick Moody on a REDMAGIC 11 Air (model NX799J, Snapdragon 8 Elite / SM8750, Adreno 830, 16 GB RAM, Android 16) running GameHub 6.3.1 (`com.xiaoji.egggame`). They describe that phone on that day. Do not treat a match as a universal fix, and do not invent a config from a signature alone.

Airplane mode was not tested. Offline-related rows below are log patterns and the session's intended fix, not confirmed airplane-mode results.

## Where to look

Logs readable from the PC:

- `/sdcard/Android/data/com.xiaoji.egggame/files/logs/log_pcengine_<date>_0.txt` — launch config, exit codes, Steam setup steps
- `/sdcard/Android/data/com.xiaoji.egggame/files/logs/log_main_<date>_0.txt` — library and store activity

logcat returned nothing on this phone (system logging appeared to be off).

Each launch writes a block between `WINEMU_LAUNCH_CONFIG_BEGIN` and `WINEMU_LAUNCH_CONFIG_END`, then a line like:

`pc模拟器游戏埋点-启动 <gameId> true 200 <exe path>`

Useful config keys: `config.exePath`, `config.launchCommandLine` / `launchArguments`, `baseContainer.name`, `config.fexConfig`, `config.gpuDriver`, `resolvedDxvk`, `resolvedVkd3d`, `config.steamAppId`, `wineData.sourceType` (1 = Steam, 2 = Epic), `wineData.gameId`, `wineData.isLaunchDesktop`, `config.resolution`, `config.envVars`, `config.dllOverrides`, `config.audioDriver`.

`isLaunchDesktop=true` with `exePath=explorer.exe` is a virtual desktop session.

`config.launchCommandLine` can contain an Epic `-AUTH_PASSWORD=` exchange code. Also redact `epicuserid=` and Steam account names or tokens before showing or saving output.

## Signatures

| Log / symptom | Meaning | Fix |
|---|---|---|
| `ExitCallback returnCode=0` within ~5 s, `RuntimeExited`, `lastFps=null`, Epic | Starter exe exits; GameHub closes container | Launch real exe via `.bat` from virtual desktop (or change install) |
| `ExitCallback returnCode=1`, `RuntimeFailed`, `UplayLaunch.exe` | Ubisoft Connect missing | Install UC via Run program (manual licence/sign-in) |
| `install_script_start/progress` then `UserCancelled` under ~2 min | First-run Steam setup interrupted | Relaunch; wait ~2 min on black screen |
| `NoFirstPresent` / `durationMs≈180000` | Nothing drew for 3 min | Process Manager; may be hung launcher |
| `General protection fault!` … `ShippingPC-BmGame.exe` | PhysX system software missing (UE3) | Install `physx` component |
| `dxvk::DxvkError` / Vulkan 1.1 instance fail via Run program | No usable Vulkan on that launch path | Use virtual desktop or tile, not Run program |
| `appUncompressMemory` UnAsyncWork.cpp:170 | Bad unpack under aggressive FEX / corrupt file | Enable Vector TSO, Memcpy TSO, Half Barrier; if same spot every time → verify files |
| Process ~10 MB, CPU 0%, black screen | Stalled at start (anti-cheat / DRM suspected) | No fix found (Watch Dogs 2) |
| Steam `login_failed, timeout` offline | Steam online login required | Steam tab Offline mode + full client; verify online once |
| Epic tile fails offline in seconds | Needs Epic exchange code | Local import |
| Endless **Start Extract**, files present | Install state never set | Copy to Download + Import Local Game |
| Texture scramble / checkerboard | Bad Proton/FEX combo on this SoC (not fixed by Turnip/DXVK A/B) | Prefer **Proton 11 + default Game Presets FEX** |
| Compatible FEX: 14 FPS / 100% CPU | Too accurate/slow for this game | Custom + TSO safety switches instead |

Steam Offline mode was switched on for some titles in this session and was **not** airplane-tested. Epic has no offline switch; local import was not airplane-tested either.

## Extra diagnostics that worked

- `DXVK_LOG_PATH=D:` and `DXVK_LOG_LEVEL=info` write `<exe>_d3d9.log` to the Download folder.
- Redirecting the game's output in a `.bat` (`game.exe > D:\out.txt 2>&1`) captures Wine/DXVK fatal messages.
- `tasklist` in a `.bat` shows what a starter program launched.
- Unreal Engine 3 games write crash reports to `Documents\<publisher>\<game>\BmGame\Logs\`.
