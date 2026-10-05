# Offline readiness

Legitimate ways to launch games Nick already owns when GameHub has no network. These are official store and launcher offline modes, plus a local import of an install that is already on the phone.

This page does not describe cracks, unofficial Steam clients, stripped executables, or DRM bypasses. If a title cannot run through the store launcher that owns it, leave it blocked.

Observed on a REDMAGIC 11 Air (model NX799J, Snapdragon 8 Elite / SM8750, Adreno 830, 16 GB RAM, Android 16) running GameHub 6.3.1 (`com.xiaoji.egggame`), from the 2026-10-04 notes plus the 2026-10-05 Max Payne 3 status. **Airplane mode was not tested.** Nothing below is a confirmed airplane-mode result. Log patterns live in [`failure-signatures.md`](failure-signatures.md).

## Steam Offline + full steam_client

Steam tiles in Light mode cannot use Offline mode. The switch is disabled until the Steam client is the full client, recorded as `steam_client_0403`.

Path that was set up on 2026-10-04 21:55:

1. PC Game Settings → Steam tab.
2. Steam client version: full client (`steam_client_0403`), not Light mode. Dishonored was the title where Light mode was switched to the full client.
3. Turn on **Offline mode** (“Allow running verified Steam games without network connection”).

“Verified” here probably means the game was launched once online with this setting. Offline mode was turned on for Dishonored, Max Payne 3, GTA IV, Metro Exodus, and Hotline Miami 2. It was **not** airplane-tested.

Before that change, a subway test (network loss, not airplane mode) failed Steam tiles with `login_failed, timeout`. The intended fix is Offline mode plus the full client, after one online launch. See the Steam row in [`failure-signatures.md`](failure-signatures.md).

## Epic Local Import

Epic has no offline switch and no Epic tab. An Epic tile needs a fresh exchange code, so it fails in seconds when offline. The subway test did that to Thief.

The legitimate path is the one used for LEGO Batman 3: copy the install that is already on the phone to shared storage, then Library → Import → Local Game, and launch the game executable (for LEGO, `LEGOBatman3.exe`). That import is an offline candidate. Airplane mode was not tested. The LEGO local-import recipe covers menus and intro only.

Not imported, because each copy duplicates the game: Thief (30 GB), Sifu (30 GB), System Shock 2 (4 GB), Batman: Arkham Asylum (8 GB). Ask before large copies. The Saboteur was noted as a local import and was not tested.

## Rockstar Launcher offline

Max Payne 3 is a Steam install (appid 204100, GameHub id 3828). Its first launch runs a Steam install script: DirectX first, then the official Rockstar Games Launcher. On 2026-10-04 that script reached the launcher installer (“Language select”). Licence acceptance and Rockstar account sign-in are manual. Do not automate them.

The legitimate offline path is the official Rockstar Games Launcher offline mode, after that online sign-in, together with Steam Offline mode and the full Steam client above. The launcher is part of the owned Steam install. It is not a crack.

That combination was not airplane-tested. On 2026-10-05 the owner confirmed Max Payne 3 **working** in GameHub. That confirmation does not say whether Steam Offline or the Rockstar launcher offline mode was in use, and it does not record the working Proton / FEX / Turnip / DXVK stack. The recipe at `recipes/max-payne-3/selftest-working-2026-10-05.json` keeps an earlier mid-setup log as provisional settings only. Do not apply those settings as the working stack. Pull the next `log_pcengine` launch-config block first.

## Ubisoft Connect offline (Watch Dogs 2 blocked)

GameHub has no Ubisoft Connect component. On 2026-10-04 Connect was installed with the official installer via Run program. Licence acceptance and sign-in are manual.

The legitimate offline path for a Ubisoft game is official Ubisoft Connect offline mode after an online sign-in and activation. That offline mode was not switched on in this session and was not airplane-tested.

**Watch Dogs 2 stays blocked.** Epic copy, GameHub id 159162. The tile launched `UplayLaunch.exe` and failed in about 4 seconds until Connect was installed. Connect then verified and installed 23.75 GB under `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\games\WATCH_DOGS2\` and started the game. `WatchDogs2.exe` sat at about 10 MB on a black screen for over five minutes. The launch argument `-eac_launcher` changed nothing. No game-side log. No fix. The tile was removed from the library. A leftover container copy was about 25.4 GB. Offline mode does not unblock this title, and this repo does not document a bypass.

## What not to do

- Do not add cracks, emulated Steam clients, or patched executables as an “offline path”.
- Do not treat a subway failure or a `login_failed, timeout` line as proof that offline mode works.
- Do not copy another title’s settings onto Max Payne 3. The only logged stack for that game is the unverified mid-setup set in its recipe.
