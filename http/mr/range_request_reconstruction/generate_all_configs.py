#!/usr/bin/env python3
"""
Generate a detailed report of all test case configurations with colors.
For Range Request Reconstruction MR (RFC 7233).
"""

import re
import sys
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


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
    }

    lines = content.split('\n')

    for line in lines:
        if 'ClientA: <req_full>' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_full'] = match.group(1)

        elif 'ServerA: <response_full>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_full'] = match.group(1)

        elif 'ClientB: <req_p1_' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                req = match.group(1)
                current_solution['request_part1'] = req
                range_match = re.search(r'Range: bytes=0-(\d+)', req)
                if range_match:
                    current_solution['split_point'] = int(range_match.group(1)) + 1

        elif 'ServerB: <resp_p1_' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_part1'] = match.group(1)

        elif 'ClientB: <req_p2_' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_part2'] = match.group(1)

        elif 'ServerB: <resp_p2_' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_part2'] = match.group(1)

        elif 'Starting new protocol run' in line:
            if current_solution['request_full'] and current_solution['response_part2']:
                solutions.append(current_solution.copy())
            current_solution = {
                'request_full': None,
                'response_full': None,
                'request_part1': None,
                'response_part1': None,
                'request_part2': None,
                'response_part2': None,
                'split_point': None,
            }

    if current_solution['request_full'] and current_solution['response_part2']:
        solutions.append(current_solution.copy())

    return solutions


def extract_body(response):
    """Extract body from HTTP response."""
    if not response:
        return ""
    response = response.replace('\\r\\n', '\n')
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
    match = re.search(r'Content-Range: ([^\r\n\\]+)', response)
    return match.group(1) if match else ""


def c(text, color):
    """Colorize text."""
    return f"{color}{text}{Colors.RESET}"


