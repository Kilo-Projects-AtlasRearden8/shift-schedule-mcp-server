"""Tests for MCP tool schemas."""

import json
from shift_mcp.server import ALL_TOOLS, SHIFT_TOOLS, DAY_OFF_TOOLS, ROTATION_TOOLS


class TestToolSchemas:
    """Test that all tool schemas are valid and complete."""

    def test_all_tools_exist(self):
        """Verify we have the expected number of tools."""
        # 5 shift tools + 5 day off tools + 5 rotation tools = 15
        assert len(ALL_TOOLS) == 15
        assert len(SHIFT_TOOLS) == 5
        assert len(DAY_OFF_TOOLS) == 5
        assert len(ROTATION_TOOLS) == 5

    def test_tool_names_unique(self):
        """Verify all tool names are unique."""
        names = [tool.name for tool in ALL_TOOLS]
        assert len(names) == len(set(names))

    def test_shift_tool_names(self):
        """Verify shift tool names."""
        shift_names = {tool.name for tool in SHIFT_TOOLS}
        expected = {
            "list_shifts",
            "get_shift",
            "add_shift",
            "update_shift",
            "delete_shift",
        }
        assert shift_names == expected

    def test_day_off_tool_names(self):
        """Verify day off tool names."""
        day_off_names = {tool.name for tool in DAY_OFF_TOOLS}
        expected = {
            "list_days_off",
            "get_day_off",
            "add_day_off",
            "update_day_off",
            "delete_day_off",
        }
        assert day_off_names == expected

    def test_rotation_tool_names(self):
        """Verify rotation tool names."""
        rotation_names = {tool.name for tool in ROTATION_TOOLS}
        expected = {
            "list_rotations",
            "get_rotation",
            "add_rotation",
            "update_rotation",
            "delete_rotation",
        }
        assert rotation_names == expected

    def test_all_tools_have_required_fields(self):
        """Verify all tools have name, description, and inputSchema."""
        for tool in ALL_TOOLS:
            assert tool.name, f"Tool missing name: {tool}"
            assert tool.description, f"Tool {tool.name} missing description"
            assert tool.input_schema, f"Tool {tool.name} missing inputSchema"
            assert tool.input_schema.get("type") == "object", f"Tool {tool.name} inputSchema type must be object"
            assert "properties" in tool.input_schema, f"Tool {tool.name} inputSchema missing properties"

    def test_list_shifts_schema(self):
        """Test list_shifts tool schema."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "list_shifts")
        props = tool.input_schema["properties"]
        assert "worker_id" in props
        assert props["worker_id"]["type"] == "string"
        assert "date" in props
        assert props["date"]["type"] == "string"
        # No required fields for list (all optional filters)
        assert tool.input_schema.get("required") == [] or "required" not in tool.input_schema

    def test_get_shift_schema(self):
        """Test get_shift tool schema."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "get_shift")
        props = tool.input_schema["properties"]
        assert "shift_id" in props
        assert props["shift_id"]["type"] == "string"
        assert tool.input_schema["required"] == ["shift_id"]

    def test_add_shift_schema(self):
        """Test add_shift tool schema."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "add_shift")
        props = tool.input_schema["properties"]
        required = tool.input_schema["required"]
        # Required fields
        assert "id" in required
        assert "worker_id" in required
        assert "date" in required
        assert "start_time" in required
        assert "end_time" in required
        # Optional fields
        assert "department" in props
        assert "notes" in props
        assert "department" not in required
        assert "notes" not in required
        # Types
        assert props["id"]["type"] == "string"
        assert props["worker_id"]["type"] == "string"
        assert props["date"]["type"] == "string"
        assert props["start_time"]["type"] == "string"
        assert props["end_time"]["type"] == "string"

    def test_update_shift_schema(self):
        """Test update_shift tool schema."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "update_shift")
        props = tool.input_schema["properties"]
        required = tool.input_schema["required"]
        assert required == ["shift_id"]
        # All other fields optional
        assert "worker_id" in props
        assert "date" in props
        assert "start_time" in props
        assert "end_time" in props
        assert "department" in props
        assert "notes" in props

    def test_delete_shift_schema(self):
        """Test delete_shift tool schema."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "delete_shift")
        props = tool.input_schema["properties"]
        assert "shift_id" in props
        assert tool.input_schema["required"] == ["shift_id"]

    def test_list_days_off_schema(self):
        """Test list_days_off tool schema."""
        tool = next(t for t in DAY_OFF_TOOLS if t.name == "list_days_off")
        props = tool.input_schema["properties"]
        assert "worker_id" in props
        assert "date" in props
        assert props["worker_id"]["type"] == "string"
        assert props["date"]["type"] == "string"

    def test_get_day_off_schema(self):
        """Test get_day_off tool schema."""
        tool = next(t for t in DAY_OFF_TOOLS if t.name == "get_day_off")
        assert tool.input_schema["required"] == ["day_off_id"]
        assert tool.input_schema["properties"]["day_off_id"]["type"] == "string"

    def test_add_day_off_schema(self):
        """Test add_day_off tool schema."""
        tool = next(t for t in DAY_OFF_TOOLS if t.name == "add_day_off")
        props = tool.input_schema["properties"]
        required = tool.input_schema["required"]
        assert required == ["id", "worker_id", "date"]
        assert "reason" in props
        assert "reason" not in required
        assert props["id"]["type"] == "string"
        assert props["worker_id"]["type"] == "string"
        assert props["date"]["type"] == "string"
        assert props["reason"]["type"] == "string"

    def test_update_day_off_schema(self):
        """Test update_day_off tool schema."""
        tool = next(t for t in DAY_OFF_TOOLS if t.name == "update_day_off")
        assert tool.input_schema["required"] == ["day_off_id"]
        props = tool.input_schema["properties"]
        assert "worker_id" in props
        assert "date" in props
        assert "reason" in props

    def test_delete_day_off_schema(self):
        """Test delete_day_off tool schema."""
        tool = next(t for t in DAY_OFF_TOOLS if t.name == "delete_day_off")
        assert tool.input_schema["required"] == ["day_off_id"]
        assert tool.input_schema["properties"]["day_off_id"]["type"] == "string"

    def test_list_rotations_schema(self):
        """Test list_rotations tool schema."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "list_rotations")
        props = tool.input_schema["properties"]
        assert "worker_id" in props
        assert props["worker_id"]["type"] == "string"

    def test_get_rotation_schema(self):
        """Test get_rotation tool schema."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "get_rotation")
        assert tool.input_schema["required"] == ["rotation_id"]
        assert tool.input_schema["properties"]["rotation_id"]["type"] == "string"

    def test_add_rotation_schema(self):
        """Test add_rotation tool schema."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "add_rotation")
        props = tool.input_schema["properties"]
        required = tool.input_schema["required"]
        assert required == ["id", "name", "worker_ids", "cycle_days", "pattern", "start_date"]
        assert props["id"]["type"] == "string"
        assert props["name"]["type"] == "string"
        assert props["worker_ids"]["type"] == "array"
        assert props["worker_ids"]["items"]["type"] == "string"
        assert props["cycle_days"]["type"] == "integer"
        assert props["pattern"]["type"] == "array"
        assert props["pattern"]["items"]["type"] == "string"
        assert props["start_date"]["type"] == "string"

    def test_update_rotation_schema(self):
        """Test update_rotation tool schema."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "update_rotation")
        assert tool.input_schema["required"] == ["rotation_id"]
        props = tool.input_schema["properties"]
        assert "name" in props
        assert "worker_ids" in props
        assert "cycle_days" in props
        assert "pattern" in props
        assert "start_date" in props

    def test_delete_rotation_schema(self):
        """Test delete_rotation tool schema."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "delete_rotation")
        assert tool.input_schema["required"] == ["rotation_id"]
        assert tool.input_schema["properties"]["rotation_id"]["type"] == "string"

    def test_schemas_are_json_serializable(self):
        """Verify all tool schemas can be serialized to JSON."""
        for tool in ALL_TOOLS:
            # Should not raise
            json.dumps(tool.input_schema)


