#!/usr/bin/env python3
"""
Parse Fandango test output and generate a diff-style comparison of all solutions.
Shows the differences between full request A and partial requests B for each test case.
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
        'request_full': None,
        'response_full': None,
        'request_part1': None,
        'response_part1': None,
        'request_part2': None,
        'response_part2': None,
        'split_point': None,
        'result': None
    }

    lines = content.split('\n')
    solution_num = 1

    for line in lines:
        # Detect full request
        if 'ClientA: <req_full>' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_full'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect full response
        elif 'ServerA: <response_full>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_full'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect part1 requests (various split points)
        elif 'ClientB: <req_' in line and '_p1>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                req = match.group(1)
                current_solution['request_part1'] = req.replace('\\r\\n', '\n').replace('\\n', '\n')
                # Extract split point from Range header
                range_match = re.search(r'Range: bytes=0-(\d+)', req)
                if range_match:
                    current_solution['split_point'] = int(range_match.group(1)) + 1

        # Detect part1 responses
        elif 'ServerB: <resp_' in line and '_p1>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_part1'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect part2 requests
        elif 'ClientB: <req_' in line and '_p2>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_part2'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Detect part2 responses
        elif 'ServerB: <resp_' in line and '_p2>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_part2'] = match.group(1).replace('\\r\\n', '\n').replace('\\n', '\n')

        # Starting new protocol run means save current and reset
        elif 'Starting new protocol run' in line:
            if current_solution['request_full'] and current_solution['response_part2']:
                current_solution['num'] = solution_num
                current_solution['result'] = '[PASS]'
                solutions.append(current_solution.copy())
                solution_num += 1
            current_solution = {
                'request_full': None,
                'response_full': None,
                'request_part1': None,
                'response_part1': None,
                'request_part2': None,
                'response_part2': None,
                'split_point': None,
                'result': None
            }

        # Detect explicit result
        elif '[PASS]' in line:
            pass  # Will be set when we see the complete solution
        elif '[VIOLATION]' in line:
            if solutions:
                solutions[-1]['result'] = '[VIOLATION] ' + line.strip()

    # Don't forget the last solution
    if current_solution['request_full'] and current_solution['response_part2']:
        current_solution['num'] = solution_num
        current_solution['result'] = '[PASS]'
        solutions.append(current_solution.copy())

    return solutions


def extract_body(response):
    """Extract body from HTTP response."""
    if not response:
        return ""
    idx = response.find('\n\n')
    if idx >= 0:
        return response[idx + 2:]
    return ""


def extract_content_length(response):
    """Extract Content-Length from response."""
    if not response:
        return 0
    match = re.search(r'Content-Length: (\d+)', response)
    return int(match.group(1)) if match else 0


def extract_content_range(response):
    """Extract Content-Range from response."""
    if not response:
        return ""
    match = re.search(r'Content-Range: ([^\n]+)', response)
    return match.group(1) if match else ""


def format_solution_diff(solution):
    """Format a single solution as a diff."""
    output = []
    output.append("=" * 80)
    output.append(f"SOLUTION #{solution['num']} - Split at byte {solution.get('split_point', 'N/A')}")
    output.append("=" * 80)

    # Result status
    result = solution.get('result') or ''
    if '[PASS]' in result or '[VIOLATION]' not in result:
        output.append("Result: PASS")
    else:
        output.append("Result: VIOLATION")
    output.append("")

    # Full request/response
    output.append("--- Full Request A (no Range header)")
    output.append(solution.get('request_full', '').strip())
    output.append("")

    full_body = extract_body(solution.get('response_full', ''))
    full_len = extract_content_length(solution.get('response_full', ''))
    output.append(f"--- Full Response A: {full_len} bytes")
    output.append(f"    Status: HTTP/1.1 200 OK")
    output.append(f"    Body preview: {full_body[:60]}...")
    output.append("")

    # Partial requests/responses
    output.append("+++ Partial Request B1 (Range: bytes=0-{})".format(solution.get('split_point', 0) - 1))
    output.append(solution.get('request_part1', '').strip())
    output.append("")

    part1_body = extract_body(solution.get('response_part1', ''))
    part1_len = extract_content_length(solution.get('response_part1', ''))
    part1_range = extract_content_range(solution.get('response_part1', ''))
    output.append(f"+++ Partial Response B1: {part1_len} bytes")
    output.append(f"    Status: HTTP/1.1 206 Partial Content")
    output.append(f"    Content-Range: {part1_range}")
    output.append(f"    Body preview: {part1_body[:60]}...")
    output.append("")

    output.append("+++ Partial Request B2 (Range: bytes={}-end)".format(solution.get('split_point', 0)))
    output.append(solution.get('request_part2', '').strip())
    output.append("")

    part2_body = extract_body(solution.get('response_part2', ''))
    part2_len = extract_content_length(solution.get('response_part2', ''))
    part2_range = extract_content_range(solution.get('response_part2', ''))
    output.append(f"+++ Partial Response B2: {part2_len} bytes")
    output.append(f"    Status: HTTP/1.1 206 Partial Content")
    output.append(f"    Content-Range: {part2_range}")
    output.append(f"    Body preview: {part2_body[:60]}...")
    output.append("")

    # Reconstruction check
    reconstructed = part1_body + part2_body
    output.append("@@ RECONSTRUCTION CHECK @@")
    output.append(f"    Full body length:         {len(full_body)} bytes")
    output.append(f"    Part1 length:             {len(part1_body)} bytes")
    output.append(f"    Part2 length:             {len(part2_body)} bytes")
    output.append(f"    Reconstructed length:     {len(reconstructed)} bytes")
    output.append(f"    Match: {'YES' if full_body == reconstructed else 'NO'}")
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
    output.append("RANGE REQUEST RECONSTRUCTION - METAMORPHIC TEST DIFF REPORT")
    output.append("RFC 7233: HTTP Range Requests")
    output.append("=" * 80)
    output.append(f"Total Solutions: {len(solutions)}")
    passed = sum(1 for s in solutions if '[VIOLATION]' not in (s.get('result') or ''))
    violations = len(solutions) - passed
    output.append(f"Passed: {passed}")
    output.append(f"Violations: {violations}")
    output.append("")
    output.append("Metamorphic Relation:")
    output.append("  A: Full GET request returns complete content (200 OK)")
    output.append("  B: Two partial GET requests with Range headers (206 Partial Content)")
    output.append("  Relation: Concatenated B1 + B2 body must equal A body exactly")
    output.append("")

    for solution in solutions:
        output.append(format_solution_diff(solution))

    # Summary
    output.append("=" * 80)
    output.append("SUMMARY")
    output.append("=" * 80)
    for solution in solutions:
        result = solution.get('result') or ''
        status = "PASS" if '[VIOLATION]' not in result else "VIOLATION"
        split = solution.get('split_point', 'N/A')
        output.append(f"Solution #{solution['num']}: {status} - Split at byte {split}")

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
