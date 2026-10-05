# recipes/

Per-game recipe folders. Only **sourced** recipes belong here (EmuReady listing, BannerHub JSON, Reddit post with explicit settings, etc.).

- `verification.status` must be `community` or `verified` for real recipes.
- Never invent Wine/Proton/DXVK/driver values.
- See `examples/recipe.example.json` for structure (`status: example` — do not apply).
- The `mg` engine (separate project) looks up recipes by title / exe / Steam appid / GameHub id.
- Owner self-tests (`provenance.source_type` = `self_test`, author Nick Moody) are verified on the listed phone. They are separate files from EmuReady `community` recipes in the same slug and must not be merged into those listings. LEGO Batman 3 local-import verification covers menus and intro. Batman: Arkham Asylum GOTY is verified with issues. Airplane mode was not tested.

Layout:

```
recipes/<game-slug>/<recipe-id-suffix>.json
```
