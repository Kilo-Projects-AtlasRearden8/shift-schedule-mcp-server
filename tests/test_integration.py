"""End-to-end integration tests using the MCP stdio client.

These launch the server as a subprocess and exercise tools over the real
stdio transport, verifying build/run correctness (not just schema shape).
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


@pytest.fixture
def isolated_env():
    """Provide a fresh, temporary data directory and env for each test."""
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["SHIFT_SCHEDULE_DATA_DIR"] = tmp
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        yield tmp, env


def _params(env: dict[str, str]) -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "shift_mcp"],
        env=env,
    )


@pytest.mark.asyncio
async def test_server_lists_all_tools(isolated_env):
    """The server should list all 15 tools on startup."""
    _, env = isolated_env
    async with Client(_params(env)) as client:
        result = await client.list_tools()
        tools = result.tools
    names = {t.name for t in tools}
    assert len(tools) == 15
    assert "add_shift" in names
    assert "add_day_off" in names
    assert "add_rotation" in names


@pytest.mark.asyncio
async def test_shift_crud_lifecycle(isolated_env):
    """Add, list, get, update, delete a shift end-to-end."""
    _, env = isolated_env
    async with Client(_params(env)) as client:
        add_result = await client.call_tool(
            "add_shift",
            {
                "id": "s1",
                "worker_id": "nurse-a",
                "date": "2026-10-28",
                "start_time": "07:00",
                "end_time": "19:00",
                "department": "ICU",
                "notes": "Day shift",
            },
        )
        assert add_result.is_error is False
        assert "s1" in add_result.content[0].text

        list_result = await client.call_tool("list_shifts", {})
        assert list_result.is_error is False
        assert "s1" in list_result.content[0].text

        filtered = await client.call_tool("list_shifts", {"worker_id": "nurse-a"})
        assert "nurse-a" in filtered.content[0].text

        get_result = await client.call_tool("get_shift", {"shift_id": "s1"})
        assert get_result.is_error is False
        assert "ICU" in get_result.content[0].text

        upd = await client.call_tool(
            "update_shift", {"shift_id": "s1", "department": "ER"}
        )
        assert "ER" in upd.content[0].text

        dele = await client.call_tool("delete_shift", {"shift_id": "s1"})
        assert "deleted" in dele.content[0].text

        missing = await client.call_tool("get_shift", {"shift_id": "s1"})
        assert missing.is_error is True


@pytest.mark.asyncio
async def test_day_off_and_rotation(isolated_env):
    """Exercise day-off and rotation patterns end-to-end."""
    _, env = isolated_env
    async with Client(_params(env)) as client:
        do = await client.call_tool(
            "add_day_off",
            {
                "id": "d1",
                "worker_id": "nurse-b",
                "date": "2026-11-01",
                "reason": "Personal",
            },
        )
        assert do.is_error is False
        assert "d1" in do.content[0].text

        rot = await client.call_tool(
            "add_rotation",
            {
                "id": "r1",
                "name": "NightRotation",
                "worker_ids": ["nurse-b", "nurse-c"],
                "cycle_days": 4,
                "pattern": ["work", "work", "off", "off"],
                "start_date": "2026-11-01",
            },
        )
        assert rot.is_error is False
        assert "NightRotation" in rot.content[0].text

        rots = await client.call_tool("list_rotations", {"worker_id": "nurse-b"})
        assert "NightRotation" in rots.content[0].text

        gd = await client.call_tool("get_day_off", {"day_off_id": "d1"})
        assert "Personal" in gd.content[0].text


@pytest.mark.asyncio
async def test_list_shifts_date_filter(isolated_env):
    """list_shifts filters by date."""
    _, env = isolated_env
    async with Client(_params(env)) as client:
        await client.call_tool(
            "add_shift",
            {
                "id": "s1",
                "worker_id": "nurse-a",
                "date": "2026-10-28",
                "start_time": "07:00",
                "end_time": "19:00",
            },
        )
        await client.call_tool(
            "add_shift",
            {
                "id": "s2",
                "worker_id": "nurse-a",
                "date": "2026-10-29",
                "start_time": "19:00",
                "end_time": "07:00",
            },
        )
        result = await client.call_tool("list_shifts", {"date": "2026-10-28"})
        text = result.content[0].text
        assert "2026-10-28" in text
        assert "2026-10-29" not in text


@pytest.mark.asyncio
async def test_unknown_tool_returns_error(isolated_env):
    """Calling a nonexistent tool returns an error."""
    _, env = isolated_env
    async with Client(_params(env)) as client:
        result = await client.call_tool("not_a_real_tool", {})
        assert result.is_error is True


@pytest.mark.asyncio
async def test_data_persists_across_server_starts(isolated_env):
    """Data written by one server process must survive in the JSON file."""
    data_dir, env = isolated_env

    # First process: add data
    async with Client(_params(env)) as client:
        await client.call_tool(
            "add_shift",
            {
                "id": "persist-1",
                "worker_id": "nurse-z",
                "date": "2026-11-05",
                "start_time": "07:00",
                "end_time": "19:00",
            },
        )

    # Verify the raw JSON file contains the record
    shifts_file = Path(data_dir) / "shifts.json"
    assert shifts_file.exists()
    data = json.loads(shifts_file.read_text())
    assert len(data) == 1
    assert data[0]["id"] == "persist-1"

    # Second process: read it back
    async with Client(_params(env)) as client:
        result = await client.call_tool("list_shifts", {})
        assert "persist-1" in result.content[0].text
