# STATUS.md

## What Was Built

**shift-schedule-mcp-server** — a Model Context Protocol (MCP) server for tracking work shifts, days off, and rotation patterns for healthcare workers.

### Core Features

1. **Shifts** — Store/retrieve work shifts with:
   - Unique ID, worker ID, date (YYYY-MM-DD)
   - Start/end times (HH:MM)
   - Optional department and notes

2. **Days Off** — Track days off with:
   - Unique ID, worker ID, date
   - Optional reason

3. **Rotation Patterns** — Define recurring rotation cycles:
   - Name, list of worker IDs, cycle length in days
   - Pattern array (e.g., `["work", "work", "off", "off"]`)
   - Start date

### MCP Tools (15 total)

| Category | Tools |
|----------|-------|
| **Shifts** | `list_shifts`, `get_shift`, `add_shift`, `update_shift`, `delete_shift` |
| **Days Off** | `list_days_off`, `get_day_off`, `add_day_off`, `update_day_off`, `delete_day_off` |
| **Rotations** | `list_rotations`, `get_rotation`, `add_rotation`, `update_rotation`, `delete_rotation` |

All tools support filtering by worker_id and/or date where applicable.

### Storage

- Local JSON files in `~/.shift-schedule-mcp/` by default
- Configurable via `SHIFT_SCHEDULE_DATA_DIR` environment variable
- Files: `shifts.json`, `days_off.json`, `rotations.json`

### Architecture

- Python 3.10+, MCP SDK v2.3.0
- Runs over stdio transport
- Pydantic models for validation
- Clean separation: `storage.py` (data), `server.py` (MCP handlers), `__main__.py` (entry)

## How to Run

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 3. Run the server (stdio - meant to be launched by an MCP client)
python -m shift_mcp

# Or configure in an MCP client (e.g., Claude Desktop, VS Code with MCP):
# {
#   "mcpServers": {
#     "shift-schedule": {
#       "command": "/path/to/venv/bin/python",
#       "args": ["-m", "shift_mcp"],
#       "env": { "SHIFT_SCHEDULE_DATA_DIR": "/custom/data/path" }
#     }
#   }
# }
```

## Verification Results

### Tests: 34 passed (4.3s)

| Test Suite | Tests | Status |
|------------|-------|--------|
| `tests/test_schemas.py` | 28 | ✅ All pass |
| `tests/test_integration.py` | 6 | ✅ All pass |

**Schema tests** validate:
- All 15 tools present with correct names
- Unique tool names
- Required/optional fields correct
- Types: strings, arrays, integers
- JSON serializability
- Schema validation behavior

**Integration tests** validate (via real stdio subprocess):
- Server lists all 15 tools
- Shift CRUD: add → list → get → update → delete
- Day off and rotation CRUD
- Date filtering on `list_shifts`
- Unknown tool returns error
- Data persists across server restarts (raw JSON verified)

### Manual Verification

- `python -m shift_mcp` starts without error
- Package installs cleanly in editable mode
- No import errors in `src/shift_mcp/`
- All schema dicts are valid JSON

## Known Gaps / Future Work

1. **No authentication/authorization** — Local-first design assumes trusted environment
2. **No built-in scheduling engine** — Rotation patterns are stored but not automatically expanded into future shifts
3. **No conflict detection** — Overlapping shifts for same worker not prevented
4. **No query by date range** — Only exact date or all dates
5. **No export/import** — JSON files are portable but no CLI for bulk operations
6. **No metrics/observability** — No logging of tool calls or performance
7. **Single-process stdio only** — No HTTP/SSE transport variant
8. **Timezone handling** — Dates are naive (no TZ); times stored as HH:MM strings

## License & Credits

- **License**: MIT — `LICENSE` file with `Copyright (c) 2026 Asdale Dynamics, LLC`
- **README** credits Asdale Dynamics, LLC
- No secrets, API keys, or personal data in repository
- No `.github/workflows` files
- Git commits use existing identity (Dylan Asdale), no co-author trailers