#!/usr/bin/env python3
"""
Parse Fandango test output and generate a diff-style comparison of all solutions.
Shows the differences between request A (keep-alive) and request B (close) for each test case.
"""

import re
import sys
from pathlib import Path

def parse_test_output(log_file):
    """Parse the Fandango log and extract test cases."""
    with open(log_file, 'r') as f:
        content = f.read()

    solutions = []
    current_solution = {
        'request_A': None,
        'response_A': None,
        'request_B': None,
        'response_B': None,
        'result': None
    }

    lines = content.split('\n')
    solution_num = 1

    for line in lines:
        # Detect request A (any keepalive request)
        if 'ClientA:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_A'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect response A
        elif 'ServerA: <response_A>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_A'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect request B (any close request)
        elif 'ClientB:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_B'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect response B - this marks the end of a solution
        elif 'ServerB: <response_B>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_B'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Starting new protocol run means save current and reset
        elif 'Starting new protocol run' in line:
            if current_solution['request_A'] and current_solution['request_B']:
                current_solution['num'] = solution_num
                current_solution['result'] = '[PASS]'  # Default, will be updated
                solutions.append(current_solution.copy())
                solution_num += 1
            current_solution = {
                'request_A': None,
                'response_A': None,
                'request_B': None,
                'response_B': None,
                'result': None
            }

        # Detect explicit result
        elif '[PASS]' in line:
            if solutions:
                solutions[-1]['result'] = '[PASS]'
        elif '[VIOLATION]' in line:
            if solutions:
                solutions[-1]['result'] = '[VIOLATION] ' + line.strip()

    # Don't forget the last solution
    if current_solution['request_A'] and current_solution['request_B']:
        current_solution['num'] = solution_num
        current_solution['result'] = '[PASS]'
        solutions.append(current_solution.copy())

    return solutions


def generate_diff(text_a, text_b):
    """Generate a simple diff-style output between two texts."""
    lines_a = text_a.strip().split('\n') if text_a else []
    lines_b = text_b.strip().split('\n') if text_b else []

    diff_lines = []
    max_lines = max(len(lines_a), len(lines_b))

    for i in range(max_lines):
        line_a = lines_a[i] if i < len(lines_a) else ""
        line_b = lines_b[i] if i < len(lines_b) else ""

        if line_a == line_b:
            diff_lines.append(f"  {line_a}")
        else:
            if line_a:
                diff_lines.append(f"- {line_a}")
            if line_b:
                diff_lines.append(f"+ {line_b}")

    return '\n'.join(diff_lines)


def format_solution_diff(solution):
    """Format a single solution as a diff."""
    output = []
    output.append(f"=" * 80)
    output.append(f"SOLUTION #{solution['num']}")
    output.append(f"=" * 80)

    # Result status
    result = solution.get('result') or ''
    if '[PASS]' in result:
        output.append(f"Result: ✓ PASS")
    else:
        output.append(f"Result: ✗ VIOLATION")
    output.append("")

    # Request diff
    output.append("--- Request A (Connection: keep-alive)")
    output.append("+++ Request B (Connection: close)")
    output.append("@@ REQUEST @@")
    output.append(generate_diff(solution['request_A'], solution['request_B']))
    output.append("")

    # Response diff
    output.append("--- Response A (from keep-alive request)")
    output.append("+++ Response B (from close request)")
    output.append("@@ RESPONSE @@")
    output.append(generate_diff(solution['response_A'], solution['response_B']))
    output.append("")

    return '\n'.join(output)


def main():
    script_dir = Path(__file__).parent
    log_file = script_dir / "test_output.log"

    if not log_file.exists():
        print(f"Error: {log_file} not found. Run the test first.")
        sys.exit(1)

    solutions = parse_test_output(log_file)

    if not solutions:
        print("No solutions found in the log file.")
        sys.exit(1)

    # Generate diff output
    output = []
    output.append("=" * 80)
    output.append("CONNECTION HEADER VARIANTS - METAMORPHIC TEST DIFF REPORT")
    output.append("=" * 80)
    output.append(f"Total Solutions: {len(solutions)}")
    passed = sum(1 for s in solutions if '[PASS]' in (s.get('result') or ''))
    violations = len(solutions) - passed
    output.append(f"Passed: {passed}")
    output.append(f"Violations: {violations}")
    output.append("")
    output.append("Legend:")
    output.append("  - Line only in A (keep-alive)")
    output.append("  + Line only in B (close)")
    output.append("    Lines identical in both")
    output.append("")

    for solution in solutions:
        output.append(format_solution_diff(solution))

    # Summary
    output.append("=" * 80)
    output.append("SUMMARY")
    output.append("=" * 80)
    for solution in solutions:
        result = solution.get('result') or ''
        status = "✓ PASS" if '[PASS]' in result else "✗ VIOLATION"
        # Extract endpoint from request
        req = solution.get('request_A', '')
        endpoint_match = re.search(r'GET ([^\s]+)', req)
        endpoint = endpoint_match.group(1) if endpoint_match else "unknown"
        output.append(f"Solution #{solution['num']}: {status} - Endpoint: {endpoint}")

    output.append("=" * 80)

    diff_report = '\n'.join(output)

    # Save to file
    diff_file = script_dir / "diff_report.txt"
    with open(diff_file, 'w') as f:
        f.write(diff_report)

    print(diff_report)
    print(f"\nDiff report saved to: {diff_file}")


if __name__ == "__main__":
    main()
