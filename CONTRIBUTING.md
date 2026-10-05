# Contributing

Thanks for helping build a **sourced** recipe store. The hard rule: **never invent a config**.

## Adding a recipe

1. Confirm a public source with **explicit** settings (versions of Proton/Wine, DXVK, VKD3D, Turnip/driver, FEX/Box64, resolution, env vars, etc.).
2. Create `recipes/<game-slug>/<short-id>.json` matching `schema/recipe.schema.json`.
3. Set:
   - `verification.status`: `community` (cited) or `verified` (you retested)
   - `provenance.source_url` to the canonical public URL
   - `device` / `target` to match the report (do not “improve” for a different phone)
4. Run `node scripts/validate.js`.
5. Open a PR. Prefer one game per PR when possible.

## Do not

- Submit Fabricated / “should work” settings.
- Mark `verified` without a retest on the listed device class.
- Put `example` recipes outside `recipes/examples/`.
- Strip `provenance` or licence notes.
- Include personal phone dumps, tokens, account ids, or private paths.

## Recipe requests

Use the **Recipe request** issue template. Include device/SoC and any EmuReady / Reddit links. Maintainers will only add a recipe when a source is found.

## Code

Scripts and CI are MIT. Keep `scripts/validate.js` dependency-free unless there is a strong reason to add packages.
