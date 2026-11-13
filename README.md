# skills

agent skills i've created, adapted, and/or use in my daily workflow.

## context

a curated collection of self-contained agent skills, separate from my personal agent configuration. documentation is in english; output language depends on the request and each skill's instructions.

## goal

share useful skills with clear requirements and traceable sources.

- [whatsapp-format](skills/whatsapp-format/SKILL.md): prepare whatsapp messages and convert common markdown formatting while preserving the requested language. includes a python 3 converter with no third-party dependencies.

## constraints

skills live directly under `skills/<name>/`. copy the complete folder you want into your agent's supported skills directory. discovery and invocation depend on the agent. installation does not configure integrations or authorize sending messages.

each skill keeps its source record and applicable license inside its folder, so they accompany individual copies. original material is mit-licensed; third-party material, when included, retains its own licenses and notices. the root [license](LICENSE) does not replace third-party licenses.

## examples

with the skill installed, ask: "format this announcement for whatsapp without translating it."

to run the converter directly from this repository:

```bash
python3 skills/whatsapp-format/scripts/to_whatsapp.py input.md -o whatsapp.txt
```

review the result before sending. the converter handles common markdown patterns; complex markup may need manual adjustment. without a suitable integration, the agent prepares text for you to copy and send.
