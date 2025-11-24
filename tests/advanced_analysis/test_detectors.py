"""Tests for advanced code analysis detectors."""

import json

import pytest

from coding_open_agent_tools.advanced_analysis.detectors import (
    analyze_import_cycles,
    check_gdpr_compliance,
    detect_circular_imports,
    detect_license_violations,
    detect_memory_leak_patterns,
    detect_sql_injection_patterns,
    find_blocking_io,
    find_unused_dependencies,
    find_xss_vulnerabilities,
    identify_n_squared_loops,
    scan_for_hardcoded_credentials,
    validate_accessibility,
)


class TestDetectCircularImports:
    """Tests for detect_circular_imports function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="import_graph_json must be a string"):
            detect_circular_imports(123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="import_graph_json cannot be empty"):
            detect_circular_imports("")

    def test_invalid_json(self):
        """Test that function handles invalid JSON."""
        result = detect_circular_imports("{invalid json}")
        assert result["has_circular"] == "false"
        assert result["cycle_count"] == "0"
        assert "Invalid JSON" in result["error"]

    def test_no_circular_imports(self):
        """Test detection with no circular imports."""
        graph = {"a": ["b"], "b": ["c"], "c": []}
        result = detect_circular_imports(json.dumps(graph))
        assert result["has_circular"] == "false"
        assert result["cycle_count"] == "0"
        assert result["severity"] == "none"

    def test_simple_circular_import(self):
        """Test detection of simple A->B->A cycle."""
        graph = {"a": ["b"], "b": ["a"]}
        result = detect_circular_imports(json.dumps(graph))
        assert result["has_circular"] == "true"
        assert int(result["cycle_count"]) >= 1
        cycles = json.loads(result["cycles"])
        assert len(cycles) >= 1
        assert result["severity"] in ["low", "medium", "high"]

    def test_complex_circular_import(self):
        """Test detection of complex multi-module cycle."""
        graph = {"a": ["b"], "b": ["c"], "c": ["d"], "d": ["a"]}
        result = detect_circular_imports(json.dumps(graph))
        assert result["has_circular"] == "true"
        cycles = json.loads(result["cycles"])
        assert any(len(cycle) > 2 for cycle in cycles)
        assert result["severity"] in ["medium", "high"]

    def test_self_referencing_import(self):
        """Test detection of module importing itself."""
        graph = {"a": ["a"]}
        result = detect_circular_imports(json.dumps(graph))
        assert result["has_circular"] == "true"
        cycles = json.loads(result["cycles"])
        assert any("a" in cycle for cycle in cycles)


class TestFindUnusedDependencies:
    """Tests for find_unused_dependencies function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="dependencies_json must be a string"):
            find_unused_dependencies(123, "[]")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="imports_json must be a string"):
            find_unused_dependencies("[]", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="dependencies_json cannot be empty"):
            find_unused_dependencies("", "[]")
        with pytest.raises(ValueError, match="imports_json cannot be empty"):
            find_unused_dependencies("[]", "")

    def test_no_unused_dependencies(self):
        """Test when all dependencies are used."""
        deps = ["requests", "numpy", "pandas"]
        imports = ["import requests", "import numpy", "import pandas"]
        result = find_unused_dependencies(json.dumps(deps), json.dumps(imports))
        assert result["has_unused"] == "false"
        assert result["unused_count"] == "0"

    def test_unused_dependencies(self):
        """Test detection of unused dependencies."""
        deps = ["requests", "numpy", "pandas", "flask"]
        imports = ["import requests", "import numpy"]
        result = find_unused_dependencies(json.dumps(deps), json.dumps(imports))
        assert result["has_unused"] == "true"
        assert int(result["unused_count"]) == 2
        unused = json.loads(result["unused_dependencies"])
        assert "pandas" in unused
        assert "flask" in unused

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive."""
        deps = ["PyYAML", "NumPy"]
        imports = ["import yaml", "import numpy"]
        result = find_unused_dependencies(json.dumps(deps), json.dumps(imports))
        assert result["has_unused"] == "false"

    def test_normalized_package_names(self):
        """Test that package names are normalized (dashes to underscores)."""
        deps = ["python-dateutil", "google-cloud-storage"]
        imports = ["import dateutil", "import google.cloud.storage"]
        result = find_unused_dependencies(json.dumps(deps), json.dumps(imports))
        assert result["has_unused"] == "false"


class TestAnalyzeImportCycles:
    """Tests for analyze_import_cycles function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="import_graph_json must be a string"):
            analyze_import_cycles(123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="import_graph_json cannot be empty"):
            analyze_import_cycles("")

    def test_simple_import_graph(self):
        """Test analysis of simple import graph."""
        graph = {"a": ["b"], "b": ["c"], "c": []}
        result = analyze_import_cycles(json.dumps(graph))
        assert int(result["total_modules"]) == 3
        assert int(result["total_imports"]) == 2
        assert result["has_cycles"] == "false"
        assert float(result["average_imports_per_module"]) > 0

    def test_complex_import_graph(self):
        """Test analysis of complex import graph with cycles."""
        graph = {
            "a": ["b", "c"],
            "b": ["c", "d"],
            "c": ["d"],
            "d": ["a"],  # Cycle
        }
        result = analyze_import_cycles(json.dumps(graph))
        assert int(result["total_modules"]) == 4
        assert result["has_cycles"] == "true"
        assert int(result["cycle_count"]) >= 1
        assert float(result["complexity_score"]) > 0


