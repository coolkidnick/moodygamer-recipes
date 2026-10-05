# Offline readiness

Legitimate ways to launch games Nick already owns when GameHub has no network. These are official store and launcher offline modes, plus a local import of an install that is already on the phone.

This page does not describe cracks, Denuvo removers, unofficial Steam or Uplay clients, stripped executables, or anything that fakes ownership. If a title cannot run through the store launcher that owns it, leave it blocked.

Observed on a REDMAGIC 11 Air (model NX799J, Snapdragon 8 Elite / SM8750, Adreno 830, 16 GB RAM, Android 16) running GameHub 6.3.1 (`com.xiaoji.egggame`). Phone notes are from 2026-10-04. The per-game table below is the 2026-10-05 research pass (PCGamingWiki DRM notes plus those phone notes). **Airplane mode was not tested.** “Offline likely” is a research assessment, not a confirmed airplane-mode result. Log patterns live in [`failure-signatures.md`](failure-signatures.md).

## Per-game table

| Game | Store | DRM (PCGamingWiki) | Offline likely | Exact GameHub / launcher steps | One-time online activation? | Before airplane mode |
| --- | --- | --- | --- | --- | --- | --- |
| Metro Exodus | Steam | Steamworks; Denuvo removed 2020-05-27 | Yes, after a Steam offline cache | Install with full `steam_client_0403`. Play once online. Per-game Steam Offline ON. Launch from Steam Offline / the cached client. | Steam login + first launch | Confirm the title launches under Steam Offline while still online; sync cloud saves if wanted; then airplane. |
| Max Payne 3 | Steam | Steam + Rockstar Games Launcher + Social Club | **Working** in GameHub (owner, 2026-10-05). Offline play is likely after the first online launch. Airplane mode was not tested. | Steam Offline + full `steam_client_0403`. Inside the container, prepare Rockstar Games Launcher offline (see below). Launch via Steam → Rockstar Games Launcher → game. | Yes — Steam + Rockstar account; run the game once online | Remember password and Auto Sign-in on the Rockstar launcher; run single-player once; fully quit the launcher; verify an offline launch once before airplane. |
| GTA IV | Steam | Steam + Rockstar Games Launcher | Yes after first online (may need a periodic re-check) | Same Steam Offline + Rockstar launcher prep as Max Payne 3. Optional legitimate launch arg: `-scOfflineOnly`. Prefer the Steam/launcher path that already worked online. | Yes — Steam + Rockstar; run once online | Same Rockstar offline checklist; test Steam Offline and game boot while connected, then disconnect and retest. |
| Dishonored | Steam | Steam (a GOG edition is DRM-free; the Steam copy needs the client) | Yes | Steam Offline + `steam_client_0403`; launch once online first. This phone was switched off Light mode onto the full client for this title. | Steam login + first launch | Cache offline; optional cloud-save sync. |
| Hotline Miami 2 | Steam | Steam. PCGamingWiki notes `steam_appid.txt` only for owned files. That is not a piracy path. On GameHub use Steam Offline. | Yes | Steam Offline + `steam_client_0403`. | Steam login + first launch | Confirm boot under Steam Offline. |
| Thief (2014) | Epic | Epic. PCGamingWiki: the owned `Shipping-ThiefGame` executable (32/64) with `-AUTH_TYPE=exchangecode` | Yes | Preferred: Epic Local Import of the shipping exe (same pattern as LEGO Batman 3), after the owned install. Not imported yet (~30 GB duplicate). | Epic account ownership / first install | Local Import points at the shipping exe; verify launch with no network. |
| Sifu | Epic | Epic. PCGamingWiki: standalone mode via the owned shipping exe | Yes | Epic Local Import of `Sifu-Win64-Shipping.exe` from the owned install. Not imported yet (~30 GB duplicate). | Epic ownership / first run | Confirm Local Import boots offline; cloud saves off. |
| LEGO Batman 3 | Epic | Epic; PCGamingWiki: DRM-free from the owned executable | Yes. Owner: works as a Local Import (menus and intro). | Keep the Epic Local Import of `LEGOBatman3.exe`. No Ubisoft or Rockstar launcher. | Epic install once | None beyond the existing working Local Import. Airplane mode was not tested. |
| Batman: Arkham Asylum | Epic | Epic GOTY; PCGamingWiki: DRM-free when launched from the owned executable | Yes. Owner: runs, with the issues in the 2026-10-04 recipe. | Local Import or the known working shortcut to `ShippingPC-BmGame.exe`. Not imported yet (~8 GB duplicate). | Epic install / first successful boot | Confirm the current working shortcut still boots offline. |
| System Shock 2 Remaster | Epic | Epic; PCGamingWiki (verified 2026-10-01): DRM-free from the owned executable | Yes | Epic Local Import of the remaster exe after the owned install. Not imported yet (~4 GB duplicate). | Epic install once | Direct exe smoke test offline. |
| Watch Dogs 2 | Epic | Ubisoft Connect + Denuvo + Easy Anti-Cheat | **Blocked / parked.** Unlikely under Android Wine until Ubisoft Connect launches cleanly. Offline single-player is only theoretical after a first online activation, which this phone never reached. | Do not crack. The tile was removed. `-eac_launcher` was tried and changed nothing. Official Ubisoft Connect offline mode is the legitimate path only after Connect and the game reach a menu online once. | Yes — Ubisoft account linked to the Epic copy, then one online activation | Not useful until Connect and the game reach the menu online. They did not. |

