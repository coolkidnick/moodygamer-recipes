# recipes/

Per-game recipe folders. Only **sourced** recipes belong here (EmuReady listing, BannerHub JSON, Reddit post with explicit settings, etc.).

- `verification.status` must be `community` or `verified` for real recipes.
- Never invent Wine/Proton/DXVK/driver values.
- See `examples/recipe.example.json` for structure (`status: example` — do not apply).
- The `mg` engine (separate project) looks up recipes by title / exe / Steam appid / GameHub id.

Layout:

```
recipes/<game-slug>/<recipe-id-suffix>.json
```
