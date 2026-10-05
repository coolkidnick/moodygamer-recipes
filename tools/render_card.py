#!/usr/bin/env python3
"""Render portrait config cards for working moodygamer recipes.

One 1080x1920 PNG per working recipe under recipes/ (recipes/examples/ is
skipped). Values are copied from the recipe. A field with no value is the
words "not yet verified". Nothing is guessed.

  python3 tools/render_card.py            # write cards/*.png (needs Pillow)
  python3 tools/render_card.py --check    # stdlib only; CI uses this
  python3 tools/render_card.py --report   # print the field summary

Pillow is imported only when rendering. --check and --report do not need it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES_DIR = ROOT / "recipes"
CARDS_DIR = ROOT / "cards"

MISSING = "not yet verified"
WIDTH = 1080
HEIGHT = 1920

PERF_OK = ("perfect", "great", "playable", "ingame", "launches")

# Notes that mean this file is a failed or blocked report, not a working one.
FAIL_PHRASES = (
    "failed path",
    "stays blocked",
    "blocked / parked",
    "blocked and parked",
    "does not run",
    "did not run",
    "will not launch",
    "won't launch",
    "cannot launch",
    "never reached",
)

RUN_WORDS = re.compile(
    r"\b(working|works|runs|ran|running|playable|launches|launched|in-game|ingame)\b",
    re.I,
)

APP_LABELS = {
    "gamehub": "GameHub",
    "gamehub_lite": "GameHub Lite",
    "bannerhub": "BannerHub",
    "winlator": "Winlator",
    "winlator_frost": "Winlator Frost",
    "winlator_glibc": "Winlator glibc",
    "winlator_cmod": "Winlator Cmod",
    "winlator_ajay": "Winlator Ajay",
    "gamenative": "GameNative",
    "mobox": "Mobox",
    "other": "Other",
}

# Specific symbols become words first. Anything else outside ASCII is dropped
# so cards never render arrows, daggers, or other special symbols.
CHAR_MAP = {
    "\u2192": " to ",
    "\u2190": " from ",
    "\u2191": " up ",
    "\u2193": " down ",
    "\u2194": " to ",
    "\u21d2": " to ",
    "\u25b6": " ",
    "\u25ba": " ",
    "\u2022": " ",
    "\u00b7": " ",
    "\u2013": "-",
    "\u2014": " - ",
    "\u2011": "-",
    "\u2212": "-",
    "\u00d7": "x",
    "\u2026": "...",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u00a0": " ",
    "\u202f": " ",
    "\u2009": " ",
    "\u00b0": " degrees ",
    "\u2020": "",
    "\u2021": "",
    "\u00ae": "",
    "\u2122": "",
}


def plain(value) -> str:
    """ASCII words only. Arrows become words. Daggers and other symbols go."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    for src, dst in CHAR_MAP.items():
        text = text.replace(src, dst)
    kept = []
    for ch in text:
        code = ord(ch)
        if ch in "\n\t":
            kept.append(" ")
        elif 32 <= code <= 126:
            kept.append(ch)
    text = "".join(kept)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def present(value) -> str | None:
    """Return a plain non-empty value, or None when the recipe has nothing."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return None
    text = plain(value)
    return text if text else None


def is_examples_path(rel: str) -> bool:
    norm = rel.replace("\\", "/")
    return norm.startswith("recipes/examples/") or "/examples/" in norm


def performance_matches(perf: str) -> bool:
    label = plain(perf).lower()
    if not label:
        return False
    for word in PERF_OK:
        if label == word or label.startswith(word + " ") or label.startswith(word + ",") or label.startswith(word + ";") or label.startswith(word + "("):
            return True
    return False


def is_broken(recipe: dict) -> bool:
    notes = ((recipe.get("verification") or {}).get("notes") or "").lower()
    return any(phrase in notes for phrase in FAIL_PHRASES)


def notes_say_it_runs(recipe: dict) -> bool:
    verification = recipe.get("verification") or {}
    blob = f"{verification.get('notes') or ''} {verification.get('performance') or ''}"
    if RUN_WORDS.search(blob):
        return True
    if re.search(r"\bfps\b", blob, re.I):
        return True
    if present(verification.get("average_fps")):
        return True
    return False


def is_working(recipe: dict, rel: str) -> bool:
    """Working recipes get a card. Examples, broken paths, and silent files do not."""
    if is_examples_path(rel):
        return False
    verification = recipe.get("verification") or {}
    status = verification.get("status")
    if status not in ("verified", "community"):
        return False
    if is_broken(recipe):
        return False
    if performance_matches(verification.get("performance") or ""):
        return True
    return notes_say_it_runs(recipe)


def walk_recipes():
    files = sorted(RECIPES_DIR.rglob("*.json"))
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        yield rel, data


def app_label(app: str | None) -> str | None:
    if not app:
        return None
    return APP_LABELS.get(app, plain(app) or None)


def emulator_name(recipe: dict) -> str:
    target = recipe.get("target") or {}
    label = app_label(target.get("app"))
    package = present(target.get("package_name"))
    if label and package:
        return f"{label} ({package})"
    return label or package or MISSING


def emulator_version(recipe: dict) -> str:
    target = recipe.get("target") or {}
    minimum = present(target.get("app_version_min"))
    maximum = present(target.get("app_version_max"))
    if minimum and maximum and maximum != minimum:
        return f"{minimum} to {maximum}"
    if minimum:
        return minimum
    # A short note is a version. A sentence is the note itself, not a guess.
    note = present(target.get("app_version_note"))
    return note or MISSING


def store_value(recipe: dict) -> str:
    game = recipe.get("game") or {}
    notes = plain((recipe.get("verification") or {}).get("notes") or "").lower()
    tags = {plain(tag).lower() for tag in (recipe.get("tags") or [])}
    parts: list[str] = []

    match = re.search(r"game source = ([^.;]+)", notes)
    if match:
        source = match.group(1).strip()
        if source:
            parts.append("GOG" if source == "gog" else source.title())

    epic = "epic copy" in notes or "epic" in tags
    if epic and not any(part.lower() == "epic" for part in parts):
        parts.append("Epic")

    steam_id = game.get("steam_appid")
    steam_text = present(steam_id) if steam_id not in (None, "", 0) else None
    has_steam = any(part.lower() == "steam" for part in parts)
    if steam_text and not has_steam:
        if any(part.lower() == "epic" for part in parts):
            parts.append(f"Steam appid {steam_text} also listed")
        else:
            parts.append("Steam")
    elif "steam" in tags and not has_steam and not any(part.lower().startswith("steam appid") for part in parts):
        parts.append("Steam")

    gog_id = present(game.get("gog_id"))
    if gog_id and not any(part.lower() == "gog" for part in parts):
        parts.append("GOG")

    if not parts:
        return MISSING
    # Keep first occurrence only.
    seen = set()
    unique = []
    for part in parts:
        key = part.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(part)
    return "; ".join(unique)


def device_value(recipe: dict) -> str:
    device = recipe.get("device") or {}
    bits = []
    for key in ("manufacturer", "model", "soc", "gpu"):
        text = present(device.get(key))
        if text:
            bits.append(text)
    ram = device.get("ram_gb")
    if ram is not None and present(ram):
        bits.append(f"{present(ram)} GB RAM")
    android = present(device.get("android_version"))
    if android:
        bits.append(f"Android {android}")
    notes = present(device.get("notes"))
    if notes:
        bits.append(notes)
    return ", ".join(bits) if bits else MISSING


def verification_line(recipe: dict) -> str:
    verification = recipe.get("verification") or {}
    provenance = recipe.get("provenance") or {}
    status = verification.get("status") or ""
    source_type = provenance.get("source_type") or ""
    author = present(provenance.get("author"))
    captured = present(provenance.get("captured_at")) or ""
    date = captured[:10] if len(captured) >= 10 else captured

    if status == "verified" and source_type == "self_test":
        who = author or "the listed author"
        if date:
            return f"Verified by {who} on device, {date}"
        return f"Verified by {who} on device"
    if status == "community" and source_type == "emuready":
        bits = ["EmuReady community report"]
        if author:
            bits.append(author)
        if date:
            bits.append(date)
        return ", ".join(bits)

    bits = [plain(status) or MISSING]
    if source_type:
        bits.append(plain(source_type))
    if author:
        bits.append(author)
    if date:
        bits.append(date)
    return ", ".join(bits)


def dx_version(settings: dict) -> str:
    parts = []
    dxvk = present(settings.get("dxvk_version"))
    vkd3d = present(settings.get("vkd3d_version"))
    if dxvk:
        parts.append(f"DXVK {dxvk}")
    if vkd3d:
        parts.append(f"VKD3D {vkd3d}")
    return "; ".join(parts) if parts else MISSING


def graphics_driver(settings: dict) -> str:
    extra = settings.get("extra") or {}
    driver = present(settings.get("gpu_driver"))
    mesa = present(extra.get("mesa_driver"))
    if driver and mesa:
        return f"{driver}; Mesa {mesa}"
    if driver:
        return driver
    if mesa:
        return f"Mesa {mesa}"
    return MISSING


def preset_value(settings: dict) -> str:
    bits = []
    translator = present(settings.get("translator_preset"))
    fex = present(settings.get("fex_preset"))
    box = present(settings.get("box64_preset"))
    if translator:
        bits.append(translator)
    if fex:
        bits.append(f"FEX preset {fex}")
    if box:
        bits.append(f"Box64 preset {box}")
    return "; ".join(bits) if bits else MISSING


def container_variant(settings: dict) -> str:
    extra = settings.get("extra") if isinstance(settings.get("extra"), dict) else {}
    for key in ("container_variant", "containerVariant", "variant"):
        found = present(settings.get(key)) or present(extra.get(key))
        if found:
            return found
    return MISSING


def exec_path(recipe: dict) -> str:
    game = recipe.get("game") or {}
    extra = (recipe.get("settings") or {}).get("extra") or {}
    if not isinstance(extra, dict):
        extra = {}
    bits = []
    exe = present(game.get("exe"))
    if exe:
        bits.append(exe)
    imported = present(extra.get("import_exe"))
    if imported and imported != exe:
        bits.append(f"import {imported}")
    via = present(extra.get("launch_via"))
    if via:
        bits.append(f"via {via}")
    launches = present(extra.get("launches_exe"))
    if launches and launches != exe:
        bits.append(f"launches {launches}")
    launch_from = present(extra.get("launch_from"))
    if launch_from:
        bits.append(launch_from)
    blocked = present(extra.get("do_not_launch"))
    if blocked:
        bits.append(f"do not launch {blocked}")
    return "; ".join(bits) if bits else MISSING


def settings_warning(recipe: dict) -> str | None:
    extra = (recipe.get("settings") or {}).get("extra") or {}
    if not isinstance(extra, dict):
        return None
    note = present(extra.get("provisional_note"))
    flagged = extra.get("not_the_working_launch_stack") is True or extra.get("do_not_apply_as_working_stack") is True
    if note:
        return note
    if flagged:
        status = present(extra.get("settings_status"))
        return status
    return None


def optional_text(settings: dict, key: str) -> str | None:
    return present(settings.get(key))


def component_names(settings: dict) -> str | None:
    components = settings.get("components")
    if not isinstance(components, list):
        return None
    names = []
    for item in components:
        if isinstance(item, dict):
            name = present(item.get("name"))
            if name:
                names.append(name)
        else:
            name = present(item)
            if name:
                names.append(name)
    return ", ".join(names) if names else None


def known_issues(recipe: dict) -> str | None:
    issues = (recipe.get("verification") or {}).get("known_issues")
    if not isinstance(issues, list):
        return None
    texts = [present(item) for item in issues]
    texts = [item for item in texts if item]
    return "; ".join(texts) if texts else None


class Row:
    def __init__(self, label: str, value: str, optional: bool = False, flex: bool = False):
        self.label = label
        self.value = value if value else MISSING
        self.optional = optional
        self.flex = flex

    @property
    def missing(self) -> bool:
        return self.value == MISSING


class Section:
    def __init__(self, title: str, rows: list[Row]):
        self.title = title
        self.rows = [row for row in rows if not (row.optional and row.missing)]


def build_model(recipe: dict) -> dict:
    settings = recipe.get("settings") or {}
    verification = recipe.get("verification") or {}
    provenance = recipe.get("provenance") or {}
    game = recipe.get("game") or {}

    offline = settings.get("offline_mode")
    offline_text = MISSING
    if isinstance(offline, bool):
        offline_text = "true" if offline else "false"

    sections = [
        Section(
            "General",
            [
                Row("Game", present(game.get("title")) or MISSING),
                Row("Store", store_value(recipe)),
                Row("Device", device_value(recipe)),
                Row("Emulator", emulator_name(recipe)),
                Row("Emulator version", emulator_version(recipe)),
                Row("Performance", present(verification.get("performance")) or MISSING),
                Row("FPS", present(verification.get("average_fps")) or MISSING),
                Row("Container variant", container_variant(settings)),
                Row("Offline-ready", offline_text),
            ],
        ),
        Section(
            "Graphics",
            [
                Row("Resolution", present(settings.get("resolution")) or MISSING),
                Row("Graphics driver", graphics_driver(settings)),
                Row("DX wrapper", present(settings.get("dx_wrapper")) or MISSING),
                Row("DX version", dx_version(settings)),
                Row("Surface format", optional_text(settings, "surface_format") or MISSING, optional=True),
                Row("Audio driver", optional_text(settings, "audio_driver") or MISSING, optional=True),
                Row("VRAM limit", optional_text(settings, "vram_limit") or MISSING, optional=True),
            ],
        ),
        Section(
            "Emulation",
            [
                Row("Proton / Wine", present(settings.get("wine_or_proton")) or MISSING),
                Row("FEX / Box64", present(settings.get("cpu_translator")) or MISSING),
                Row("Preset", preset_value(settings)),
                Row("CPU core limit", optional_text(settings, "cpu_core_limit") or MISSING, optional=True),
                Row("DInput library", optional_text(settings, "dinput_library") or MISSING, optional=True),
            ],
        ),
        Section(
            "Environment",
            [
                Row("Env vars", present(settings.get("env_vars")) or MISSING),
                Row("Launch options", present(settings.get("launch_args")) or MISSING),
                Row("Steam client", optional_text(settings, "steam_client_version") or MISSING, optional=True),
                Row(
                    "Native rendering",
                    optional_text(settings, "native_rendering_plus") or MISSING,
                    optional=True,
                ),
            ],
        ),
        Section(
            "Advanced",
            [
                Row("Exec path", exec_path(recipe)),
                Row("Components", component_names(settings) or MISSING, optional=True),
                Row("Notes", present(verification.get("notes")) or MISSING, flex=True),
                Row("Known issues", known_issues(recipe) or MISSING, optional=True, flex=True),
            ],
        ),
    ]

    return {
        "id": recipe.get("id") or "",
        "title": present(game.get("title")) or MISSING,
        "app": app_label((recipe.get("target") or {}).get("app")) or MISSING,
        "status": verification.get("status") or "",
        "performance": present(verification.get("performance")) or MISSING,
        "verification": verification_line(recipe),
        "source": present(provenance.get("source_url")) or MISSING,
        "warning": settings_warning(recipe),
        "sections": sections,
    }


def missing_labels(model: dict) -> list[str]:
    labels = []
    for section in model["sections"]:
        for row in section.rows:
            if row.missing:
                labels.append(row.label)
    return labels


def card_filename(recipe_id: str) -> str:
    safe = plain(recipe_id).lower().replace(" ", "-")
    safe = re.sub(r"[^a-z0-9._-]", "", safe)
    if not safe:
        raise SystemExit(f"recipe id is not a usable filename: {recipe_id!r}")
    return f"{safe}.png"


def working_recipes():
    selected = []
    for rel, data in walk_recipes():
        if is_working(data, rel):
            selected.append((rel, data))
    return selected


def expected_cards():
    cards = {}
    for rel, data in working_recipes():
        name = card_filename(data["id"])
        cards[name] = (rel, data)
    return cards


def run_logic_tests() -> None:
    assert plain("menu 55\u201360 FPS \u2192 desktop \u2020") == "menu 55-60 FPS to desktop"
    assert "\u2020" not in plain("dagger \u2020 here")
    assert plain("51\u00b0C") == "51 degrees C"
    assert all(32 <= ord(ch) <= 126 or ch == " " for ch in plain("A \u2192 B \u2122"))

    failed = {
        "verification": {
            "status": "verified",
            "performance": "Great",
            "notes": "This is the failed path inside another container.",
        }
    }
    assert not is_working(failed, "recipes/game/failed.json")

    example = {"verification": {"status": "example", "performance": "Great", "notes": "runs"}}
    assert not is_working(example, "recipes/examples/recipe.example.json")

    silent = {"verification": {"status": "verified", "notes": "No result recorded."}}
    assert not is_working(silent, "recipes/game/silent.json")

    working = {
        "game": {"title": "Sample"},
        "target": {"app": "gamehub", "package_name": "com.xiaoji.egggame"},
        "verification": {"status": "verified", "notes": "Owner confirmed the game is WORKING."},
        "provenance": {
            "source_type": "self_test",
            "author": "Nick Moody",
            "captured_at": "2026-10-05",
            "source_url": "https://example.com/recipe",
        },
        "settings": {"env_vars": "", "offline_mode": False, "wine_or_proton": "proton10.0-arm64x-2"},
    }
    assert is_working(working, "recipes/sample/a.json")
    model = build_model(working)
    by_label = {row.label: row.value for section in model["sections"] for row in section.rows}
    assert by_label["Performance"] == MISSING
    assert by_label["Env vars"] == MISSING
    assert by_label["Offline-ready"] == "false"
    assert by_label["Proton / Wine"] == "proton10.0-arm64x-2"
    assert model["app"] == "GameHub"
    assert "GameNative" not in model["verification"]
    assert by_label["Emulator"] == "GameHub (com.xiaoji.egggame)"

    native = {
        "game": {"title": "Native"},
        "target": {"app": "gamenative", "package_name": "app.gamenative", "app_version_min": "1.2.1"},
        "verification": {"status": "community", "performance": "Playable", "notes": ""},
        "provenance": {"source_type": "emuready", "author": "ada", "captured_at": "2026-01-02", "source_url": "https://www.emuready.com/listings/x"},
        "settings": {},
    }
    native_model = build_model(native)
    assert native_model["app"] == "GameNative"
    assert "GameNative" in emulator_name(native)
    assert "EmuReady community report" in native_model["verification"]

    lite = {
        "target": {"app": "gamehub_lite", "package_name": "gamehub.lite"},
        "game": {"title": "Lite"},
        "verification": {"status": "community", "performance": "Great"},
        "provenance": {},
        "settings": {},
    }
    assert build_model(lite)["app"] == "GameHub Lite"
    assert "GameNative" not in emulator_name(lite)


def cmd_check() -> int:
    run_logic_tests()
    cards = expected_cards()
    if not cards:
        print("FAIL: no working recipes found", file=sys.stderr)
        return 1
    names = set(cards)
    if len(names) != len(cards):
        print("FAIL: two working recipes share a card filename", file=sys.stderr)
        return 1
    on_disk = set()
    if CARDS_DIR.exists():
        for path in CARDS_DIR.iterdir():
            if path.name.startswith("."):
                continue
            on_disk.add(path.name)
            if path.suffix.lower() != ".png":
                print(f"FAIL: unexpected file in cards/: {path.name}", file=sys.stderr)
                return 1
    missing = sorted(names - on_disk)
    extra = sorted(on_disk - names)
    if missing or extra:
        for name in missing:
            print(f"FAIL: missing card {name} for {cards[name][0]}", file=sys.stderr)
        for name in extra:
            print(f"FAIL: card {name} does not match a working recipe", file=sys.stderr)
        return 1
    print(f"OK {len(names)} config card(s) match working recipes.")
    for name in sorted(names):
        rel, _data = cards[name]
        print(f"OK cards/{name} <= {rel}")
    return 0


def cmd_report() -> int:
    run_logic_tests()
    cards = expected_cards()
    skipped = []
    for rel, data in walk_recipes():
        if not is_working(data, rel):
            skipped.append((rel, (data.get("verification") or {}).get("status")))
    for name in sorted(cards):
        rel, data = cards[name]
        model = build_model(data)
        missing = ", ".join(missing_labels(model)) or "(none)"
        print(f"- {model['title']}")
        print(f"  file: cards/{name}")
        print(f"  recipe: {rel}")
        print(f"  status/performance: {model['status']} / {model['performance']}")
        print(f"  emulator: {model['app']}")
        print(f"  verification: {model['verification']}")
        if model["warning"]:
            print(f"  settings warning: {model['warning']}")
        print(f"  not yet verified: {missing}")
    if skipped:
        print("Skipped:")
        for rel, status in skipped:
            print(f"  - {rel} ({status})")
    return 0


def load_font(size: int, kind: str):
    from PIL import ImageFont

    candidates = {
        "regular": [
            "/usr/share/fonts/truetype/macos/Inter-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        "medium": [
            "/usr/share/fonts/truetype/macos/Inter-Medium.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        "bold": [
            "/usr/share/fonts/truetype/macos/Inter-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ],
        "mono": [
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ],
        "mono_medium": [
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ],
    }
    for path in candidates[kind]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit(
        "No sans or mono font found. Install Inter or DejaVu, then re-run."
    )


def wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.split(" ") if text else [""]
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.getlength(trial) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        if font.getlength(word) <= max_width:
            current = word
            continue
        chunk = ""
        for ch in word:
            if font.getlength(chunk + ch) <= max_width:
                chunk += ch
            else:
                if chunk:
                    lines.append(chunk)
                chunk = ch
        current = chunk
    if current or not lines:
        lines.append(current)
    return lines


def fit_lines(text: str, font, max_width: int, max_lines: int, suffix: str) -> list[str]:
    lines = wrap_text(text, font, max_width)
    if len(lines) <= max_lines:
        return lines
    trimmed = text
    while trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0] if " " in trimmed else ""
        candidate = f"{trimmed} {suffix}".strip()
        lines = wrap_text(candidate, font, max_width)
        if len(lines) <= max_lines:
            return lines
    return wrap_text(suffix, font, max_width)[:max_lines]


def render_card(recipe: dict, dest: Path) -> None:
    from PIL import Image, ImageDraw

    model = build_model(recipe)
    bg = (16, 17, 20)
    text = (242, 241, 237)
    muted = (154, 156, 163)
    accent = (227, 155, 69)
    line = (42, 44, 51)
    warn_bg = (32, 28, 22)

    image = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 8), fill=accent)

    font_eyebrow = load_font(22, "medium")
    font_title = load_font(52, "bold")
    font_id = load_font(20, "mono")
    font_status = load_font(26, "medium")
    font_source = load_font(20, "mono")
    font_section = load_font(22, "medium")
    font_label = load_font(22, "medium")
    font_value = load_font(26, "mono")
    font_small = load_font(22, "mono")
    font_warn = load_font(22, "medium")
    font_footer = load_font(28, "bold")
    font_footer_sub = load_font(22, "mono")

    margin = 52
    content_w = WIDTH - margin * 2
    label_w = 248
    value_x = margin + label_w + 16
    value_w = WIDTH - margin - value_x
    footer_top = HEIGHT - 156
    # Last ink stays above this line so descenders do not touch the footer rule.
    content_bottom = footer_top - 18

    y = 36
    eyebrow = plain(model["app"]).upper()
    draw.text((margin, y), eyebrow, font=font_eyebrow, fill=accent)
    eyebrow_w = font_eyebrow.getlength(eyebrow)
    draw.text((margin + eyebrow_w + 16, y), "CONFIG CARD", font=font_eyebrow, fill=muted)
    y += 40

    title_lines = wrap_text(model["title"], font_title, content_w)[:3]
    for title_line in title_lines:
        draw.text((margin, y), title_line, font=font_title, fill=text)
        y += 60
    y += 4

    id_text = plain(model["id"])
    draw.text((margin, y), id_text, font=font_id, fill=muted)
    y += 32
    draw.text((margin, y), model["verification"], font=font_status, fill=text)
    y += 36
    source = model["source"]
    for source_line in wrap_text(source, font_source, content_w)[:2]:
        draw.text((margin, y), source_line, font=font_source, fill=muted)
        y += 26
    y += 8

    if model["warning"]:
        warn_lines = wrap_text(model["warning"], font_warn, content_w - 28)
        block_h = 16 + len(warn_lines) * 28 + 8
        draw.rectangle((margin, y, WIDTH - margin, y + block_h), fill=warn_bg)
        draw.rectangle((margin, y, margin + 4, y + block_h), fill=accent)
        text_y = y + 12
        for warn_line in warn_lines:
            draw.text((margin + 18, text_y), warn_line, font=font_warn, fill=accent)
            text_y += 28
        y += block_h + 16

    def row_height(lines: list[str]) -> int:
        return max(40, 4 + len(lines) * 30)

    # Notes and known issues are refit from the space left after the fixed rows.
    prepared = []
    for section in model["sections"]:
        rows_out = []
        for row in section.rows:
            if row.flex:
                rows_out.append((row, [], True))
            else:
                lines = wrap_text(row.value, font_value, value_w)
                rows_out.append((row, lines, False))
        prepared.append((section, rows_out))

    stop = False
    for section, rows_out in prepared:
        if stop or y + 32 > content_bottom:
            break
        draw.text((margin, y), section.title.upper(), font=font_section, fill=accent)
        label_width = font_section.getlength(section.title.upper())
        rule_y = y + 12
        draw.line((margin + label_width + 14, rule_y, WIDTH - margin, rule_y), fill=line, width=1)
        y += 34
        flex_left = sum(1 for _row, _lines, is_flex in rows_out if is_flex)
        for row, lines, is_flex in rows_out:
            color = accent if row.missing else text
            if is_flex:
                remaining = content_bottom - y
                share = remaining // max(1, flex_left)
                flex_left -= 1
                label_h = 26
                line_h = 28
                max_lines = (share - label_h - 8) // line_h
                if max_lines < 1:
                    stop = True
                    break
                lines = fit_lines(
                    row.value,
                    font_small,
                    content_w,
                    max_lines,
                    "Full text is in the recipe.",
                )
                draw.text((margin, y), row.label.upper(), font=font_label, fill=muted)
                y += label_h
                for line_text in lines:
                    draw.text((margin, y), line_text, font=font_small, fill=color)
                    y += line_h
                y += 8
            else:
                block_h = row_height(lines)
                if y + block_h > content_bottom:
                    stop = True
                    break
                draw.text((margin, y + 2), row.label, font=font_label, fill=muted)
                line_y = y
                for line_text in lines:
                    draw.text((value_x, line_y), line_text, font=font_value, fill=color)
                    line_y += 30
                y += block_h

    draw.line((margin, footer_top, WIDTH - margin, footer_top), fill=line, width=1)
    draw.text((margin, footer_top + 18), "MobileMoody", font=font_footer, fill=text)
    draw.text((margin, footer_top + 56), "youtube.com/@MobileMoody", font=font_footer_sub, fill=muted)
    draw.text(
        (margin, footer_top + 86),
        "github.com/coolkidnick/moodygamer-recipes",
        font=font_footer_sub,
        fill=muted,
    )
    draw.rectangle((0, HEIGHT - 8, WIDTH, HEIGHT), fill=accent)

    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, format="PNG", optimize=True)


def cmd_render() -> int:
    run_logic_tests()
    cards = expected_cards()
    if not cards:
        print("FAIL: no working recipes found", file=sys.stderr)
        return 1
    # Remove cards for recipes that are no longer working so --check stays true.
    if CARDS_DIR.exists():
        keep = set(cards)
        for path in CARDS_DIR.iterdir():
            if path.suffix.lower() == ".png" and path.name not in keep:
                path.unlink()
    for name, (rel, data) in sorted(cards.items()):
        dest = CARDS_DIR / name
        render_card(data, dest)
        print(f"Wrote cards/{name} from {rel}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or check recipe config cards.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Confirm cards/*.png matches working recipes. Does not render.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print game, status, emulator, and fields left not yet verified.",
    )
    args = parser.parse_args(argv)
    if args.check:
        return cmd_check()
    if args.report:
        return cmd_report()
    return cmd_render()


if __name__ == "__main__":
    sys.exit(main())
