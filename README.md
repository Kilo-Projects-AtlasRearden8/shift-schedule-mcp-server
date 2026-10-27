# Shift Schedule MCP Server

A friendly, local-first MCP server for tracking work shifts, days off, and rotation patterns — built with healthcare workers in mind.

## What is this?

This is an **MCP server**. MCP (Model Context Protocol) is a way for AI assistants to talk to tools and data on your computer. Think of it like a USB port for AI: it lets an AI assistant (like Claude or another model) safely read and update your shift schedule over a simple standard connection called **stdio**.

Instead of your schedule living in someone else's cloud, it stays on your machine in plain JSON files. You stay in control of your data.

## Who this is for

- **Healthcare workers** (nurses, aides, techs, and anyone on a rotating schedule) who want a simple, private way to track shifts and days off
- **AI beginners** learning how MCP works — this server is small, tested, and easy to read
- **Asdale Dynamics, LLC** projects and tools that need a practical, local-first scheduling example

> **Important:** This tool is for organization and education only. It does not provide medical advice and is not a replacement for professional scheduling software.

## What it tracks

| Category | What you store |
|----------|----------------|
| **Shifts** | Worker, date, start/end times, department, notes |
| **Days off** | Worker, date, optional reason |
| **Rotation patterns** | Named rotation cycles (for example: 2 days on, 2 days off) with a list of workers |

## The 15 tools an AI assistant can call

**Shifts**
- `list_shifts` — List all shifts, optionally filter by worker and/or date
- `get_shift` — Get one shift by its ID
- `add_shift` — Add a new shift
- `update_shift` — Change an existing shift
- `delete_shift` — Remove a shift

**Days off**
- `list_days_off` — List all days off, optionally filter by worker and/or date
- `get_day_off` — Get one day off by its ID
- `add_day_off` — Add a new day off
- `update_day_off` — Change an existing day off
- `delete_day_off` — Remove a day off

**Rotation patterns**
- `list_rotations` — List rotation patterns, optionally filter by worker
- `get_rotation` — Get one rotation by its ID
- `add_rotation` — Add a rotation pattern
- `update_rotation` — Change a rotation pattern
- `delete_rotation` — Remove a rotation pattern

## Where data lives

By default, data is stored in three JSON files under `~/.shift-schedule-mcp/`:

- `shifts.json`
- `days_off.json`
- `rotations.json`

You can point it somewhere else with the `SHIFT_SCHEDULE_DATA_DIR` environment variable.

## Install

You need Python 3.10 or newer.

```bash
# 1. Clone the project (or unzip it)
cd shift-schedule-mcp-server

# 2. Create a virtual environment (keeps things tidy and local)
python3 -m venv venv
source venv/bin/activate

# 3. Install the server and test tools
pip install -e ".[dev]"
```

## Run it

The server speaks MCP over stdio, so you run it inside an MCP-compatible client. For example, add this to your MCP client config:

```json
{
  "mcpServers": {
    "shift-schedule": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "shift_mcp"]
    }
  }
}
```

Once connected, an AI assistant can ask things like:

> "What shifts does nurse-a have next week?"
> "Add a day off for nurse-b on 2026-11-01 for personal time."
> "List all rotation patterns for the ICU team."

## Run the tests

This project is tested. Run the test suite with:

```bash
source venv/bin/activate
pytest tests/ -v
```

You should see **34 tests pass**: 28 that check the tool schemas are correct, and 6 that launch the real server and exercise it end-to-end (add, list, update, delete, date filtering, persistence).

## Local-first and private

- Data stays on your machine in JSON files you can open in any text editor
- No accounts, no cloud, no tracking
- No secrets, API keys, or personal data are stored in the project files

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Asdale Dynamics, LLC

## Credits

Created by **Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI education, books, and practical tools. Learn more at dylanasdale.github.io.
