# Iris AI Skills

This directory allows you to inject custom skills, rules, or persona guidelines directly into specific AI model roles.

## How it works
To add custom instructions to a specific model role, create a directory named after that role (e.g. `skills/code/` or `skills/math/`). Inside that directory, you can drop as many `.md` or `.txt` files as you like.

When the system boots up or switches roles, it will automatically look for these directories, read all the files inside them, and append their contents to the model's base system prompt.

### Supported Roles Directories
You can create directories for any of the following roles:
- `triage/`
- `router/`
- `math/`
- `code/`
- `reasoning/`
- `general/`
- `vision/`
- `control/`
- `reviewer/`

## Example
If you create a file `skills/code/style_guidelines.md` containing:
```text
Always use explicit type hints for all Python code. Do not use single-letter variables unless it is a loop counter.
```
And another file `skills/code/banned_functions.md` containing:
```text
Never use the `eval()` function under any circumstances.
```
The coding specialist model will absorb both of these skills and adhere to them during generation.
