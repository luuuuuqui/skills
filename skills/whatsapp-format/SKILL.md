---
name: whatsapp-format
description: Write or reformat text for WhatsApp messages, group announcements, summaries, lists, schedules, and code snippets. Use when the user asks for WhatsApp-ready text or existing Markdown converted to WhatsApp formatting, in any language. Supports manual copying or delivery through an available integration. Includes a Markdown to WhatsApp converter script.
---

# WhatsApp formatting

## Context

An agent may have access to WhatsApp through an API or another integration. If no suitable integration is available, access is missing, or delivery cannot be completed, provide the formatted text for the user to copy and send manually. Do not assume API access is always available or always absent.

This skill handles formatting; sending requires the user's authorization and a suitable tool. Preparing a message does not itself authorize sending it. The bundled converter only transforms text and does not call WhatsApp.

## Objective

Produce copyable WhatsApp text in the language requested by the user. Preserve the source language when reformatting unless translation is requested. Follow the user's tone and capitalization preferences; do not force English or lowercase text. The converter changes markup, not language or letter case.

## Constraints

### Deliver the formatted text

For manual copying, put the finished message in a fenced code block. Chat UIs render Markdown, so `*bold*` shows up as italic and the asterisks can be lost when copied. A code block preserves the raw characters.

For authorized delivery through an available integration, pass the raw WhatsApp-formatted message without the outer chat code fence. Preserve any backticks that belong to the message itself. Report the actual delivery result; if it is uncertain, state that uncertainty rather than claiming success or automatically sending again.

For manual copying:

- Use an outer fence longer than any backtick run inside the message (for example, four backticks around a message containing triple backticks).
- Put only the message in the block. At most one short line outside it.
- If the message is long (roughly 40+ lines), also save it as `whatsapp.txt` and hand over the file.

### Syntax

- bold: `*text*`
- italic: `_text_`
- strikethrough: `~text~`
- bold and italic: `*_text_*`
- monospace block, can span lines: ```` ```text``` ````
- inline code: `` `text` ``
- bulleted list: `- text` or `* text`
- numbered list: `1. text`
- quote: `> text`, repeated on every line of the quote

Emphasis markers must touch the text with no space inside (`* text *` does nothing), and each pair must close on the same line. Triple-backtick monospace blocks can span multiple lines.

### What does not render

WhatsApp shows these as raw symbols or raw text:

- `**bold**` (WhatsApp bold is a single asterisk)
- headings (`#`)
- tables
- horizontal rules (`---`)
- `[text](url)` links
- underline, spoilers, font size, HTML

### Writing rules

1. Headings are a bold line, like `*Summary*`, followed by a blank line.
2. Turn tables into bullet lines: `- *label*: value`.
3. Links are a bare URL. Put a short label before it, on the same line or the line above.
4. Short paragraphs, one idea each. The reader is on a phone.
5. Put file names, commands, ids and anything with underscores in backticks. Paired underscores can be read as italic markers, and backticks rule that out.
6. Keep lists flat. Nested lists are not in WhatsApp's formatting docs and have not been tested here.
7. Add emojis only if the user's own tone uses them.
8. Follow the user's language and casing preferences. This skill only governs syntax.

### Converting existing markdown

`scripts/to_whatsapp.py` requires Python 3 with only the standard library. Run it from this skill's directory, or use its absolute path; input and output paths are relative to the working directory. Files are read and written as UTF-8.

```
python3 scripts/to_whatsapp.py input.md              # stdout
cat input.md | python3 scripts/to_whatsapp.py        # stdin
python3 scripts/to_whatsapp.py input.md -o out.txt   # file
```

It converts `**bold**`, `*italic*`, `~~strike~~`, headings, links, tables, `* item` bullets, task lists (`- [x]` becomes `- ✅`, `- [ ]` becomes `- ⬜`) and strips supported HTML tags. It protects code content from emphasis conversion and removes horizontal rules. It normalizes code fences to triple backticks, strips language tags, and trims surrounding whitespace inside inline code.

It does not flatten nested lists (indentation is kept), and it has no dedicated support for setext headings, footnotes or math. It is a best-effort regex converter, not a full Markdown parser: complex links, escaped markup, and code containing backtick delimiters need manual review. It is intended for Markdown input; do not run it on already formatted WhatsApp text, where `*bold*` would become `_bold_`. Read the output once before delivering it.

### Check before sending

- outside literal code, no Markdown `**bold**`, `#` headings, `[text](url)`, table separator rows or horizontal rules left
- emphasis markers touch the text and close on the same line; multiline monospace blocks have matching triple backticks
- for manual copying, the message is inside a fence longer than any backtick run inside; integration payloads omit that outer fence

### Limits

- Formatting reference: [WhatsApp Help Center](https://faq.whatsapp.com/539178204879377/).
- Older WhatsApp versions show the newer formats (lists, quotes, inline code) as raw symbols.
- WhatsApp Business API templates are outside this skill's scope. Check the current provider documentation for their formatting and length restrictions.

## Examples

Requests such as "Format this announcement for WhatsApp" or "Convert this Markdown summary into a WhatsApp message" should activate this skill. Equivalent requests in other languages should work the same way.

Example of a final reply:

````
```
*Friday meeting*

- Time: 2 p.m.
- Location: Room 3

Full agenda:
https://example.com/agenda
```
````

(The outer four backticks are only for this example. In a real reply the message sits inside one plain fence.)
