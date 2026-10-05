# moodygamer-recipes

**Plug-and-play per-game recipes for GameHub, Winlator and Android emulators. Not a GameHub fork.**

This repository is a **shared recipe store**: JSON configs keyed by game (title / exe / Steam AppID / GameHub id), with a strict schema, CI validation, and provenance for every real entry.

The companion CLI engine is **`mg`** (built separately). This repo does **not** contain the `mg` engine. `mg` is expected to: look up a recipe on add/launch → **dry-run** → apply into the host’s per-game settings when a sourced recipe exists → otherwise diagnose from logs (and optionally consult [EmuReady](https://www.emuready.com)) and **never invent** a config.

## Recipe model

| Situation | What happens |
|---|---|
| **Known fix** | One `mg` command (or companion auto-apply) looks up the recipe and applies it after dry-run. |
| **Unknown game** | Diagnose once from logs / public reports, then **save a recipe** with a real source link. Do not guess. |

Recipes are **not** universal. A working Snapdragon 8 Gen 2 + Turnip build may fail on another SoC, driver, or GameHub version. Match `device` / `target` fields; treat mismatches as warnings.

## What’s in the box

```
schema/recipe.schema.json   JSON Schema (schema_version 1.0.0)
recipes/<slug>/*.json       Sourced recipes only
recipes/examples/           Placeholder example (status: example — never apply)
scripts/validate.js         Node validator (no npm deps)
docs/research.md            Research notes + sources
```

## Safety rules (for humans and for `mg`)

- Never delete user data or game installs.
- Never change phone **system** settings.
- Never sign in or accept licences on the user’s behalf.
- Never tap UI without confirming the app and screen.
- Every phone-touching command must have a **dry-run** mode.
- **Never invent recipes.** If there is no cited public source, leave the game unknown.

This project targets **stock GameHub** (and later Winlator / GameNative). It is explicitly **not** a GameHub fork (unlike BannerHub / GameHub Lite patches).

## Honest limits

- No universal config; per-title and per-device variance is normal.
- Unknown games will **not** auto-work.
- Stock GameHub has no documented public import API for Wine settings; apply paths must stay dry-run-first and user-confirmed (see `docs/research.md`).
- EmuReady and community reports can be wrong or outdated—`community` ≠ `verified`.

## How to contribute a recipe

1. Find a **public** source with explicit settings (EmuReady listing, BannerHub JSON, Reddit post that lists Proton/DXVK/driver/etc.).
2. Copy fields into a new file under `recipes/<game-slug>/` using `schema/recipe.schema.json` (or start from `recipes/examples/recipe.example.json` but set `verification.status` to `community` and replace all placeholder values).
3. Fill `provenance.source_url` and mark `verification.status` as `community` (or `verified` only if you retested on the listed device).
4. Run `node scripts/validate.js` and open a PR.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

- **Code** (scripts, CI, schema tooling): [MIT](LICENSE)
- **Recipes** (JSON under `recipes/`): [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) — attribute the recipe authors and **always keep `provenance.source_url`**.

Upstream reports remain subject to their own terms (e.g. [EmuReady ToS](https://www.emuready.com/terms); EmuReady project code is GPL-3.0-or-later).

## Related

- Research: [`docs/research.md`](docs/research.md)
- `mg` engine: separate teammate / repo (not here)

## Inspired By
- User: rhythmerc/ emu-hub
- User: utkarshdalal/ GameNative