class TestDetectSqlInjectionPatterns:
    """Tests for detect_sql_injection_patterns function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            detect_sql_injection_patterns(123, "python")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            detect_sql_injection_patterns("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            detect_sql_injection_patterns("", "python")
        with pytest.raises(ValueError, match="language cannot be empty"):
            detect_sql_injection_patterns("code", "")

    def test_safe_parameterized_query(self):
        """Test that parameterized queries are not flagged."""
        code = 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
        result = detect_sql_injection_patterns(code, "python")
        assert result["has_vulnerabilities"] == "false"
        assert result["vulnerability_count"] == "0"

    def test_string_concatenation_vulnerability(self):
        """Test detection of SQL injection via string concatenation."""
        code = 'query = "SELECT * FROM users WHERE name = \'" + user_input + "\'"'
        result = detect_sql_injection_patterns(code, "python")
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) >= 1
        vulns = json.loads(result["vulnerabilities"])
        assert any("concatenation" in str(v).lower() for v in vulns)

    def test_format_string_vulnerability(self):
        """Test detection of SQL injection via format strings."""
        code = 'query = f"SELECT * FROM users WHERE id = {user_id}"'
        result = detect_sql_injection_patterns(code, "python")
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) >= 1

    def test_javascript_sql_injection(self):
        """Test detection in JavaScript code."""
        code = 'db.query("SELECT * FROM users WHERE name = \'" + userName + "\'")'
        result = detect_sql_injection_patterns(code, "javascript")
        assert result["has_vulnerabilities"] == "true"

    def test_multiple_vulnerabilities(self):
        """Test detection of multiple SQL injection patterns."""
        code = """
        query1 = "SELECT * FROM users WHERE id = " + str(user_id)
        query2 = f"DELETE FROM logs WHERE user = {username}"
        db.execute("UPDATE users SET name = '%s'" % new_name)
        """
        result = detect_sql_injection_patterns(code, "python")
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) >= 2


class TestFindXssVulnerabilities:
    """Tests for find_xss_vulnerabilities function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            find_xss_vulnerabilities(123, "javascript")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            find_xss_vulnerabilities("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_xss_vulnerabilities("", "javascript")
        with pytest.raises(ValueError, match="language cannot be empty"):
            find_xss_vulnerabilities("code", "")

    def test_safe_text_content(self):
        """Test that safe DOM manipulation is not flagged."""
        code = "element.textContent = userInput;"
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "false"

    def test_innerhtml_vulnerability(self):
        """Test detection of innerHTML XSS."""
        code = "element.innerHTML = userInput;"
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) >= 1
        vulns = json.loads(result["vulnerabilities"])
        assert any("innerHTML" in str(v) for v in vulns)

    def test_document_write_vulnerability(self):
        """Test detection of document.write XSS."""
        code = "document.write(userData);"
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "true"
        vulns = json.loads(result["vulnerabilities"])
        assert any("document.write" in str(v) for v in vulns)

    def test_eval_vulnerability(self):
        """Test detection of eval() XSS."""
        code = 'eval("var x = " + userCode);'
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "true"

    def test_react_dangerously_set_html(self):
        """Test detection of React dangerouslySetInnerHTML."""
        code = "<div dangerouslySetInnerHTML={{__html: userContent}} />"
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "true"
        vulns = json.loads(result["vulnerabilities"])
        assert any("dangerouslySetInnerHTML" in str(v) for v in vulns)

    def test_multiple_xss_patterns(self):
        """Test detection of multiple XSS vulnerabilities."""
        code = """
        element.innerHTML = data;
        document.write(input);
        eval(userCode);
        """
        result = find_xss_vulnerabilities(code, "javascript")
        assert result["has_vulnerabilities"] == "true"
        assert int(result["vulnerability_count"]) >= 3