Ask before large Local Import copies. The Saboteur was noted as a local import on 2026-10-04 and was not tested; it is not in this research table.

**DRM / offline sources:**

- https://www.pcgamingwiki.com/wiki/Metro_Exodus
- https://www.pcgamingwiki.com/wiki/Max_Payne_3
- https://www.pcgamingwiki.com/wiki/Store:Rockstar_Games_Launcher
- https://www.pcgamingwiki.com/wiki/Dishonored
- https://www.pcgamingwiki.com/wiki/Hotline_Miami_2:_Wrong_Number
- https://www.pcgamingwiki.com/wiki/Thief
- https://www.pcgamingwiki.com/wiki/Sifu
- https://www.pcgamingwiki.com/wiki/Lego_Batman_3:_Beyond_Gotham
- https://www.pcgamingwiki.com/wiki/Batman:_Arkham_Asylum
- https://www.pcgamingwiki.com/wiki/System_Shock_2:_25th_Anniversary_Remaster
- https://www.pcgamingwiki.com/wiki/Watch_Dogs_2

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

Not imported, because each copy duplicates the game: Thief (30 GB), Sifu (30 GB), System Shock 2 (4 GB), Batman: Arkham Asylum (8 GB). Executable names in the table for Thief, Sifu, and the System Shock 2 remaster are from PCGamingWiki, not from a phone log. Ask before large copies.

## Rockstar Launcher offline

Max Payne 3 is a Steam install (appid 204100, GameHub id 3828). Its first launch runs a Steam install script: DirectX first, then the official Rockstar Games Launcher. On 2026-10-04 that script reached the launcher installer (“Language select”). Licence acceptance and Rockstar account sign-in are manual. Do not automate them.

On 2026-10-05 the owner confirmed Max Payne 3 **working** in GameHub. That confirmation does not say whether Steam Offline or the Rockstar launcher offline mode was in use, and it does not record the working Proton / FEX / Turnip / DXVK stack. The recipe at `recipes/max-payne-3/selftest-working-2026-10-05.json` keeps an earlier mid-setup log as provisional settings only. Do not apply those settings as the working stack. Pull the next `log_pcengine` launch-config block first.

PCGamingWiki’s legitimate offline prep for the Rockstar Games Launcher (the checklist the table refers to; not recorded as already completed on this phone, and not airplane-tested):

1. Open Rockstar Games Launcher while online.
2. Log in with **Remember my password** checked.
3. Run the game at least once so the offline config is written.
4. Open the launcher overlay → Settings → Profile → **Auto Sign-in = Enabled**.
5. Close the game and fully quit the launcher.
6. Disconnect, then relaunch the launcher and confirm it signs into offline mode and the title is playable.

All digital Max Payne 3 versions require Social Club. The Steam build also requires the Rockstar Games Launcher since update v1.0.0.255. Source: [PCGamingWiki — Rockstar Games Launcher](https://www.pcgamingwiki.com/wiki/Store:Rockstar_Games_Launcher), [PCGamingWiki — Max Payne 3](https://www.pcgamingwiki.com/wiki/Max_Payne_3).

GTA IV uses the same Steam Offline + launcher prep. `-scOfflineOnly` is an optional legitimate argument from that research pass. It was not logged on this phone.

## Ubisoft Connect offline (Watch Dogs 2 blocked / parked)

GameHub has no Ubisoft Connect component. On 2026-10-04 Connect was installed with the official installer via Run program. Licence acceptance and sign-in are manual.

The legitimate offline path for a Ubisoft game is official Ubisoft Connect offline mode after an online sign-in and activation. That offline mode was not switched on in this session and was not airplane-tested. It cannot help a game that never reaches a menu.

**Watch Dogs 2 stays blocked and parked.** Epic copy, GameHub id 159162. The tile launched `UplayLaunch.exe` and failed in about 4 seconds until Connect was installed. Connect then verified and installed 23.75 GB under `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\games\WATCH_DOGS2\` and started the game. `WatchDogs2.exe` sat at about 10 MB on a black screen for over five minutes (CPU idle). The launch argument `-eac_launcher` changed nothing. No game-side log. No fix. The tile was removed from the library. A leftover container copy was about 25.4 GB; delete it only after confirming no other Ubisoft title needs it.

PCGamingWiki: every edition needs Ubisoft Connect and Denuvo. Easy Anti-Cheat is on by default; `-eac_launcher` is the documented single-player switch and disables multiplayer. It was already tried here. Direct `WatchDogs2.exe` does not skip Connect. This repo does not document a bypass. Source: [PCGamingWiki — Watch Dogs 2](https://www.pcgamingwiki.com/wiki/Watch_Dogs_2).

## What not to do

- Do not add cracks, Denuvo removers, emulated Steam or Uplay clients, or patched executables as an “offline path”.
- Do not use `steam_appid.txt`, a “DRM-free exe” guide, or an Epic auth argument as a way to run a copy you do not own. The table’s executable notes are for installs already on this phone.
- Do not treat a subway failure, a `login_failed, timeout` line, or “offline likely” as proof that airplane mode works.
- Do not copy another title’s settings onto Max Payne 3. The only logged stack for that game is the unverified mid-setup set in its recipe.