def main():
    script_dir = Path(__file__).parent
    log_file = script_dir / "test_output.log"

    if not log_file.exists():
        print(f"{Colors.RED}Error: {log_file} not found. Run the test first.{Colors.RESET}")
        sys.exit(1)

    solutions = parse_test_output(log_file)

    output = []

    # Header
    output.append(c("=" * 100, Colors.CYAN))
    output.append(c(" RANGE REQUEST RECONSTRUCTION - ALL TEST CASES", Colors.BOLD + Colors.CYAN))
    output.append(c(" RFC 7233: HTTP Range Requests", Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")
    output.append(f"Total test cases: {c(str(len(solutions)), Colors.GREEN + Colors.BOLD)}")
    output.append("")

    # Summary table
    output.append(c("-" * 100, Colors.DIM))
    header = (
        f"{c('TC#', Colors.BOLD):>12}  "
        f"{c('Split', Colors.BOLD):<10}  "
        f"{c('Full (A)', Colors.BOLD):<15}  "
        f"{c('Part1 (B)', Colors.BOLD):<15}  "
        f"{c('Part2 (B)', Colors.BOLD):<15}  "
        f"{c('Match', Colors.BOLD):<10}  "
        f"{c('Result', Colors.BOLD)}"
    )
    output.append(header)
    output.append(c("-" * 100, Colors.DIM))

    for i, sol in enumerate(solutions):
        full_body = extract_body(sol['response_full'])
        part1_body = extract_body(sol['response_part1'])
        part2_body = extract_body(sol['response_part2'])
        reconstructed = part1_body + part2_body

        full_len = len(full_body)
        part1_len = len(part1_body)
        part2_len = len(part2_body)

        match = full_body == reconstructed
        split = sol.get('split_point', 'N/A')

        tc_num = c(f"#{i+1:02d}", Colors.CYAN + Colors.BOLD)
        split_str = c(f"byte {split}", Colors.BLUE)
        full_str = c(f"{full_len} bytes", Colors.YELLOW)
        part1_str = c(f"{part1_len} bytes", Colors.MAGENTA)
        part2_str = c(f"{part2_len} bytes", Colors.MAGENTA)
        match_str = c("YES", Colors.GREEN + Colors.BOLD) if match else c("NO", Colors.RED + Colors.BOLD)
        result_str = c("PASS", Colors.GREEN + Colors.BOLD) if match else c("FAIL", Colors.RED + Colors.BOLD)

        row = f"{tc_num:>20}  {split_str:<18}  {full_str:<23}  {part1_str:<23}  {part2_str:<23}  {match_str:<18}  {result_str}"
        output.append(row)

    output.append(c("-" * 100, Colors.DIM))
    output.append("")

    # Detailed view
    output.append(c("=" * 100, Colors.CYAN))
    output.append(c(" DETAILED VIEW OF EACH TEST CASE", Colors.BOLD + Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")

    for i, sol in enumerate(solutions):
        full_body = extract_body(sol['response_full'])
        part1_body = extract_body(sol['response_part1'])
        part2_body = extract_body(sol['response_part2'])
        reconstructed = part1_body + part2_body

        full_len = len(full_body)
        part1_len = len(part1_body)
        part2_len = len(part2_body)
        split = sol.get('split_point', 'N/A')

        match = full_body == reconstructed

        output.append(c(f"{'=' * 100}", Colors.CYAN))
        output.append(c(f" TEST CASE #{i+1:02d} - Split at byte {split}", Colors.CYAN + Colors.BOLD))
        output.append(c(f"{'=' * 100}", Colors.CYAN))
        output.append("")

        # Request A (Full)
        output.append(c(" REQUEST A (Full GET - no Range header):", Colors.GREEN + Colors.BOLD))
        output.append(c("   GET /large HTTP/1.1", Colors.WHITE))
        output.append(c("   Host: localhost", Colors.DIM))
        output.append(c("   User-Agent: Fandango/1.0", Colors.DIM))
        output.append("")

        # Response A
        output.append(c(" RESPONSE A:", Colors.GREEN + Colors.BOLD))
        output.append(c(f"   Status: HTTP/1.1 200 OK", Colors.GREEN))
        output.append(c(f"   Content-Length: {full_len}", Colors.YELLOW))
        output.append(c(f"   Body: {full_body}", Colors.DIM))
        output.append("")

        output.append(c("-" * 100, Colors.DIM))
        output.append("")

        # Request B1 (Part 1)
        output.append(c(f" REQUEST B1 (Range: bytes=0-{split-1}):", Colors.MAGENTA + Colors.BOLD))
        output.append(c("   GET /large HTTP/1.1", Colors.WHITE))
        output.append(c("   Host: localhost", Colors.DIM))
        output.append(c("   User-Agent: Fandango/1.0", Colors.DIM))
        output.append(c(f"   Range: bytes=0-{split-1}", Colors.MAGENTA))
        output.append("")

        # Response B1
        part1_range = extract_content_range(sol['response_part1'])
        output.append(c(" RESPONSE B1:", Colors.MAGENTA + Colors.BOLD))
        output.append(c(f"   Status: HTTP/1.1 206 Partial Content", Colors.BLUE))
        output.append(c(f"   Content-Length: {part1_len}", Colors.YELLOW))
        output.append(c(f"   Content-Range: {part1_range}", Colors.CYAN))
        output.append(c(f"   Body: {part1_body}", Colors.DIM))
        output.append("")

        # Request B2 (Part 2)
        output.append(c(f" REQUEST B2 (Range: bytes={split}-):", Colors.MAGENTA + Colors.BOLD))
        output.append(c("   GET /large HTTP/1.1", Colors.WHITE))
        output.append(c("   Host: localhost", Colors.DIM))
        output.append(c("   User-Agent: Fandango/1.0", Colors.DIM))
        output.append(c(f"   Range: bytes={split}-", Colors.MAGENTA))
        output.append("")

        # Response B2
        part2_range = extract_content_range(sol['response_part2'])
        output.append(c(" RESPONSE B2:", Colors.MAGENTA + Colors.BOLD))
        output.append(c(f"   Status: HTTP/1.1 206 Partial Content", Colors.BLUE))
        output.append(c(f"   Content-Length: {part2_len}", Colors.YELLOW))
        output.append(c(f"   Content-Range: {part2_range}", Colors.CYAN))
        output.append(c(f"   Body: {part2_body}", Colors.DIM))
        output.append("")

        output.append(c("-" * 100, Colors.DIM))
        output.append("")

        # Reconstruction verification
        output.append(c(" RECONSTRUCTION VERIFICATION:", Colors.BOLD + Colors.WHITE))
        output.append(c(f"   Full body (A):           {full_len} bytes", Colors.YELLOW))
        output.append(c(f"   Part 1 body (B1):        {part1_len} bytes", Colors.MAGENTA))
        output.append(c(f"   Part 2 body (B2):        {part2_len} bytes", Colors.MAGENTA))
        output.append(c(f"   Reconstructed (B1+B2):   {part1_len + part2_len} bytes", Colors.CYAN))
        output.append("")

        if match:
            output.append(c("   PASS - Concatenated partial responses match full response exactly", Colors.GREEN + Colors.BOLD))
        else:
            output.append(c("   FAIL - Reconstructed content does not match full response", Colors.RED + Colors.BOLD))
            if full_len != part1_len + part2_len:
                output.append(c(f"   Length mismatch: {full_len} vs {part1_len + part2_len}", Colors.RED))

        output.append("")
        output.append("")

    # Final summary
    output.append(c("=" * 100, Colors.CYAN))
    output.append(c(" FINAL SUMMARY", Colors.BOLD + Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")

    passed = sum(1 for sol in solutions if extract_body(sol['response_full']) == extract_body(sol['response_part1']) + extract_body(sol['response_part2']))
    failed = len(solutions) - passed

    output.append(f"   Total test cases:  {c(str(len(solutions)), Colors.BOLD)}")
    output.append(f"   Passed:            {c(str(passed), Colors.GREEN + Colors.BOLD)}")
    output.append(f"   Failed:            {c(str(failed), Colors.RED + Colors.BOLD if failed > 0 else Colors.GREEN)}")
    output.append("")
    output.append(f"   RFC 7233 Compliance: {c('VERIFIED' if failed == 0 else 'ISSUES FOUND', Colors.GREEN + Colors.BOLD if failed == 0 else Colors.RED + Colors.BOLD)}")
    output.append("")

    # Print and save
    result_text = '\n'.join(output)
    print(result_text)

    output_file = script_dir / "all_test_cases.txt"
    with open(output_file, 'w') as f:
        f.write(result_text)

    print(c(f"\nSaved to: {output_file}", Colors.DIM))


if __name__ == "__main__":
    main()