class TestScanForHardcodedCredentials:
    """Tests for scan_for_hardcoded_credentials function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            scan_for_hardcoded_credentials(123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            scan_for_hardcoded_credentials("")

    def test_no_credentials(self):
        """Test code with no hardcoded credentials."""
        code = """
        def connect_db():
            username = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            return connect(username, password)
        """
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "false"
        assert result["secret_count"] == "0"

    def test_password_detection(self):
        """Test detection of hardcoded password."""
        code = 'password = "SuperSecret123"'
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"
        assert int(result["secret_count"]) >= 1
        secrets = json.loads(result["secrets"])
        assert any("password" in str(s).lower() for s in secrets)

    def test_api_key_detection(self):
        """Test detection of hardcoded API key."""
        code = 'API_KEY = "sk-1234567890abcdef"'
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"
        secrets = json.loads(result["secrets"])
        assert any("api_key" in str(s).lower() or "sk-" in str(s) for s in secrets)

    def test_aws_key_detection(self):
        """Test detection of AWS credentials."""
        code = 'AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"
        secrets = json.loads(result["secrets"])
        assert any("aws" in str(s).lower() for s in secrets)

    def test_github_token_detection(self):
        """Test detection of GitHub token."""
        code = 'GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuv"'
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"
        secrets = json.loads(result["secrets"])
        assert any("github" in str(s).lower() or "ghp_" in str(s) for s in secrets)

    def test_openai_key_detection(self):
        """Test detection of OpenAI API key."""
        code = 'OPENAI_API_KEY = "sk-proj-1234567890abcdef"'
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"

    def test_multiple_secrets(self):
        """Test detection of multiple secrets."""
        code = """
        DB_PASSWORD = "secret123"
        API_KEY = "sk-1234567890"
        AWS_SECRET = "wJalrXUtnFEMI/K7MDENG"
        """
        result = scan_for_hardcoded_credentials(code)
        assert result["has_secrets"] == "true"
        assert int(result["secret_count"]) >= 3


class TestIdentifyNSquaredLoops:
    """Tests for identify_n_squared_loops function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            identify_n_squared_loops(123, "python")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            identify_n_squared_loops("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            identify_n_squared_loops("", "python")
        with pytest.raises(ValueError, match="language cannot be empty"):
            identify_n_squared_loops("code", "")

    def test_single_loop_no_antipattern(self):
        """Test that single loop is not flagged."""
        code = """
        for item in items:
            process(item)
        """
        result = identify_n_squared_loops(code, "python")
        assert result["has_anti_patterns"] == "false"
        assert result["pattern_count"] == "0"

    def test_nested_loop_different_collections(self):
        """Test nested loops over different collections."""
        code = """
        for user in users:
            for order in orders:
                process(user, order)
        """
        result = identify_n_squared_loops(code, "python")
        # Should be flagged as nested loop (potential O(n*m))
        assert result["has_anti_patterns"] == "true"

    def test_nested_loop_same_collection(self):
        """Test nested loop over same collection (O(n²))."""
        code = """
        for i in items:
            for j in items:
                compare(i, j)
        """
        result = identify_n_squared_loops(code, "python")
        assert result["has_anti_patterns"] == "true"
        assert int(result["pattern_count"]) >= 1
        patterns = json.loads(result["patterns"])
        assert any("same collection" in str(p).lower() for p in patterns)

    def test_triple_nested_loop(self):
        """Test deeply nested loops (O(n³))."""
        code = """
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    process(i, j, k)
        """
        result = identify_n_squared_loops(code, "python")
        assert result["has_anti_patterns"] == "true"
        assert result["severity"] == "high"

    def test_javascript_nested_loops(self):
        """Test detection in JavaScript code."""
        code = """
        for (let i = 0; i < arr.length; i++) {
            for (let j = 0; j < arr.length; j++) {
                compare(arr[i], arr[j]);
            }
        }
        """
        result = identify_n_squared_loops(code, "javascript")
        assert result["has_anti_patterns"] == "true"


class TestDetectMemoryLeakPatterns:
    """Tests for detect_memory_leak_patterns function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            detect_memory_leak_patterns(123, "python")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            detect_memory_leak_patterns("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            detect_memory_leak_patterns("", "python")
        with pytest.raises(ValueError, match="language cannot be empty"):
            detect_memory_leak_patterns("code", "")

    def test_safe_file_handling(self):
        """Test that proper file handling is not flagged."""
        code = """
        with open('file.txt', 'r') as f:
            data = f.read()
        """
        result = detect_memory_leak_patterns(code, "python")
        assert result["has_leak_patterns"] == "false"

    def test_unclosed_file_handle(self):
        """Test detection of unclosed file handle."""
        code = """
        f = open('file.txt', 'r')
        data = f.read()
        # Missing f.close()
        """
        result = detect_memory_leak_patterns(code, "python")
        assert result["has_leak_patterns"] == "true"
        assert int(result["pattern_count"]) >= 1
        patterns = json.loads(result["patterns"])
        assert any(
            "file" in str(p).lower() or "close" in str(p).lower() for p in patterns
        )

    def test_unremoved_event_listener(self):
        """Test detection of unremoved event listeners."""
        code = """
        element.addEventListener('click', handler);
        // Missing removeEventListener
        """
        result = detect_memory_leak_patterns(code, "javascript")
        assert result["has_leak_patterns"] == "true"
        patterns = json.loads(result["patterns"])
        assert any("listener" in str(p).lower() for p in patterns)

    def test_uncleaned_interval(self):
        """Test detection of uncleaned setInterval."""
        code = """
        setInterval(() => {
            updateData();
        }, 1000);
        // Missing clearInterval
        """
        result = detect_memory_leak_patterns(code, "javascript")
        assert result["has_leak_patterns"] == "true"
        patterns = json.loads(result["patterns"])
        assert any(
            "interval" in str(p).lower() or "timeout" in str(p).lower()
            for p in patterns
        )

    def test_global_list_accumulation(self):
        """Test detection of global list/array accumulation."""
        code = """
        global_cache = []
        def process_data(item):
            global_cache.append(item)  # Never cleared
        """
        result = detect_memory_leak_patterns(code, "python")
        assert result["has_leak_patterns"] == "true"

    def test_multiple_leak_patterns(self):
        """Test detection of multiple leak patterns."""
        code = """
        f = open('data.txt', 'r')
        data = f.read()

        element.addEventListener('click', handler);

        cache = []
        cache.append(large_object)
        """
        result = detect_memory_leak_patterns(code, "javascript")
        assert result["has_leak_patterns"] == "true"
        assert int(result["pattern_count"]) >= 2


class TestFindBlockingIo:
    """Tests for find_blocking_io function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            find_blocking_io(123, "python")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            find_blocking_io("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            find_blocking_io("", "python")
        with pytest.raises(ValueError, match="language cannot be empty"):
            find_blocking_io("code", "")

    def test_async_operations_not_flagged(self):
        """Test that async operations are not flagged."""
        code = """
        async def fetch_data():
            response = await aiohttp.get('https://api.example.com')
            return await response.json()
        """
        result = find_blocking_io(code, "python")
        assert result["has_blocking_io"] == "false"

    def test_sync_http_request(self):
        """Test detection of synchronous HTTP request."""
        code = "response = requests.get('https://api.example.com')"
        result = find_blocking_io(code, "python")
        assert result["has_blocking_io"] == "true"
        assert int(result["blocking_count"]) >= 1
        operations = json.loads(result["operations"])
        assert any(
            "http" in str(op).lower() or "request" in str(op).lower()
            for op in operations
        )

    def test_sync_file_io(self):
        """Test detection of synchronous file I/O."""
        code = """
        with open('large_file.txt', 'r') as f:
            data = f.read()
        """
        result = find_blocking_io(code, "python")
        assert result["has_blocking_io"] == "true"
        operations = json.loads(result["operations"])
        assert any("file" in str(op).lower() for op in operations)

    def test_time_sleep(self):
        """Test detection of time.sleep()."""
        code = "time.sleep(5)"
        result = find_blocking_io(code, "python")
        assert result["has_blocking_io"] == "true"
        operations = json.loads(result["operations"])
        assert any("sleep" in str(op).lower() for op in operations)

    def test_javascript_xhr_sync(self):
        """Test detection of synchronous XMLHttpRequest."""
        code = """
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/api/data', false);  // false = synchronous
        xhr.send();
        """
        result = find_blocking_io(code, "javascript")
        assert result["has_blocking_io"] == "true"

    def test_javascript_fs_sync(self):
        """Test detection of Node.js synchronous file operations."""
        code = "const data = fs.readFileSync('file.txt', 'utf8');"
        result = find_blocking_io(code, "javascript")
        assert result["has_blocking_io"] == "true"

    def test_multiple_blocking_operations(self):
        """Test detection of multiple blocking I/O operations."""
        code = """
        response = requests.get('https://api.example.com')
        time.sleep(1)
        with open('data.txt', 'r') as f:
            data = f.read()
        """
        result = find_blocking_io(code, "python")
        assert result["has_blocking_io"] == "true"
        assert int(result["blocking_count"]) >= 3


class TestCheckGdprCompliance:
    """Tests for check_gdpr_compliance function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            check_gdpr_compliance(123, "python")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="language must be a string"):
            check_gdpr_compliance("code", 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            check_gdpr_compliance("", "python")
        with pytest.raises(ValueError, match="language cannot be empty"):
            check_gdpr_compliance("code", "")

    def test_compliant_code(self):
        """Test code with proper GDPR practices."""
        code = """
        if user_consent and user_consent.analytics_approved:
            encrypted_email = encrypt(user.email)
            log_action(user.id, 'login', encrypted_email)
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "false"
        assert result["issue_count"] == "0"

    def test_pii_without_consent(self):
        """Test detection of PII processing without consent check."""
        code = """
        user_email = request.form.get('email')
        send_marketing_email(user_email)
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "true"
        assert int(result["issue_count"]) >= 1
        issues = json.loads(result["issues"])
        assert any("consent" in str(i).lower() for i in issues)

    def test_unencrypted_pii(self):
        """Test detection of unencrypted PII."""
        code = """
        db.execute("INSERT INTO logs VALUES (?, ?)", (user.email, action))
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "true"
        issues = json.loads(result["issues"])
        assert any("encrypt" in str(i).lower() for i in issues)

    def test_missing_audit_trail(self):
        """Test detection of PII access without audit logging."""
        code = """
        def get_user_data(user_id):
            user = db.query("SELECT * FROM users WHERE id = ?", (user_id,))
            return user
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "true"
        issues = json.loads(result["issues"])
        assert any("audit" in str(i).lower() or "log" in str(i).lower() for i in issues)

    def test_missing_retention_policy(self):
        """Test detection of data storage without retention policy."""
        code = """
        db.execute("INSERT INTO user_history VALUES (?, ?, ?)",
                   (user.id, user.email, datetime.now()))
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "true"

    def test_multiple_compliance_issues(self):
        """Test detection of multiple GDPR issues."""
        code = """
        # No consent check
        user_email = request.form['email']
        user_phone = request.form['phone']

        # No encryption
        db.execute("INSERT INTO contacts VALUES (?, ?)", (user_email, user_phone))

        # No audit log
        # No retention policy
        """
        result = check_gdpr_compliance(code, "python")
        assert result["has_compliance_issues"] == "true"
        assert int(result["issue_count"]) >= 2


class TestValidateAccessibility:
    """Tests for validate_accessibility function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="source_code must be a string"):
            validate_accessibility(123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="source_code cannot be empty"):
            validate_accessibility("")

    def test_accessible_html(self):
        """Test HTML with proper accessibility."""
        code = """
        <img src="logo.png" alt="Company logo" />
        <button aria-label="Submit form">Submit</button>
        <input type="text" id="name" aria-label="Your name" />
        <main><h1>Welcome</h1></main>
        """
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "false"
        assert result["issue_count"] == "0"

    def test_missing_alt_text(self):
        """Test detection of images without alt text."""
        code = '<img src="photo.jpg" />'
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "true"
        assert int(result["issue_count"]) >= 1
        issues = json.loads(result["issues"])
        assert any("alt" in str(i).lower() for i in issues)

    def test_button_without_label(self):
        """Test detection of buttons without accessible labels."""
        code = '<button><i class="icon"></i></button>'
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "true"
        issues = json.loads(result["issues"])
        assert any(
            "button" in str(i).lower() or "label" in str(i).lower() for i in issues
        )

    def test_input_without_label(self):
        """Test detection of inputs without labels."""
        code = '<input type="text" placeholder="Enter name" />'
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "true"
        issues = json.loads(result["issues"])
        assert any(
            "input" in str(i).lower() or "label" in str(i).lower() for i in issues
        )

    def test_non_semantic_html(self):
        """Test detection of non-semantic HTML structure."""
        code = """
        <div class="container">
            <div class="header">Title</div>
            <div class="content">Content here</div>
        </div>
        """
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "true"
        issues = json.loads(result["issues"])
        assert any("semantic" in str(i).lower() for i in issues)

    def test_wcag_level_detection(self):
        """Test WCAG level is correctly assigned."""
        code = '<img src="image.jpg" />'
        result = validate_accessibility(code)
        assert result["wcag_level"] in ["A", "AA", "AAA"]

    def test_multiple_accessibility_issues(self):
        """Test detection of multiple accessibility issues."""
        code = """
        <div class="wrapper">
            <img src="banner.jpg" />
            <button><span class="icon"></span></button>
            <input type="email" placeholder="Email" />
        </div>
        """
        result = validate_accessibility(code)
        assert result["has_accessibility_issues"] == "true"
        assert int(result["issue_count"]) >= 3


class TestDetectLicenseViolations:
    """Tests for detect_license_violations function."""

    def test_type_validation(self):
        """Test that function validates input types."""
        with pytest.raises(TypeError, match="dependencies_json must be a string"):
            detect_license_violations(123, "MIT")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="project_license must be a string"):
            detect_license_violations('{"dep1": "MIT"}', 123)  # type: ignore[arg-type]

    def test_empty_input(self):
        """Test that function handles empty input."""
        with pytest.raises(ValueError, match="dependencies_json cannot be empty"):
            detect_license_violations("", "MIT")
        with pytest.raises(ValueError, match="project_license cannot be empty"):
            detect_license_violations('{"dep1": "MIT"}', "")

    def test_compatible_licenses(self):
        """Test that compatible licenses don't trigger violations."""
        deps = {"requests": "Apache-2.0", "numpy": "BSD-3-Clause", "click": "BSD"}
        result = detect_license_violations(json.dumps(deps), "MIT")
        assert result["has_violations"] == "false"
        assert result["violation_count"] == "0"

    def test_gpl_in_mit_project(self):
        """Test detection of GPL dependency in MIT project."""
        deps = {"some-lib": "GPL-3.0"}
        result = detect_license_violations(json.dumps(deps), "MIT")
        assert result["has_violations"] == "true"
        assert int(result["violation_count"]) >= 1
        violations = json.loads(result["violations"])
        assert any("gpl" in str(v).lower() for v in violations)
        assert result["severity"] in ["high", "critical"]

    def test_proprietary_in_gpl_project(self):
        """Test detection of proprietary license in GPL project."""
        deps = {"commercial-lib": "Proprietary"}
        result = detect_license_violations(json.dumps(deps), "GPL-3.0")
        assert result["has_violations"] == "true"
        violations = json.loads(result["violations"])
        assert any("proprietary" in str(v).lower() for v in violations)

    def test_lgpl_compatibility(self):
        """Test that LGPL is compatible with MIT/Apache projects."""
        deps = {"lgpl-lib": "LGPL-3.0"}
        result = detect_license_violations(json.dumps(deps), "MIT")
        assert result["has_violations"] == "false"

    def test_agpl_detection(self):
        """Test detection of AGPL license (most restrictive)."""
        deps = {"agpl-lib": "AGPL-3.0"}
        result = detect_license_violations(json.dumps(deps), "MIT")
        assert result["has_violations"] == "true"
        assert result["severity"] == "critical"

    def test_multiple_violations(self):
        """Test detection of multiple license violations."""
        deps = {
            "gpl-lib": "GPL-3.0",
            "agpl-lib": "AGPL-3.0",
            "proprietary-lib": "Proprietary",
        }
        result = detect_license_violations(json.dumps(deps), "Apache-2.0")
        assert result["has_violations"] == "true"
        assert int(result["violation_count"]) >= 3

    def test_case_insensitive_license_matching(self):
        """Test that license matching is case-insensitive."""
        deps = {"lib": "gpl-3.0"}  # lowercase
        result = detect_license_violations(json.dumps(deps), "mit")  # lowercase
        assert result["has_violations"] == "true"

    def test_legal_risk_assessment(self):
        """Test that legal risk is properly assessed."""
        deps = {"gpl-lib": "GPL-3.0", "agpl-lib": "AGPL-3.0"}
        result = detect_license_violations(json.dumps(deps), "MIT")
        assert result["legal_risk"] in ["low", "medium", "high", "critical"]