class TestToolSchemaValidation:
    """Test that tool input schemas properly validate input."""

    def test_list_shifts_accepts_empty_input(self):
        """list_shifts should accept empty input (all filters optional)."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "list_shifts")
        # Empty input should be valid per schema (no required fields)
        schema = tool.input_schema
        assert schema.get("required", []) == []

    def test_add_shift_requires_all_fields(self):
        """add_shift should require id, worker_id, date, start_time, end_time."""
        tool = next(t for t in SHIFT_TOOLS if t.name == "add_shift")
        required = tool.input_schema["required"]
        assert set(required) == {"id", "worker_id", "date", "start_time", "end_time"}

    def test_add_rotation_requires_all_fields(self):
        """add_rotation should require all fields."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "add_rotation")
        required = tool.input_schema["required"]
        assert set(required) == {"id", "name", "worker_ids", "cycle_days", "pattern", "start_date"}

    def test_worker_ids_is_array_of_strings(self):
        """worker_ids in rotation should be array of strings."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "add_rotation")
        worker_ids_schema = tool.input_schema["properties"]["worker_ids"]
        assert worker_ids_schema["type"] == "array"
        assert worker_ids_schema["items"]["type"] == "string"

    def test_pattern_is_array_of_strings(self):
        """pattern in rotation should be array of strings."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "add_rotation")
        pattern_schema = tool.input_schema["properties"]["pattern"]
        assert pattern_schema["type"] == "array"
        assert pattern_schema["items"]["type"] == "string"

    def test_cycle_days_is_integer(self):
        """cycle_days in rotation should be integer."""
        tool = next(t for t in ROTATION_TOOLS if t.name == "add_rotation")
        cycle_schema = tool.input_schema["properties"]["cycle_days"]
        assert cycle_schema["type"] == "integer"