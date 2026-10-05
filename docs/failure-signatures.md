# Failure signatures

Patterns in GameHub's `log_pcengine_*.txt` and what they meant on 2026-10-04. These are the rules the diagnoser should start with.

Observed by Nick Moody on a REDMAGIC 11 Air (model NX799J, Snapdragon 8 Elite / SM8750, Adreno 830, 16 GB RAM, Android 16) running GameHub 6.3.1 (`com.xiaoji.egggame`). They describe that phone on that day. Do not treat a match as a universal fix, and do not invent a config from a signature alone.

## Where to look

Logs readable from the PC:

- `/sdcard/Android/data/com.xiaoji.egggame/files/logs/log_pcengine_<date>_0.txt` — launch config, exit codes, Steam setup steps
- `/sdcard/Android/data/com.xiaoji.egggame/files/logs/log_main_<date>_0.txt` — library and store activity

logcat returned nothing on this phone (system logging appeared to be off).

Each launch writes a block between `WINEMU_LAUNCH_CONFIG_BEGIN` and `WINEMU_LAUNCH_CONFIG_END`, then a line like:

`pc模拟器游戏埋点-启动 <gameId> true 200 <exe path>`

Useful config keys: `config.exePath`, `config.launchCommandLine`, `baseContainer.name`, `config.fexConfig`, `config.gpuDriver`, `resolvedDxvk`, `config.steamAppId`, `wineData.sourceType` (1 = Steam, 2 = Epic).

`config.launchCommandLine` can contain an Epic `-AUTH_PASSWORD=` exchange code. Strip it before showing or saving output.

## Signatures

| Log pattern | Meaning | Fix |
|---|---|---|
| `ExitCallback#1 returnCode=0` within about 5 s, `reason=RuntimeExited`, `lastFps=null`, Epic source | Launch program is a starter that hands off and exits; GameHub closes the container | Launch the real game exe directly with a helper `.bat` |
| `ExitCallback#1 returnCode=1` within about 5 s, `reason=RuntimeFailed`, exe is `UplayLaunch.exe` | Ubisoft Connect not installed in the container | Install Ubisoft Connect via Run program |
| `SteamStatusCallback ... install_script_start` / `install_script_progress`, then `ExitWineActivityConfirm` and `reason=UserCancelled` under about 2 min | First-run Steam setup was still running when the user closed it | Relaunch and wait; black screen for about 2 minutes is normal |
| `result=Failed(reason=NoFirstPresent, durationMs=180031)` | Nothing drew a frame in 3 minutes: game hung, or a launcher is sitting on screen | Check the process list (side menu → Performance → Process Manager) |
| Game's own box: `General protection fault!` in `kernelbase.dll` at start (Unreal Engine 3) | PhysX system software missing, or graphics layer failed to start | Install `physx` component; check DXVK log |
| Game output: `terminate called after throwing an instance of 'dxvk::DxvkError'`, DXVK log stops before listing a GPU | Vulkan gave DXVK no usable device in that launch | Seen only when started via Run program at first; worked when started from the virtual desktop |
| Game's own box: `Assertion failed: appUncompressMemory(...)` | Background data unpack gave a wrong result: aggressive CPU translation, or a damaged file | Turn on Vector TSO, Memcpy TSO, Half Barrier; if same spot every time, verify files |
| Process list shows the game exe at about 10 MB memory, CPU 0% | Game stalled at startup (anti-cheat or copy protection suspected) | No fix found yet |

## Extra diagnostics that worked

- `DXVK_LOG_PATH=D:` and `DXVK_LOG_LEVEL=info` write `<exe>_d3d9.log` to the Download folder.
- Redirecting the game's output in a `.bat` (`game.exe > D:\out.txt 2>&1`) captures Wine/DXVK fatal messages.
- `tasklist` in a `.bat` shows what a starter program launched.
- Unreal Engine 3 games write crash reports to `Documents\<publisher>\<game>\BmGame\Logs\`.
