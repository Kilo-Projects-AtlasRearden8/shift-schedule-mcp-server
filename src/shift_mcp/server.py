"""MCP Server for shift schedule management."""

import asyncio
import json
import os
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .storage import (
    DayOff,
    RotationPattern,
    Shift,
    Storage,
)

_SERVER_VERSION = "0.1.0"


def _make_storage() -> Storage:
    """Create storage, honoring the SHIFT_SCHEDULE_DATA_DIR env var."""
    env_dir = os.environ.get("SHIFT_SCHEDULE_DATA_DIR")
    if env_dir:
        return Storage(Path(env_dir))
    return Storage()


# ---------------------------------------------------------------------------
# Tool definitions (input schemas)
# ---------------------------------------------------------------------------
SHIFT_TOOLS = [
    types.Tool(
        name="list_shifts",
        description="List all shifts, optionally filtered by worker_id and/or date",
        input_schema={
            "type": "object",
            "properties": {
                "worker_id": {"type": "string", "description": "Filter by worker ID"},
                "date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)"},
            },
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="get_shift",
        description="Get a specific shift by ID",
        input_schema={
            "type": "object",
            "properties": {
                "shift_id": {"type": "string", "description": "Shift ID to retrieve"},
            },
            "required": ["shift_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="add_shift",
        description="Add a new shift",
        input_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique shift ID"},
                "worker_id": {"type": "string", "description": "Worker ID"},
                "date": {"type": "string", "description": "Shift date (YYYY-MM-DD)"},
                "start_time": {"type": "string", "description": "Start time (HH:MM)"},
                "end_time": {"type": "string", "description": "End time (HH:MM)"},
                "department": {"type": "string", "description": "Department name (optional)"},
                "notes": {"type": "string", "description": "Notes (optional)"},
            },
            "required": ["id", "worker_id", "date", "start_time", "end_time"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="update_shift",
        description="Update an existing shift",
        input_schema={
            "type": "object",
            "properties": {
                "shift_id": {"type": "string", "description": "Shift ID to update"},
                "worker_id": {"type": "string", "description": "Worker ID"},
                "date": {"type": "string", "description": "Shift date (YYYY-MM-DD)"},
                "start_time": {"type": "string", "description": "Start time (HH:MM)"},
                "end_time": {"type": "string", "description": "End time (HH:MM)"},
                "department": {"type": "string", "description": "Department name"},
                "notes": {"type": "string", "description": "Notes"},
            },
            "required": ["shift_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="delete_shift",
        description="Delete a shift by ID",
        input_schema={
            "type": "object",
            "properties": {
                "shift_id": {"type": "string", "description": "Shift ID to delete"},
            },
            "required": ["shift_id"],
            "additionalProperties": False,
        },
    ),
]

DAY_OFF_TOOLS = [
    types.Tool(
        name="list_days_off",
        description="List all days off, optionally filtered by worker_id and/or date",
        input_schema={
            "type": "object",
            "properties": {
                "worker_id": {"type": "string", "description": "Filter by worker ID"},
                "date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)"},
            },
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="get_day_off",
        description="Get a specific day off by ID",
        input_schema={
            "type": "object",
            "properties": {
                "day_off_id": {"type": "string", "description": "Day off ID to retrieve"},
            },
            "required": ["day_off_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="add_day_off",
        description="Add a new day off",
        input_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique day off ID"},
                "worker_id": {"type": "string", "description": "Worker ID"},
                "date": {"type": "string", "description": "Day off date (YYYY-MM-DD)"},
                "reason": {"type": "string", "description": "Reason for day off (optional)"},
            },
            "required": ["id", "worker_id", "date"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="update_day_off",
        description="Update an existing day off",
        input_schema={
            "type": "object",
            "properties": {
                "day_off_id": {"type": "string", "description": "Day off ID to update"},
                "worker_id": {"type": "string", "description": "Worker ID"},
                "date": {"type": "string", "description": "Day off date (YYYY-MM-DD)"},
                "reason": {"type": "string", "description": "Reason for day off"},
            },
            "required": ["day_off_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="delete_day_off",
        description="Delete a day off by ID",
        input_schema={
            "type": "object",
            "properties": {
                "day_off_id": {"type": "string", "description": "Day off ID to delete"},
            },
            "required": ["day_off_id"],
            "additionalProperties": False,
        },
    ),
]

ROTATION_TOOLS = [
    types.Tool(
        name="list_rotations",
        description="List all rotation patterns, optionally filtered by worker_id",
        input_schema={
            "type": "object",
            "properties": {
                "worker_id": {"type": "string", "description": "Filter by worker ID"},
            },
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="get_rotation",
        description="Get a specific rotation pattern by ID",
        input_schema={
            "type": "object",
            "properties": {
                "rotation_id": {"type": "string", "description": "Rotation ID to retrieve"},
            },
            "required": ["rotation_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="add_rotation",
        description="Add a new rotation pattern",
        input_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique rotation ID"},
                "name": {"type": "string", "description": "Rotation name"},
                "worker_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of worker IDs in this rotation",
                },
                "cycle_days": {"type": "integer", "description": "Length of rotation cycle in days"},
                "pattern": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Pattern of work/off days (e.g., ['work', 'work', 'off', 'off'])",
                },
                "start_date": {"type": "string", "description": "Rotation start date (YYYY-MM-DD)"},
            },
            "required": ["id", "name", "worker_ids", "cycle_days", "pattern", "start_date"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="update_rotation",
        description="Update an existing rotation pattern",
        input_schema={
            "type": "object",
            "properties": {
                "rotation_id": {"type": "string", "description": "Rotation ID to update"},
                "name": {"type": "string", "description": "Rotation name"},
                "worker_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of worker IDs",
                },
                "cycle_days": {"type": "integer", "description": "Cycle length in days"},
                "pattern": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Pattern of work/off days",
                },
                "start_date": {"type": "string", "description": "Rotation start date (YYYY-MM-DD)"},
            },
            "required": ["rotation_id"],
            "additionalProperties": False,
        },
    ),
    types.Tool(
        name="delete_rotation",
        description="Delete a rotation pattern by ID",
        input_schema={
            "type": "object",
            "properties": {
                "rotation_id": {"type": "string", "description": "Rotation ID to delete"},
            },
            "required": ["rotation_id"],
            "additionalProperties": False,
        },
    ),
]

ALL_TOOLS = SHIFT_TOOLS + DAY_OFF_TOOLS + ROTATION_TOOLS


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------
def _shift_to_dict(shift: Shift) -> dict[str, Any]:
    return {
        "id": shift.id,
        "worker_id": shift.worker_id,
        "date": shift.date.isoformat(),
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "department": shift.department,
        "notes": shift.notes,
    }


def _day_off_to_dict(day_off: DayOff) -> dict[str, Any]:
    return {
        "id": day_off.id,
        "worker_id": day_off.worker_id,
        "date": day_off.date.isoformat(),
        "reason": day_off.reason,
    }


def _rotation_to_dict(rotation: RotationPattern) -> dict[str, Any]:
    return {
        "id": rotation.id,
        "name": rotation.name,
        "worker_ids": rotation.worker_ids,
        "cycle_days": rotation.cycle_days,
        "pattern": rotation.pattern,
        "start_date": rotation.start_date.isoformat(),
    }


# ---------------------------------------------------------------------------
# Tool call dispatcher
# ---------------------------------------------------------------------------
def _call_tool(name: str, arguments: dict[str, Any], store: Storage) -> types.CallToolResult:
    """Execute a tool call and return a CallToolResult."""
    try:
        if name == "list_shifts":
            worker_id = arguments.get("worker_id")
            date_str = arguments.get("date")
            target_date = date.fromisoformat(date_str) if date_str else None

            if worker_id and target_date:
                shifts = store.get_shifts_by_worker_and_date(worker_id, target_date)
            elif worker_id:
                shifts = store.get_shifts_by_worker(worker_id)
            elif target_date:
                shifts = store.get_shifts_by_date(target_date)
            else:
                shifts = store.get_shifts()

            text = json.dumps([_shift_to_dict(s) for s in shifts], indent=2)
            return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

        elif name == "get_shift":
            shift = store.get_shift(arguments["shift_id"])
            if shift is None:
                return _error(f"Shift {arguments['shift_id']} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_shift_to_dict(shift), indent=2))]
            )

        elif name == "add_shift":
            shift = Shift(
                id=arguments["id"],
                worker_id=arguments["worker_id"],
                date=date.fromisoformat(arguments["date"]),
                start_time=arguments["start_time"],
                end_time=arguments["end_time"],
                department=arguments.get("department"),
                notes=arguments.get("notes"),
            )
            store.add_shift(shift)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_shift_to_dict(shift), indent=2))]
            )

        elif name == "update_shift":
            shift_id = arguments["shift_id"]
            updates = {k: v for k, v in arguments.items() if k != "shift_id" and v is not None}
            if "date" in updates:
                updates["date"] = date.fromisoformat(updates["date"])
            shift = store.update_shift(shift_id, **updates)
            if shift is None:
                return _error(f"Shift {shift_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_shift_to_dict(shift), indent=2))]
            )

        elif name == "delete_shift":
            shift_id = arguments["shift_id"]
            success = store.delete_shift(shift_id)
            if not success:
                return _error(f"Shift {shift_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Shift {shift_id} deleted")]
            )

        elif name == "list_days_off":
            worker_id = arguments.get("worker_id")
            date_str = arguments.get("date")
            target_date = date.fromisoformat(date_str) if date_str else None

            if worker_id and target_date:
                days = [d for d in store.get_days_off_by_worker(worker_id) if d.date == target_date]
            elif worker_id:
                days = store.get_days_off_by_worker(worker_id)
            elif target_date:
                days = store.get_days_off_by_date(target_date)
            else:
                days = store.get_days_off()

            text = json.dumps([_day_off_to_dict(d) for d in days], indent=2)
            return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

        elif name == "get_day_off":
            day_off = store.get_day_off(arguments["day_off_id"])
            if day_off is None:
                return _error(f"Day off {arguments['day_off_id']} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_day_off_to_dict(day_off), indent=2))]
            )

        elif name == "add_day_off":
            day_off = DayOff(
                id=arguments["id"],
                worker_id=arguments["worker_id"],
                date=date.fromisoformat(arguments["date"]),
                reason=arguments.get("reason"),
            )
            store.add_day_off(day_off)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_day_off_to_dict(day_off), indent=2))]
            )

        elif name == "update_day_off":
            day_off_id = arguments["day_off_id"]
            updates = {k: v for k, v in arguments.items() if k != "day_off_id" and v is not None}
            if "date" in updates:
                updates["date"] = date.fromisoformat(updates["date"])
            day_off = store.update_day_off(day_off_id, **updates)
            if day_off is None:
                return _error(f"Day off {day_off_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_day_off_to_dict(day_off), indent=2))]
            )

        elif name == "delete_day_off":
            day_off_id = arguments["day_off_id"]
            success = store.delete_day_off(day_off_id)
            if not success:
                return _error(f"Day off {day_off_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Day off {day_off_id} deleted")]
            )

        elif name == "list_rotations":
            worker_id = arguments.get("worker_id")
            if worker_id:
                rotations = store.get_rotations_by_worker(worker_id)
            else:
                rotations = store.get_rotations()
            text = json.dumps([_rotation_to_dict(r) for r in rotations], indent=2)
            return types.CallToolResult(content=[types.TextContent(type="text", text=text)])

        elif name == "get_rotation":
            rotation = store.get_rotation(arguments["rotation_id"])
            if rotation is None:
                return _error(f"Rotation {arguments['rotation_id']} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_rotation_to_dict(rotation), indent=2))]
            )

        elif name == "add_rotation":
            rotation = RotationPattern(
                id=arguments["id"],
                name=arguments["name"],
                worker_ids=arguments["worker_ids"],
                cycle_days=arguments["cycle_days"],
                pattern=arguments["pattern"],
                start_date=date.fromisoformat(arguments["start_date"]),
            )
            store.add_rotation(rotation)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_rotation_to_dict(rotation), indent=2))]
            )

        elif name == "update_rotation":
            rotation_id = arguments["rotation_id"]
            updates = {k: v for k, v in arguments.items() if k != "rotation_id" and v is not None}
            if "start_date" in updates:
                updates["start_date"] = date.fromisoformat(updates["start_date"])
            rotation = store.update_rotation(rotation_id, **updates)
            if rotation is None:
                return _error(f"Rotation {rotation_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(_rotation_to_dict(rotation), indent=2))]
            )

        elif name == "delete_rotation":
            rotation_id = arguments["rotation_id"]
            success = store.delete_rotation(rotation_id)
            if not success:
                return _error(f"Rotation {rotation_id} not found")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Rotation {rotation_id} deleted")]
            )

        else:
            return _error(f"Unknown tool: {name}")

    except Exception as e:
        return _error(f"Error: {str(e)}")


def _error(message: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=message)],
        is_error=True,
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
def _build_list_tools_handler(store: Storage):
    async def list_tools(ctx, params):
        return types.ListToolsResult(tools=ALL_TOOLS)
    return list_tools


def _build_call_tool_handler(store: Storage):
    async def call_tool(ctx, params):
        arguments = params.arguments or {}
        return _call_tool(params.name, arguments, store)
    return call_tool


def create_server(store: Storage | None = None) -> Server:
    """Create and configure the MCP server."""
    if store is None:
        store = _make_storage()

    return Server(
        "shift-schedule-mcp-server",
        version=_SERVER_VERSION,
        title="Shift Schedule MCP Server",
        description="MCP server for healthcare worker shift schedules, days off, and rotation patterns",
        on_list_tools=_build_list_tools_handler(store),
        on_call_tool=_build_call_tool_handler(store),
    )


async def main() -> None:
    """Run the MCP server over stdio."""
    store = _make_storage()
    server = create_server(store)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())