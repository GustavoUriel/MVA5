# Project Rules & AI Constraints

## 1. Environment & Framework
- **Environment:** Always use the virtual environment in `.venv`.
- **Framework:** Flask 3.x.
- **Style:** Use Functional Blueprints. Do NOT write logic in a single `app.py`. Organise code into discrete blueprint modules.

## 2. Mandatory Modification Protocol (Least Invasive)
- All modifications must be the **least invasive** to the existing code.
- Change as few lines as possible. Avoid rewriting entire functions if a single line change suffices.

## 3. Persistent Logging (MANDATORY)
Every time you perform any change to code, data, or configuration, you must follow this logging ritual:
- **File Naming:** Create a descriptive `.md` file named: `YYMMDDHHmm-intended_repair.md`.
  - Format: 2 digits for year, month, date, hour, and minute. (e.g., 2601161245-fix_route.md).
  - Place the file in folder Agents
- **Persistence:** If a log file already exists for this current agent task, **append** the changes to the existing file instead of creating a new one.
- **Summary:** Every update must include a final summary of what was done at the bottom of the file.