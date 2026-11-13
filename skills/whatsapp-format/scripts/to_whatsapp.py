#!/usr/bin/env python3
"""Convert Markdown into WhatsApp-formatted text without translating it.

Usage:
  python to_whatsapp.py input.md              # write to stdout
  cat input.md | python to_whatsapp.py        # read from stdin
  python to_whatsapp.py input.md -o output.txt # write a UTF-8 file

Conversions:
  **bold** / __bold__        -> *bold*
  *italic*                  -> _italic_
  ~~strike~~                -> ~strike~
  # heading                 -> *heading*
  [text](url)               -> text: url
  table                     -> bullet list using the first column as a label
  ---                       -> removed
  * item / + item            -> - item
  - [x] task                -> - ✅ task
  code fences               -> triple backticks without language tags

Code content is protected from emphasis conversion. Inline code delimiters
are normalized to single backticks and surrounding whitespace is trimmed.
This is a best-effort converter, not a full Markdown parser.
"""
import argparse
import re
import sys

BOLD = "\ue000"  # WhatsApp bold placeholder, replaced with * at the end
STASH_OPEN = "\ue001"
STASH_CLOSE = "\ue002"

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
HR_RE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)(?:\s+#+)?\s*$")
TASK_RE = re.compile(r"^(\s*)[-*+]\s+\[([ xX])\]\s+(.*)$")
BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
QUOTE_RE = re.compile(r"^\s{0,3}(?:>\s?)+(.*)$")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_TAG_RE = re.compile(
    r"</?(?:p|div|span|b|i|u|em|strong|ul|ol|li|h[1-6]|table|thead|tbody|tr|td|th"
    r"|hr|a|img|details|summary|center|sub|sup|kbd)(?:\s[^>]*)?/?>",
    re.I,
)


def make_stash():
    items = []
    pat = re.compile(f"{STASH_OPEN}(\\d+){STASH_CLOSE}")

    def put(s):
        items.append(s)
        return f"{STASH_OPEN}{len(items) - 1}{STASH_CLOSE}"

    def restore(text):
        while pat.search(text):
            text = pat.sub(lambda m: items[int(m.group(1))], text)
        return text

    return put, restore


def _link(m):
    label, url = m.group(1).strip(), m.group(2)
    return url if (not label or label == url) else f"{label}: {url}"


def inline(text, put):
    text = LINK_RE.sub(_link, text)
    # Protect URLs from emphasis patterns (underscores and tildes in URLs).
    text = re.sub(r"https?://[^\s<>\]]+", lambda m: put(m.group(0)), text)
    text = re.sub(
        r"(\*\*\*|___)(?=\S)(.+?)(?<=\S)\1",
        lambda m: f"{BOLD}_{m.group(2)}_{BOLD}",
        text,
    )
    text = re.sub(
        r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1",
        lambda m: f"{BOLD}{m.group(2)}{BOLD}",
        text,
    )
    text = re.sub(r"~~(?=\S)(.+?)(?<=\S)~~", r"~\1~", text)
    text = re.sub(
        r"(?<![\w*])\*(?=[^\s*])([^*\n]+?)(?<=[^\s*])\*(?![\w*])", r"_\1_", text
    )
    return text


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", line)]


def table_row(headers, cells):
    first = re.sub(r"\*\*|__", "", cells[0]) if cells else ""
    if len(headers) <= 2:
        rest = cells[1] if len(cells) > 1 else ""
    else:
        parts = []
        for h, c in zip(headers[1:], cells[1:]):
            if c:
                parts.append(f"{h}: {c}" if h else c)
        rest = ", ".join(parts)
    head = f"{BOLD}{first}{BOLD}" if first else ""
    if head and rest:
        return f"- {head}: {rest}"
    return f"- {head or rest}".rstrip()


def convert_tables(lines):
    out, i = [], 0
    while i < len(lines):
        if (
            "|" in lines[i]
            and i + 1 < len(lines)
            and "|" in lines[i + 1]
            and SEP_RE.match(lines[i + 1])
        ):
            headers = split_row(lines[i])
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                out.append(table_row(headers, split_row(lines[i])))
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return out


def convert_line(line, put):
    if HR_RE.match(line):
        return ""
    m = HEADER_RE.match(line)
    if m:
        body = inline(m.group(1), put).replace(BOLD, "").strip()
        return f"{BOLD}{body}{BOLD}" if body else ""
    m = TASK_RE.match(line)
    if m:
        mark = "✅" if m.group(2) in "xX" else "⬜"
        return f"{m.group(1)}- {mark} {inline(m.group(3), put)}"
    m = BULLET_RE.match(line)
    if m:
        return f"{m.group(1)}- {inline(m.group(2), put)}"
    m = ORDERED_RE.match(line)
    if m:
        return f"{m.group(1)}{m.group(2)}. {inline(m.group(3), put)}"
    m = QUOTE_RE.match(line)
    if m:
        return f"> {inline(m.group(1), put)}"
    return inline(line, put)


def convert_chunk(chunk):
    put, restore = make_stash()
    chunk = re.sub(
        r"(`+)(.+?)\1", lambda m: put("`" + m.group(2).strip() + "`"), chunk
    )
    chunk = re.sub(r"<(https?://[^>\s]+)>", r"\1", chunk)
    chunk = re.sub(r"<br\s*/?>", "\n", chunk, flags=re.I)
    chunk = HTML_TAG_RE.sub("", chunk)
    lines = convert_tables(chunk.split("\n"))
    text = "\n".join(convert_line(line, put) for line in lines)
    text = restore(text).replace(BOLD, "*")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def convert(text):
    text = text.replace("\r\n", "\n")
    out, chunk, fence = [], [], None

    def flush():
        if chunk:
            out.append(convert_chunk("\n".join(chunk)))
            chunk.clear()

    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence is None and m:
            flush()
            fence = m.group(1)
            out.append("```")
        elif fence is not None:
            closing = rf"\s{{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*"
            if re.fullmatch(closing, line):
                out.append("```")
                fence = None
            else:
                out.append(line)
        else:
            chunk.append(line)
    flush()
    if fence is not None:
        out.append("```")
    return "\n".join(out).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Convert Markdown to WhatsApp-formatted text")
    ap.add_argument("file", nargs="?", help="Markdown input file (stdin if omitted)")
    ap.add_argument("-o", "--out", help="output file (stdout if omitted)")
    args = ap.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            src = f.read()
    else:
        sys.stdin.reconfigure(encoding="utf-8")
        src = sys.stdin.read()

    result = convert(src)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
