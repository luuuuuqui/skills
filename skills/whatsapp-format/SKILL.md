---
name: whatsapp-format
description: write or reformat text for whatsapp messages, group announcements, summaries, lists, schedules, and code snippets. use when the user asks for whatsapp-ready text or existing markdown converted to whatsapp formatting, in any language. supports manual copying or delivery through an available integration. includes a markdown to whatsapp converter script.
metadata:
  author: "https://github.com/luuuuuqui"
---

# whatsapp formatting

## context

an agent may have access to whatsapp through an api or another integration. if no suitable integration is available, access is missing, or delivery cannot be completed, provide the formatted text for the user to copy and send manually. do not assume api access is always available or always absent.

this skill handles formatting; sending requires the user's authorization and a suitable tool. preparing a message does not itself authorize sending it. the bundled converter only transforms text and does not call whatsapp.

## objective

produce copyable whatsapp text in the language requested by the user. preserve the source language when reformatting unless translation is requested. follow the user's tone and capitalization preferences; do not force english or lowercase text. the converter changes markup, not language or letter case.

## constraints

### deliver the formatted text

for manual copying, put the finished message in a fenced code block. chat uis render markdown, so `*bold*` shows up as italic and the asterisks can be lost when copied. a code block preserves the raw characters.

for authorized delivery through an available integration, pass the raw whatsapp-formatted message without the outer chat code fence. preserve any backticks that belong to the message itself. report the actual delivery result; if it is uncertain, state that uncertainty rather than claiming success or automatically sending again.

for manual copying:

- use an outer fence longer than any backtick run inside the message (for example, four backticks around a message containing triple backticks).
- put only the message in the block. at most one short line outside it.
- if the message is long (roughly 40+ lines), also save it as `whatsapp.txt` and hand over the file.

### syntax

- bold: `*text*`
- italic: `_text_`
- strikethrough: `~text~`
- bold and italic: `*_text_*`
- monospace block, can span lines: ```` ```text``` ````
- inline code: `` `text` ``
- bulleted list: `- text` or `* text`
- numbered list: `1. text`
- quote: `> text`, repeated on every line of the quote

emphasis markers must touch the text with no space inside (`* text *` does nothing), and each pair must close on the same line. triple-backtick monospace blocks can span multiple lines.

### what does not render

whatsapp shows these as raw symbols or raw text:

- `**bold**` (whatsapp bold is a single asterisk)
- headings (`#`)
- tables
- horizontal rules (`---`)
- `[text](url)` links
- underline, spoilers, font size, html

### writing rules

1. headings are a bold line, like `*summary*`, followed by a blank line.
2. turn tables into bullet lines: `- *label*: value`.
3. links are a bare url. put a short label before it, on the same line or the line above.
4. short paragraphs, one idea each. the reader is on a phone.
5. put file names, commands, ids and anything with underscores in backticks. paired underscores can be read as italic markers, and backticks rule that out.
6. keep lists flat. nested lists are not in whatsapp's formatting docs and have not been tested here.
7. add emojis only if the user's own tone uses them.
8. follow the user's language and casing preferences. this skill only governs syntax.

### converting existing markdown

`scripts/to_whatsapp.py` requires python 3 with only the standard library. run it from this skill's directory, or use its absolute path; input and output paths are relative to the working directory. files are read and written as utf-8.

```
python3 scripts/to_whatsapp.py input.md              # stdout
cat input.md | python3 scripts/to_whatsapp.py        # stdin
python3 scripts/to_whatsapp.py input.md -o out.txt   # file
```

it converts `**bold**`, `*italic*`, `~~strike~~`, headings, links, tables, `* item` bullets, task lists (`- [x]` becomes `- ✅`, `- [ ]` becomes `- ⬜`) and strips supported html tags. it protects code content from emphasis conversion and removes horizontal rules. it normalizes code fences to triple backticks, strips language tags, and trims surrounding whitespace inside inline code.

it does not flatten nested lists (indentation is kept), and it has no dedicated support for setext headings, footnotes or math. it is a best-effort regex converter, not a full markdown parser: complex links, escaped markup, and code containing backtick delimiters need manual review. it is intended for markdown input; do not run it on already formatted whatsapp text, where `*bold*` would become `_bold_`. read the output once before delivering it.

### check before sending

- outside literal code, no markdown `**bold**`, `#` headings, `[text](url)`, table separator rows or horizontal rules left
- emphasis markers touch the text and close on the same line; multiline monospace blocks have matching triple backticks
- for manual copying, the message is inside a fence longer than any backtick run inside; integration payloads omit that outer fence

### limits

- formatting reference: [whatsapp help center](https://faq.whatsapp.com/539178204879377/).
- older whatsapp versions show the newer formats (lists, quotes, inline code) as raw symbols.
- whatsapp business api templates are outside this skill's scope. check the current provider documentation for their formatting and length restrictions.

## examples

requests such as "format this announcement for whatsapp" or "convert this markdown summary into a whatsapp message" should activate this skill. equivalent requests in other languages should work the same way.

example of a final reply:

````
```
*friday meeting*

- time: 2 p.m.
- location: room 3

full agenda:
https://example.com/agenda
```
````

(the outer four backticks are only for this example. in a real reply the message sits inside one plain fence.)
