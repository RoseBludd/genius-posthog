#!/usr/bin/env python3
"""Patch PostHog web image with genius. branding (name + terminal logo)."""
from __future__ import annotations

import json
import re
from pathlib import Path

CODE_ROOT = Path("/code")
ICON = Path("/opt/genius/logo-icon.png")
GENIUS = "genius."
GENIUS_LOGO = "/static/icons/genius-logo.png"

LOGO_ASSETS = (
    "posthog-logo-3PNFNDWS.svg",
    "posthog-logo-cloud-KBIZ2GY7.svg",
    "posthog-logo-demo-BMTDYBZ5.svg",
)

JS_REPLACEMENTS = [
    ("/static/assets/posthog-logo-3PNFNDWS.svg", GENIUS_LOGO),
    ("/static/assets/posthog-logo-cloud-KBIZ2GY7.svg", GENIUS_LOGO),
    ("/static/assets/posthog-logo-demo-BMTDYBZ5.svg", GENIUS_LOGO),
    ("`PostHog${g?.cloud?\" Cloud\":\"\"}`", f'`{GENIUS}`'),
    ('alt:`PostHog${g?.cloud?" Cloud":""}`', f'alt:"{GENIUS}"'),
    ("PostHog AI", f"{GENIUS} AI"),
    ("Ask PostHog AI", f"Ask {GENIUS} AI"),
    ("Chat with PostHog AI", f"Chat with {GENIUS} AI"),
    ("Back to PostHog AI", f"Back to {GENIUS} AI"),
    ("Try PostHog Cloud", f"Try {GENIUS}"),
    ("Install PostHog", f"Install {GENIUS}"),
    ("enjoy PostHog!", f"enjoy {GENIUS}!"),
    ("using PostHog", f"using {GENIUS}"),
    ("PostHog is", f"{GENIUS} is"),
    ("PostHog can", f"{GENIUS} can"),
    ("PostHog experience", f"{GENIUS} experience"),
    ("PostHog app", f"{GENIUS} app"),
    ("PostHog human", f"{GENIUS} human"),
    ("PostHog status", f"{GENIUS} status"),
    ("dedicated PostHog", f"dedicated {GENIUS}"),
    ("render PostHog", f"render {GENIUS}"),
    ("| PostHog", f"| {GENIUS}"),
    ('"PostHog"', f'"{GENIUS}"'),
    ("'PostHog'", f"'{GENIUS}'"),
    ("<title>PostHog</title>", f"<title>{GENIUS}</title>"),
    ('content="PostHog"', f'content="{GENIUS}"'),
    ("%cPostHog %c", f"%c{GENIUS} %c"),
    ("fully enjoy PostHog", f"fully enjoy {GENIUS}"),
]

TEXT_SUFFIXES = {".js", ".html", ".json", ".css", ".txt", ".svg", ".xml"}


def write_favicon_ico(dest: Path, icon_bytes: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        import io

        src = Image.open(io.BytesIO(icon_bytes)).convert("RGBA")
        src.save(dest, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
        return
    except Exception:
        pass
    dest.write_bytes(icon_bytes)


def replace_icon_tree(root: Path, icon_bytes: bytes) -> None:
    if not root.is_dir():
        return

    icon_names = (
        "genius-logo.png",
        "favicon.png",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "apple-touch-icon.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
    )
    for sub in ("icons", "assets"):
        base = root / sub
        if not base.is_dir():
            continue
        for name in icon_names:
            (base / name).write_bytes(icon_bytes)
        write_favicon_ico(base / "favicon.ico", icon_bytes)
        for asset in LOGO_ASSETS:
            (base / asset).write_bytes(icon_bytes)

    manifest = root / "site.webmanifest"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        data["name"] = GENIUS
        data["short_name"] = GENIUS
        manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")


def patch_html_text(text: str) -> str:
    parts = re.split(r"(https?://[^\s\"'<>]+)", text)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
            continue
        patched = part
        for old, new in JS_REPLACEMENTS:
            patched = patched.replace(old, new)
        out.append(patched)
    return "".join(out)


def patch_js_text(text: str) -> str:
    patched = text
    for old, new in JS_REPLACEMENTS:
        patched = patched.replace(old, new)
    return patched


def iter_patch_files() -> list[Path]:
    roots = [
        CODE_ROOT / "frontend" / "dist",
        CODE_ROOT / "staticfiles",
        CODE_ROOT / "posthog" / "templates",
        CODE_ROOT / "ee" / "templates",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES)
    return files


def main() -> None:
    if not ICON.exists():
        raise SystemExit(f"Missing icon: {ICON}")
    if not CODE_ROOT.is_dir():
        raise SystemExit(f"Missing code root: {CODE_ROOT}")

    icon_bytes = ICON.read_bytes()
    replace_icon_tree(CODE_ROOT / "staticfiles", icon_bytes)
    replace_icon_tree(CODE_ROOT / "frontend" / "dist", icon_bytes)

    changed = 0
    for path in iter_patch_files():
        try:
            original = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if path.suffix == ".html" or "templates" in path.parts:
            patched = patch_html_text(original)
        elif path.suffix == ".js":
            patched = patch_js_text(original)
        else:
            patched = original
            for old, new in JS_REPLACEMENTS:
                if old in patched:
                    patched = patched.replace(old, new)
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            changed += 1

    print(f"genius. branding patched ({changed} text files, icons updated)")


if __name__ == "__main__":
    main()
