# skills

agent skills i've created, adapted, and/or use in my daily workflow.

## Context

A curated collection of self-contained agent skills, separate from my personal agent configuration. Documentation is in English; output language depends on the request and each skill's instructions.

## Goal

Share useful skills with clear requirements and traceable sources.

- [whatsapp-format](skills/whatsapp-format/SKILL.md): prepare WhatsApp messages and convert common Markdown formatting while preserving the requested language. Includes a Python 3 converter with no third-party dependencies.

## Constraints

Skills live directly under `skills/<name>/`. Copy the complete folder you want into your agent's supported skills directory. Discovery and invocation depend on the agent. Installation does not configure integrations or authorize sending messages.

Each skill keeps its source record and applicable license inside its folder, so they accompany individual copies. Original material is MIT-licensed; third-party material, when included, retains its own licenses and notices. The root [LICENSE](LICENSE) does not replace third-party licenses.

## Examples

With the skill installed, ask: "Format this announcement for WhatsApp without translating it."

To run the converter directly from this repository:

```bash
python3 skills/whatsapp-format/scripts/to_whatsapp.py input.md -o whatsapp.txt
```

Review the result before sending. The converter handles common Markdown patterns; complex markup may need manual adjustment. Without a suitable integration, the agent prepares text for you to copy and send.
