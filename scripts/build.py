#!/usr/bin/env python3
"""Check and render a Swiss Style presentation.

    python3 scripts/build.py --check
    python3 scripts/build.py --doctor
    python3 scripts/build.py --check-content content.json [filled.html]
    python3 scripts/build.py --deliver filled.html content.json
    python3 scripts/build.py --self-test
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "assets" / "templates"
SCHEMAS = ROOT / "references" / "schemas"
TOKENS_PATH = ROOT / "references" / "tokens.json"
DIAGRAMS = ROOT / "assets" / "diagrams"
EXAMPLE = ROOT / "examples" / "slides"

DECK = (959.98, 540.0)

FORBIDDEN = [
    (r"box-shadow", "shadow"),
    (r"text-shadow", "shadow"),
    (r"drop-shadow", "shadow"),
    (r"linear-gradient|radial-gradient|conic-gradient|repeating-gradient", "gradient"),
    (r"border-radius", "radius"),
    (r"@keyframes", "animation"),
    (r"\banimation\s*:", "animation"),
    (r"\btransition\s*:", "animation"),
    (r"(?<![\w-])transform\s*:", "transform"),
    (r"text-align\s*:\s*center", "centered text"),
    (r"text-align\s*:\s*justify", "justified text"),
    (r"text-align\s*:\s*right", "right-aligned text"),
    (r"justify-content\s*:\s*center", "centered group"),
    (r"justify-items\s*:\s*center", "centered group"),
    (r"justify-self\s*:\s*center", "centered group"),
    (r"align-items\s*:\s*center", "centered group"),
    (r"align-content\s*:\s*center", "centered group"),
    (r"align-self\s*:\s*center", "centered group"),
    (r"place-items\s*:\s*center", "centered group"),
    (r"place-content\s*:\s*center", "centered group"),
    (r"place-self\s*:\s*center", "centered group"),
    (r"font-style\s*:\s*(italic|oblique)", "italic"),
    (r"rgba?\(", "non-flat color"),
    (r"hsla?\(", "non-flat color"),
    (r"\bopacity\s*:", "non-flat color"),
    (r"mix-blend-mode|backdrop-filter", "non-flat color"),
    (r"\bblur\(", "blur"),
    (r"background-image", "texture"),
    (r"\burl\s*\(", "texture or file in css"),
    (r"margin\s*:[^;]*\bauto\b", "auto margin"),
    (r"margin-left\s*:\s*auto", "auto margin"),
    (r"margin-right\s*:\s*auto", "auto margin"),
    (r"margin-inline\s*:\s*auto", "auto margin"),
    (r"float\s*:\s*(?!none)\w+", "float"),
    (r":\s*(white|gray|grey|blue|green|orange|purple|yellow|silver|navy|teal|cyan|magenta|pink|brown|beige|ivory|red|black)\b", "named color"),
]

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
BRIEF_REQUIRED = (
    "audience", "job", "template", "formats", "page_target",
    "narrative", "acceptance_checks",
)
BROWSERS = [
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("brave") or "",
]


def load_tokens() -> dict:
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def allowed_hexes(tokens: dict) -> set[str]:
    found = set()
    for key in ("paper", "ink", "red"):
        found.add(normalize_hex(tokens[key]))
    return found


def normalize_hex(value: str) -> str:
    raw = value.strip().lstrip("#").upper()
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return raw


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return text


def hexes_in(text: str) -> set[str]:
    found = set()
    for match in re.finditer(r"#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b", text):
        found.add(normalize_hex(match.group(1)))
    return found


def lint_style(text: str, label: str, tokens: dict) -> list[str]:
    errors = []
    raw = strip_comments(text)
    flat = re.sub(r"\s+", " ", raw)
    if re.search(r"#[0-9A-Fa-f]{8}\b", raw):
        errors.append(f"{label}: translucent hex")
    allowed = allowed_hexes(tokens)
    for color in sorted(hexes_in(raw) - allowed):
        errors.append(f"{label}: color #{color} is outside black / rice-white / #DA291C")
    sizes = set(tokens["font_sizes"])
    for match in re.finditer(r"font-size\s*:\s*([^;}{]+)", raw):
        size = match.group(1).strip()
        if size not in sizes:
            errors.append(f"{label}: font-size {size} is not a registered step")
    for match in re.finditer(r"font-weight\s*:\s*([^;}{]+)", raw):
        weight = match.group(1).strip().lower()
        if weight not in {"400", "700", "normal", "bold", "inherit"}:
            errors.append(f"{label}: font-weight {weight} is not regular or bold")
    for pattern, why in FORBIDDEN:
        if re.search(pattern, flat, flags=re.I):
            errors.append(f"{label}: {why}")
    for attr in re.finditer(r"\b(?:fill|stroke)\s*=\s*['\"]([^'\"]+)['\"]", raw):
        value = attr.group(1).strip()
        if value.lower() in {"none", "currentcolor", "transparent"}:
            continue
        if not value.startswith("#") or normalize_hex(value) not in allowed:
            errors.append(f"{label}: paint {value} is outside the palette")
    if re.search(r"\sstyle\s*=", raw, flags=re.I):
        errors.append(f"{label}: style attribute")
    return errors


def class_list(attrs: str) -> list[str]:
    match = re.search(r'class="([^"]*)"', attrs)
    return match.group(1).split() if match else []


def lint_structure(html: str, label: str) -> list[str]:
    errors = []
    clean = strip_comments(html)
    token = re.compile(r"<(/?)([a-zA-Z][\w:-]*)\b([^>]*)>", re.S)
    stack: list[tuple[str, list[str]]] = []
    for match in token.finditer(clean):
        closing, name, attrs = match.group(1) == "/", match.group(2).lower(), match.group(3)
        if closing:
            for index in range(len(stack) - 1, -1, -1):
                if stack[index][0] == name:
                    del stack[index:]
                    break
            continue
        classes = class_list(attrs)
        start = span = None
        for item in classes:
            if re.fullmatch(r"s(1[0-2]|[1-9])", item):
                start = int(item[1:])
            elif re.fullmatch(r"w(1[0-2]|[1-9])", item):
                span = int(item[1:])
        if "g" in classes and (start or span):
            errors.append(f"{label}: .g is the grid, not a cell")
        if "slide" in classes and (start or span):
            errors.append(f"{label}: .slide is the grid, not a cell")
        if start and span and start + span - 1 > 12:
            errors.append(f"{label}: column {start} span {span} runs past the 12-column grid")
        parents = [frame[1] for frame in stack]
        if "g" in classes and any("g" in parent or "slide" in parent for parent in parents):
            errors.append(f"{label}: nested .g")
        if "slide" in classes and any("g" in parent or "slide" in parent for parent in parents):
            errors.append(f"{label}: nested .slide")
        self_close = attrs.rstrip().endswith("/") or name in VOID
        if not self_close:
            stack.append((name, classes))
    for match in re.finditer(r"<img\b([^>]*)>", clean, flags=re.I):
        attrs = match.group(1)
        classes = class_list(attrs)
        alt = re.search(r'alt="([^"]*)"', attrs)
        if "photo" in classes and (not alt or not alt.group(1).strip()):
            errors.append(f"{label}: a photograph needs an alt fact")
        if "photo" not in classes and "diagram" not in classes and "photo" not in attrs:
            if "diagram" not in attrs and "photo" not in classes:
                if not any(item in {"photo", "diagram"} for item in classes):
                    errors.append(f"{label}: img needs class photo or diagram")
    return errors


def linked_stylesheets(html: str, base: Path) -> list[Path]:
    paths = []
    for href in re.findall(r'<link\b[^>]*href="([^"]+)"', html, flags=re.I):
        if href.startswith(("http://", "https://", "data:")):
            continue
        paths.append((base.parent / href).resolve())
    return paths


def lint_document(path: Path, tokens: dict, template: bool) -> list[str]:
    html = path.read_text(encoding="utf-8")
    errors = lint_style(html, path.name, tokens)
    errors.extend(lint_structure(html, path.name))
    sheets = linked_stylesheets(html, path)
    if not any(sheet.name == "swiss.css" for sheet in sheets):
        errors.append(f"{path.name}: link swiss.css")
    for sheet in sheets:
        if not sheet.exists():
            errors.append(f"{path.name}: missing stylesheet {sheet.name}")
            continue
        errors.extend(lint_style(sheet.read_text(encoding="utf-8"), sheet.name, tokens))
    if 'content="Swiss Style"' not in html:
        errors.append(f"{path.name}: generator meta must stay Swiss Style")
    stripped = strip_comments(html)
    if template and "{{" not in stripped:
        errors.append(f"{path.name}: template is missing placeholders")
    if not template and "{{" in stripped:
        errors.append(f"{path.name}: leftover placeholder")
    if not any("deck" in class_list(attrs) for attrs in re.findall(r"<html\b([^>]*)>", stripped, flags=re.I)):
        errors.append(f"{path.name}: slides use html class deck")
    visible = visible_text(html)
    if re.search(r"(?m)^\s{0,3}#{1,6}\s", visible) or "**" in visible or "__" in visible:
        errors.append(f"{path.name}: markdown residue")
    return errors


def visible_text(html: str) -> str:
    raw = strip_comments(html)
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return html_lib.unescape(raw)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_tree(tokens: dict) -> list[str]:
    errors = lint_style((TEMPLATES / "swiss.css").read_text(encoding="utf-8"), "swiss.css", tokens)
    css = (TEMPLATES / "swiss.css").read_text(encoding="utf-8")
    for key in ("paper", "ink", "red"):
        if tokens[key].lower() not in css.lower():
            errors.append(f"swiss.css: missing {tokens[key]}")
    if "repeat(12" not in css:
        errors.append("swiss.css: the page grid is not 12 columns")
    for path in sorted(TEMPLATES.glob("*.html")):
        errors.extend(lint_document(path, tokens, template=True))
    if DIAGRAMS.exists():
        for path in sorted(DIAGRAMS.glob("*.svg")):
            errors.extend(lint_style(path.read_text(encoding="utf-8"), path.name, tokens))
    example_html = EXAMPLE / "slides.html"
    if example_html.exists():
        errors.extend(lint_document(example_html, tokens, template=False))
    return dedupe(errors)


def dedupe(items: list[str]) -> list[str]:
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def validate_instance(instance, schema, path: str) -> list[str]:
    errors = []
    if not isinstance(schema, dict):
        return errors
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(instance, dict):
            return [f"{path} should be an object"]
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key} missing")
        for key, value in instance.items():
            if key not in props:
                errors.append(f"{path}.{key} is not in the schema")
            else:
                errors.extend(validate_instance(value, props[key], f"{path}.{key}"))
        return errors
    if kind == "array":
        if not isinstance(instance, list):
            return [f"{path} should be an array"]
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path} needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path} has more than {schema['maxItems']} items")
        for index, value in enumerate(instance, start=1):
            errors.extend(validate_instance(value, schema.get("items", {}), f"{path}[{index}]"))
        return errors
    if kind == "string":
        if not isinstance(instance, str):
            return [f"{path} should be a string"]
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path} is shorter than {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path} is longer than {schema['maxLength']}")
        return errors
    if kind in {"number", "integer"}:
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            return [f"{path} should be a number"]
        if kind == "integer" and not isinstance(instance, int):
            return [f"{path} should be an integer"]
        return errors
    return errors


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {path.name}: root should be an object")
    return data


def check_content(path: Path, html: Path | None = None) -> tuple[list[str], list[str]]:
    data = load_json(path)
    errors = []
    warnings = []
    extra = set(data) - {"type", "lang", "brief", "content"}
    if extra:
        errors.append("envelope has extra keys: " + ", ".join(sorted(extra)))
    for key in ("type", "lang", "brief", "content"):
        if key not in data:
            errors.append(f"envelope missing {key}")
    if errors:
        return errors, warnings
    if data["type"] != "slides":
        return ["type must be slides; this skill supports presentations only"], warnings
    if not isinstance(data["lang"], str) or not data["lang"].strip():
        errors.append("lang is empty")
    brief = data["brief"]
    if not isinstance(brief, dict):
        return ["brief should be an object"], warnings
    for key in BRIEF_REQUIRED:
        if key not in brief:
            errors.append(f"brief.{key} missing")
    if brief.get("template") != "slides":
        errors.append("brief.template must be slides")
    formats = brief.get("formats", [])
    if not isinstance(formats, list) or not formats or any(item not in {"html", "pdf", "png"} for item in formats):
        errors.append("brief.formats must list html, pdf, or png")
    page_target = brief.get("page_target")
    if type(page_target) is not int or page_target < 1:
        errors.append("brief.page_target should be a positive slide count")
    schema_path = SCHEMAS / f"{data['type']}.json"
    if not schema_path.exists():
        errors.append(f"no schema for {data['type']}")
        return errors, warnings
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors.extend(validate_instance(data["content"], schema, "content"))
    if not errors and len(data["content"]["slides"]) != page_target:
        errors.append("brief.page_target must match content.slides, including the title slide")
    if html is not None:
        if not html.exists():
            errors.append(f"missing {html}")
            return errors, warnings
        visible = norm(visible_text(html.read_text(encoding="utf-8")))
        for leaf in string_leaves(data["content"]):
            if len(leaf.strip()) < 2:
                continue
            if norm(leaf) not in visible:
                errors.append(f"content not in the document: {leaf[:80]}")
    return errors, warnings


def string_leaves(node) -> list[str]:
    found = []
    if isinstance(node, str):
        found.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            found.extend(string_leaves(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(string_leaves(value))
    return found


def gaps(html: str) -> list[str]:
    return re.findall(r"\[DATA NEEDED:[^\]]+\]", html)


def warnings_in(html: str) -> list[str]:
    visible = visible_text(html).lower()
    found = []
    for word in ("lorem", "ipsum", "tbd", "todo"):
        if re.search(rf"\b{word}\b", visible):
            found.append(word)
    return found


def find_browser() -> str | None:
    for candidate in BROWSERS:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def pdf_pages(path: Path) -> int:
    data = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?!s)", data))


def pdf_boxes(path: Path) -> list[tuple[float, float]]:
    data = path.read_bytes()
    boxes = []
    for match in re.finditer(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", data):
        width = float(match.group(3)) - float(match.group(1))
        height = float(match.group(4)) - float(match.group(2))
        boxes.append((width, height))
    return boxes


def close_box(actual: tuple[float, float], expected: tuple[float, float]) -> bool:
    return abs(actual[0] - expected[0]) < 12 and abs(actual[1] - expected[1]) < 12


def _run_bounded(cmd: list[str], timeout: int) -> tuple[int | None, bytes]:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        _, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return None, b""
    return proc.returncode, err or b""


def render_pdf(html: Path, pdf: Path) -> str | None:
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        HTML = None
    if HTML is not None:
        HTML(filename=str(html), base_url=str(html.parent)).write_pdf(str(pdf))
        return "weasyprint"
    browser = find_browser()
    if not browser:
        return None
    with tempfile.TemporaryDirectory(prefix="swiss-style-") as tmp:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-background-networking",
            "--no-pdf-header-footer",
            "--virtual-time-budget=8000",
            f"--user-data-dir={tmp}",
            f"--print-to-pdf={pdf.resolve()}",
            html.resolve().as_uri(),
        ]
        code, err = _run_bounded(cmd, 20)
        if code is None:
            return "timeout"
        if code != 0 or not pdf.exists():
            cmd[1] = "--headless"
            code, err = _run_bounded(cmd, 20)
            if code is None:
                return "timeout"
            if code != 0 or not pdf.exists():
                tail = err.decode("utf-8", "replace")[-300:].strip()
                if tail:
                    print(f"WARN: browser pdf failed: {tail}")
                return None
    return Path(browser).name


def deliver(html_path: Path, content_path: Path) -> int:
    tokens = load_tokens()
    errors = lint_document(html_path, tokens, template=False)
    content_errors, _ = check_content(content_path, html_path)
    errors.extend(content_errors)
    html = html_path.read_text(encoding="utf-8")
    for gap in gaps(html):
        print(f"GAP: {gap}")
    for word in warnings_in(html):
        print(f"WARN: residue {word}")
    data = load_json(content_path) if content_path.exists() else {}
    if not errors:
        pdf = html_path.with_suffix(".pdf")
        try:
            engine = render_pdf(html_path, pdf)
        except Exception as exc:
            engine = None
            print(f"WARN: pdf renderer failed ({exc.__class__.__name__})")
        if engine == "timeout":
            print("WARN: pdf renderer timed out. Page count unconfirmed.")
        elif engine is None:
            print("WARN: no pdf renderer. Page count unconfirmed.")
        else:
            count = pdf_pages(pdf)
            boxes = pdf_boxes(pdf)
            print(f"PDF: {pdf} via {engine}, {count} page(s)")
            expect = DECK
            for box in boxes:
                if not close_box(box, expect) and not close_box((box[1], box[0]), expect):
                    print(f"WARN: page box {box[0]:.1f}x{box[1]:.1f} pt, expected {expect[0]:.0f}x{expect[1]:.0f}")
                    break
            target = data.get("brief", {}).get("page_target") if isinstance(data.get("brief"), dict) else None
            if isinstance(target, int) and count != target:
                print(f"WARN: {count} page(s), contract is {target}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print("FAILED")
        return 1
    print("READY")
    return 0


def doctor() -> int:
    tokens = load_tokens()
    print(f"python: {sys.version.split()[0]}")
    print(f"palette: {tokens['ink']} / {tokens['paper']} / {tokens['red']}")
    print(f"grid: {tokens['columns']} columns, gutter {tokens['gutter']}")
    try:
        import weasyprint  # type: ignore
        print(f"weasyprint: {weasyprint.__version__}")
    except Exception:
        print("weasyprint: not installed")
    browser = find_browser()
    print(f"browser: {browser or 'not found'}")
    for label, pattern in (
        ("helvetica", "/System/Library/Fonts/Helvetica.ttc"),
        ("pingfang", "/System/Library/Fonts/PingFang.ttc"),
    ):
        print(f"{label}: {'yes' if Path(pattern).exists() else 'missing'} ({pattern})")
    if not browser:
        print("WARN: PDF needs WeasyPrint or Chrome, Brave, Edge, or Chromium")
    return 0


def self_test() -> int:
    tokens = load_tokens()
    errors = check_tree(tokens)
    probe = lint_style("p { text-align: center; color: #00aaee; font-weight: 500; box-shadow: 0 1px 2px #111111; }", "probe", tokens)
    if len(probe) < 3:
        errors.append(f"linter probe missed a violation: {probe}")
    overflow = lint_structure('<div class="g"><p class="s10 w4">x</p></div>', "probe")
    if not any("past the 12-column" in item for item in overflow):
        errors.append("linter probe missed an overflow column")
    nested = lint_structure('<div class="g"><div class="g"></div></div>', "probe")
    if not any("nested" in item for item in nested):
        errors.append("linter probe missed a nested grid")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print("FAILED")
        return 1
    content_errors, _ = check_content(EXAMPLE / "content.json", EXAMPLE / "slides.html")
    for error in content_errors:
        print(f"ERROR: {error}")
    if content_errors:
        print("FAILED")
        return 1
    with tempfile.TemporaryDirectory(prefix="swiss-style-check-") as tmp:
        path = Path(tmp) / "content.json"
        for kind in ("one-pager", "resume", "letter", "portfolio", "long-doc", "equity-report", "changelog", "landing-page"):
            data = load_json(EXAMPLE / "content.json")
            data["type"] = data["brief"]["template"] = kind
            path.write_text(json.dumps(data), encoding="utf-8")
            rejected, _ = check_content(path)
            if not any("presentations only" in error for error in rejected):
                print(f"ERROR: accepted non-presentation type {kind}")
                return 1
        for target in ("screen", 0, True, 2, 4):
            data = load_json(EXAMPLE / "content.json")
            data["brief"]["page_target"] = target
            path.write_text(json.dumps(data), encoding="utf-8")
            rejected, _ = check_content(path)
            if not any("brief.page_target" in error for error in rejected):
                print(f"ERROR: accepted invalid slide count {target}")
                return 1
        html_path = Path(tmp) / "filled.html"
        html = (EXAMPLE / "slides.html").read_text(encoding="utf-8")
        html_path.write_text(html.replace('class="deck"', ''), encoding="utf-8")
        if not any("html class deck" in error for error in lint_document(html_path, tokens, template=False)):
            print("ERROR: accepted a filled document without html class deck")
            return 1
    code = deliver(EXAMPLE / "slides.html", EXAMPLE / "content.json")
    if code != 0:
        return code
    print("SELF-TEST OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and render a Swiss Style presentation.")
    parser.add_argument("--check", action="store_true", help="lint templates, diagrams, tokens, and the specimen")
    parser.add_argument("--doctor", action="store_true", help="report the renderer and fonts")
    parser.add_argument("--self-test", action="store_true", help="lint, then deliver the specimen")
    parser.add_argument("--check-content", type=Path, help="validate content.json")
    parser.add_argument("--deliver", nargs=2, type=Path, metavar=("HTML", "CONTENT"), help="lint, cover, and render")
    parser.add_argument("html", nargs="?", type=Path, help="filled html when using --check-content")
    args = parser.parse_args()

    if args.doctor:
        return doctor()
    if args.self_test:
        return self_test()
    if args.check:
        errors = check_tree(load_tokens())
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            print("FAILED")
            return 1
        print("READY")
        return 0
    if args.check_content:
        errors, _ = check_content(args.check_content, args.html)
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            print("FAILED")
            return 1
        print("READY")
        return 0
    if args.deliver:
        return deliver(args.deliver[0], args.deliver[1])
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
