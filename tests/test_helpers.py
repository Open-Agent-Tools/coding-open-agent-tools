"""Tests for helper functions."""

from coding_open_agent_tools import helpers


class TestMergeToolLists:
    """Tests for merge_tool_lists function."""

    def test_merge_two_lists(self) -> None:
        """Test merging two non-overlapping lists."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        def func3() -> None:
            pass

        list1 = [func1, func2]
        list2 = [func3]

        result = helpers.merge_tool_lists(list1, list2)
        assert len(result) == 3
        assert func1 in result
        assert func2 in result
        assert func3 in result

    def test_merge_with_duplicates(self) -> None:
        """Test merging lists with duplicate functions."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        list1 = [func1, func2]
        list2 = [func2, func1]

        result = helpers.merge_tool_lists(list1, list2)
        assert len(result) == 2
        assert func1 in result
        assert func2 in result

    def test_merge_empty_lists(self) -> None:
        """Test merging empty lists."""
        result = helpers.merge_tool_lists([], [])
        assert result == []

    def test_merge_single_list(self) -> None:
        """Test merging a single list."""

        def func1() -> None:
            pass

        list1 = [func1]
        result = helpers.merge_tool_lists(list1)
        assert len(result) == 1
        assert func1 in result

    def test_merge_multiple_lists(self) -> None:
        """Test merging more than two lists."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        def func3() -> None:
            pass

        list1 = [func1]
        list2 = [func2]
        list3 = [func3]

        result = helpers.merge_tool_lists(list1, list2, list3)
        assert len(result) == 3

    def test_preserves_order(self) -> None:
        """Test that merge preserves order of first occurrence."""

        def func1() -> None:
            pass

        def func2() -> None:
            pass

        def func3() -> None:
            pass

        list1 = [func1, func2]
        list2 = [func3, func1]

        result = helpers.merge_tool_lists(list1, list2)
        assert result[0] == func1
        assert result[1] == func2
        assert result[2] == func3


class TestLoadAnalysisTools:
    """Tests for load_all_analysis_tools function."""

    def test_loads_all_analysis_tools(self) -> None:
        """Test that all 14 analysis tools are loaded."""
        tools = helpers.load_all_analysis_tools()
        assert len(tools) == 14

    def test_analysis_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_analysis_tools()
        for tool in tools:
            assert callable(tool)

    def test_analysis_tools_have_names(self) -> None:
        """Test that all tools have proper names."""
        tools = helpers.load_all_analysis_tools()
        expected_names = {
            "parse_python_ast",
            "extract_functions",
            "extract_classes",
            "extract_imports",
            "calculate_complexity",
            "calculate_function_complexity",
            "get_code_metrics",
            "identify_complex_functions",
            "find_unused_imports",
            "organize_imports",
            "validate_import_order",
            "scan_for_secrets",
            "scan_directory_for_secrets",
            "validate_secret_patterns",
        }
        actual_names = {tool.__name__ for tool in tools}
        assert actual_names == expected_names


class TestLoadGitTools:
    """Tests for load_all_git_tools function."""

    def test_loads_all_git_tools(self) -> None:
        """Test that all 79 git tools are loaded."""
        tools = helpers.load_all_git_tools()
        assert len(tools) == 79

    def test_git_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_git_tools()
        for tool in tools:
            assert callable(tool)

    def test_git_tools_have_names(self) -> None:
        """Test that all tools have proper names."""
        tools = helpers.load_all_git_tools()
        # After Git Enhancement Module, we have 79 git tools
        # Just verify that core tools are present
        actual_names = {tool.__name__ for tool in tools}
        assert "get_git_status" in actual_names
        assert "get_current_branch" in actual_names
        assert "get_git_diff" in actual_names
        assert "get_git_log" in actual_names
        assert len(actual_names) == 79


class TestLoadProfilingTools:
    """Tests for load_all_profiling_tools function."""

    def test_loads_all_profiling_tools(self) -> None:
        """Test that all 8 profiling tools are loaded."""
        tools = helpers.load_all_profiling_tools()
        assert len(tools) == 8

    def test_profiling_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_profiling_tools()
        for tool in tools:
            assert callable(tool)


class TestLoadQualityTools:
    """Tests for load_all_quality_tools function."""

    def test_loads_all_quality_tools(self) -> None:
        """Test that all 7 quality tools are loaded."""
        tools = helpers.load_all_quality_tools()
        assert len(tools) == 7

    def test_quality_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_quality_tools()
        for tool in tools:
            assert callable(tool)


class TestLoadShellTools:
    """Tests for load_all_shell_tools function."""

    def test_loads_all_shell_tools(self) -> None:
        """Test that all 13 shell tools are loaded."""
        tools = helpers.load_all_shell_tools()
        assert len(tools) == 13

    def test_shell_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_shell_tools()
        for tool in tools:
            assert callable(tool)


class TestLoadPythonTools:
    """Tests for load_all_python_tools function."""

    def test_loads_all_python_tools(self) -> None:
        """Test that all 15 python tools are loaded."""
        tools = helpers.load_all_python_tools()
        assert len(tools) == 15

    def test_python_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_python_tools()
        for tool in tools:
            assert callable(tool)


class TestLoadDatabaseTools:
    """Tests for load_all_database_tools function."""

    def test_loads_all_database_tools(self) -> None:
        """Test that all 18 database tools are loaded."""
        tools = helpers.load_all_database_tools()
        # Should be 18 not 16 based on the function body
        assert len(tools) == 18

    def test_database_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_database_tools()
        for tool in tools:
            assert callable(tool)

    def test_database_tools_have_names(self) -> None:
        """Test that database tools have proper names."""
        tools = helpers.load_all_database_tools()
        expected_names = {
            "create_sqlite_database",
            "execute_query",
            "execute_many",
            "fetch_all",
            "fetch_one",
            "inspect_schema",
            "create_table_from_dict",
            "add_column",
            "create_index",
            "build_select_query",
            "build_insert_query",
            "build_update_query",
            "build_delete_query",
            "escape_sql_identifier",
            "validate_sql_query",
            "export_to_json",
            "import_from_json",
            "backup_database",
        }
        actual_names = {tool.__name__ for tool in tools}
        assert actual_names == expected_names


class TestLoadAllTools:
    """Tests for load_all_tools function."""

    def test_loads_all_tools(self) -> None:
        """Test that all 154 tools are loaded."""
        tools = helpers.load_all_tools()
        # 14 + 79 + 8 + 7 + 13 + 15 + 18 = 154
        assert len(tools) == 154

    def test_all_tools_callable(self) -> None:
        """Test that all loaded tools are callable."""
        tools = helpers.load_all_tools()
        for tool in tools:
            assert callable(tool)

    def test_all_tools_unique(self) -> None:
        """Test that all tools are unique (no duplicates)."""
        tools = helpers.load_all_tools()
        # Check uniqueness by comparing length with set of ids
        unique_ids = {id(tool) for tool in tools}
        assert len(unique_ids) == len(tools)

    def test_includes_all_module_tools(self) -> None:
        """Test that load_all_tools includes tools from all modules."""
        all_tools = helpers.load_all_tools()
        tool_names = {tool.__name__ for tool in all_tools}

        # Check presence of tools from each module
        assert "parse_python_ast" in tool_names  # analysis
        assert "get_git_status" in tool_names  # git
        assert "profile_function" in tool_names  # profiling
        assert "parse_ruff_json" in tool_names  # quality
        assert "validate_shell_syntax" in tool_names  # shell
        assert "validate_python_syntax" in tool_names  # python
        assert "create_sqlite_database" in tool_names  # database


class TestGetToolInfo:
    """Tests for get_tool_info function."""

    def test_get_tool_info_returns_dict(self) -> None:
        """Test that get_tool_info returns a dictionary."""
        analysis_tools = helpers.load_all_analysis_tools()
        tool = analysis_tools[0]

        info = helpers.get_tool_info(tool)
        assert isinstance(info, dict)

    def test_get_tool_info_contains_required_keys(self) -> None:
        """Test that tool info contains all required keys."""
        analysis_tools = helpers.load_all_analysis_tools()
        tool = analysis_tools[0]

        info = helpers.get_tool_info(tool)
        assert "name" in info
        assert "docstring" in info
        assert "signature" in info
        assert "module" in info
        assert "parameters" in info

    def test_get_tool_info_name_matches(self) -> None:
        """Test that tool info name matches function name."""
        from coding_open_agent_tools.analysis import parse_python_ast

        info = helpers.get_tool_info(parse_python_ast)
        assert info["name"] == "parse_python_ast"

    def test_get_tool_info_raises_on_non_callable(self) -> None:
        """Test that get_tool_info raises TypeError for non-callable."""
        import pytest

        with pytest.raises(TypeError, match="Tool must be callable"):
            helpers.get_tool_info("not a function")  # type: ignore


class TestListAllAvailableTools:
    """Tests for list_all_available_tools function."""

    def test_list_all_available_tools_returns_dict(self) -> None:
        """Test that list_all_available_tools returns a dictionary."""
        tools = helpers.list_all_available_tools()
        assert isinstance(tools, dict)

    def test_list_all_available_tools_has_all_categories(self) -> None:
        """Test that all module categories are present."""
        tools = helpers.list_all_available_tools()
        assert "analysis" in tools
        assert "git" in tools
        assert "profiling" in tools
        assert "quality" in tools
        assert "shell" in tools
        assert "python" in tools
        assert "database" in tools

    def test_list_all_available_tools_values_are_lists(self) -> None:
        """Test that each category contains a list."""
        tools = helpers.list_all_available_tools()
        for category, tool_list in tools.items():
            assert isinstance(tool_list, list)

    def test_list_all_available_tools_items_are_dicts(self) -> None:
        """Test that each tool info is a dictionary."""
        tools = helpers.list_all_available_tools()
        for category, tool_list in tools.items():
            for tool_info in tool_list:
                assert isinstance(tool_info, dict)
                assert "name" in tool_info
                assert "docstring" in tool_info


class TestHelperIntegration:
    """Integration tests for helper functions."""

    def test_merge_with_loaded_tools(self) -> None:
        """Test merging loaded tool lists."""
        analysis_tools = helpers.load_all_analysis_tools()
        git_tools = helpers.load_all_git_tools()

        merged = helpers.merge_tool_lists(analysis_tools, git_tools)
        assert len(merged) == 14 + 79

    def test_load_all_tools_equals_merged_tools(self) -> None:
        """Test that load_all_tools equals manually merging all tool lists."""
        all_tools = helpers.load_all_tools()

        manual_merge = helpers.merge_tool_lists(
            helpers.load_all_analysis_tools(),
            helpers.load_all_git_tools(),
            helpers.load_all_profiling_tools(),
            helpers.load_all_quality_tools(),
            helpers.load_all_shell_tools(),
            helpers.load_all_python_tools(),
            helpers.load_all_database_tools(),
        )

        assert len(all_tools) == len(manual_merge)

        # Check all tools are present
        all_tool_ids = {id(tool) for tool in all_tools}
        manual_tool_ids = {id(tool) for tool in manual_merge}
        assert all_tool_ids == manual_tool_ids

    def test_repeated_calls_return_same_tools(self) -> None:
        """Test that repeated calls return the same tool functions."""
        tools1 = helpers.load_all_tools()
        tools2 = helpers.load_all_tools()

        # Should be the same function objects
        ids1 = [id(tool) for tool in tools1]
        ids2 = [id(tool) for tool in tools2]
        assert ids1 == ids2
