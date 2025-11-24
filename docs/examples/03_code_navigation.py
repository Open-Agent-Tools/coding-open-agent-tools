"""Example: Navigate code without reading full files.

Demonstrates token-efficient code navigation that saves 70-95% of tokens
compared to reading entire files to find specific information.

Token Savings: 70-95% (targeted extraction vs full file reading)
"""

from coding_open_agent_tools.python import navigation

# Sample Python code for demonstration
source_code = """
'''Module for data processing and analysis.

This module provides utilities for processing and analyzing
various types of data structures.
'''

import json
import os
from typing import Any, Dict, List
from collections import defaultdict

def calculate_total(items: list[int]) -> int:
    '''Calculate the total of all items.

    Args:
        items: List of integers to sum

    Returns:
        The sum of all items

    Example:
        >>> calculate_total([1, 2, 3])
        6
    '''
    return sum(items)

def process_data(data: dict[str, Any]) -> str:
    '''Process input data and return formatted string.

    Args:
        data: Dictionary of data to process

    Returns:
        Processed data as JSON string

    Raises:
        ValueError: If data is empty
    '''
    if not data:
        raise ValueError("Data cannot be empty")
    return json.dumps(data, indent=2)

class DataProcessor:
    '''Main data processor class.

    Handles various data processing operations including
    validation, transformation, and analysis.
    '''

    def __init__(self, config: dict[str, Any]):
        '''Initialize the data processor.

        Args:
            config: Configuration dictionary
        '''
        self.config = config
        self.cache = defaultdict(list)

    def validate(self, data: Any) -> bool:
        '''Validate input data.

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        '''
        return data is not None

def helper_function(x: int, y: int) -> int:
    '''Simple helper function.'''
    return x + y
"""

# Example 1: List all functions (most token-efficient overview)
print("=" * 60)
print("Example 1: List all functions in module")
print("=" * 60)

functions = navigation.list_python_functions(source_code)
print(f"Functions found: {functions['functions']}")
print(f"Count: {functions['count']}")
print(f"Has functions: {functions['has_functions']}")
print()

# Example 2: Get function signature (no need to read full function)
print("=" * 60)
print("Example 2: Get function signature without reading full code")
print("=" * 60)

signature = navigation.get_python_function_signature(source_code, "calculate_total")
print("Function: calculate_total")
print(f"Signature: {signature['signature']}")
print(f"Has return type: {signature['has_return_type']}")
print()

# Example 3: Get function docstring (quick documentation lookup)
print("=" * 60)
print("Example 3: Get function docstring")
print("=" * 60)

docstring = navigation.get_python_function_docstring(source_code, "process_data")
print("Function: process_data")
print(f"Docstring: {docstring['docstring'][:100]}...")
print(f"Has docstring: {docstring['has_docstring']}")
print()

# Example 4: Get module overview (comprehensive summary)
print("=" * 60)
print("Example 4: Get complete module overview")
print("=" * 60)

overview = navigation.get_python_module_overview(source_code)
print(f"Function names: {overview['function_names']}")
print(f"Function count: {overview['function_count']}")
print(f"Class names: {overview['class_names']}")
print(f"Class count: {overview['class_count']}")
print(f"Has module docstring: {overview['has_module_docstring']}")
print(f"Import count: {overview['import_count']}")
print()

# Example 5: Get line numbers for targeted reading
print("=" * 60)
print("Example 5: Get line numbers for targeted file reading")
print("=" * 60)

line_nums = navigation.get_python_function_line_numbers(source_code, "process_data")
print("Function: process_data")
print(f"Start line: {line_nums['start_line']}")
print(f"End line: {line_nums['end_line']}")
print(f"Line count: {line_nums['line_count']}")
print()
print("Now you can use Read tool with offset/limit:")
print(
    f"  Read(file_path='module.py', offset={line_nums['start_line']}, limit={line_nums['line_count']})"
)
print()

# Example 6: Check if function exists (quick validation)
print("=" * 60)
print("Example 6: Check if function exists")
print("=" * 60)

exists_check = navigation.check_python_function_exists(source_code, "calculate_total")
print(f"Function 'calculate_total' exists: {exists_check['exists']}")

missing_check = navigation.check_python_function_exists(
    source_code, "nonexistent_function"
)
print(f"Function 'nonexistent_function' exists: {missing_check['exists']}")
print()

# Example 7: List all classes
print("=" * 60)
print("Example 7: List all classes in module")
print("=" * 60)

classes = navigation.list_python_classes(source_code)
print(f"Classes found: {classes['classes']}")
print(f"Count: {classes['count']}")
print()

# Example 8: Get class methods
print("=" * 60)
print("Example 8: Get methods for a specific class")
print("=" * 60)

methods = navigation.get_python_class_methods(source_code, "DataProcessor")
print("Class: DataProcessor")
print(f"Methods: {methods['methods']}")
print(f"Method count: {methods['method_count']}")
print()

# Why this saves tokens:
print("=" * 60)
print("TOKEN SAVINGS BREAKDOWN")
print("=" * 60)
print("""
Scenario: Agent wants to understand a 500-line Python file

Without navigation tools:
1. Read entire file (500 lines × 2 tokens/line = 1000 tokens)
2. Agent processes full content (500 tokens reasoning)
3. Agent extracts relevant info (200 tokens)
4. Total: ~1700 tokens

With navigation tools:
1. get_python_module_overview() (50 tokens structured response)
2. Agent identifies relevant function (50 tokens reasoning)
3. get_python_function_line_numbers() (20 tokens response)
4. Read specific function only (30 lines × 2 tokens = 60 tokens)
5. Total: ~180 tokens

Token savings: 89% (1520 tokens saved)

Real-world benefits:
- Find functions without reading full files
- Get signatures without implementation details
- Check existence without parsing
- Get line numbers for targeted reading
- Build navigation indexes efficiently

For a typical codebase with 100 files:
- Without: 170,000 tokens to understand structure
- With: 18,000 tokens for complete navigation
- Savings: ~152,000 tokens (89%)
""")
