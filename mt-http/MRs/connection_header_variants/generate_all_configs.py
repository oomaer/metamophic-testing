#!/usr/bin/env python3
"""
Generate a detailed report of all 25 test case configurations with colors.
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
        'request_A': None,
        'response_A': None,
        'request_B': None,
        'response_B': None,
    }

    lines = content.split('\n')

    for line in lines:
        if 'ClientA:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_A'] = match.group(1)

        elif 'ServerA:' in line and '<resp_A_' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_A'] = match.group(1)

        elif 'ClientB:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_B'] = match.group(1)

        elif 'ServerB:' in line and '<resp_B_' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_B'] = match.group(1)

        elif 'Starting new protocol run' in line:
            if current_solution['request_A'] and current_solution['request_B']:
                solutions.append(current_solution.copy())
            current_solution = {
                'request_A': None,
                'response_A': None,
                'request_B': None,
                'response_B': None,
            }

    if current_solution['request_A'] and current_solution['request_B']:
        solutions.append(current_solution.copy())

    return solutions


def parse_request(raw_request):
    """Parse raw request string into components."""
    lines = raw_request.replace('\\r\\n', '\n').strip().split('\n')
    if not lines:
        return {}

    request_line = lines[0]
    parts = request_line.split(' ')
    method = parts[0] if len(parts) > 0 else ""
    path = parts[1] if len(parts) > 1 else ""
    version = parts[2] if len(parts) > 2 else ""

    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()

    return {
        'method': method,
        'path': path,
        'version': version,
        'headers': headers,
    }


def parse_response(raw_response):
    """Parse raw response string into components."""
    if not raw_response:
        return {
            'status_code': '',
            'body': '',
        }

    match = re.match(r'HTTP/[\d.]+ (\d+)', raw_response.replace('\\r\\n', '\n'))
    status_code = match.group(1) if match else ""

    body = ""
    json_match = re.search(r'\{[^}]+\}', raw_response)
    if json_match:
        body = json_match.group(0)

    return {
        'status_code': status_code,
        'body': body,
    }


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
    output.append(c(" CONNECTION HEADER VARIANTS - ALL TEST CASES", Colors.BOLD + Colors.CYAN))
    output.append(c(" RFC 7230: HTTP Connection Header", Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")
    output.append(f"Total test cases: {c(str(len(solutions)), Colors.GREEN + Colors.BOLD)}")
    output.append("")

    # Column headers
    output.append(c("-" * 100, Colors.DIM))
    header = (
        f"{c('TC#', Colors.BOLD):>12}  "
        f"{c('Path', Colors.BOLD):<10}  "
        f"{c('User-Agent', Colors.BOLD):<15}  "
        f"{c('Accept', Colors.BOLD):<20}  "
        f"{c('Status', Colors.BOLD):<8}  "
        f"{c('Response Body', Colors.BOLD)}"
    )
    output.append(header)
    output.append(c("-" * 100, Colors.DIM))

    # Each test case
    for i, sol in enumerate(solutions):
        req = parse_request(sol['request_A'])
        resp = parse_response(sol['response_A'])

        tc_num = c(f"#{i+1:02d}", Colors.CYAN + Colors.BOLD)
        path = c(req.get('path', ''), Colors.BLUE)

        ua_full = req.get('headers', {}).get('User-Agent', '')
        ua_short = ua_full.split('/')[0] if '/' in ua_full else ua_full
        ua = c(ua_short, Colors.MAGENTA)

        accept = c(req.get('headers', {}).get('Accept', ''), Colors.YELLOW)

        status = req.get('headers', {}).get('Connection', '')
        status_code = resp.get('status_code', '')
        status_color = Colors.GREEN if status_code == '200' else Colors.RED
        status_display = c(status_code, status_color)

        body = resp.get('body', '')
        body_display = c(body[:35] + "..." if len(body) > 35 else body, Colors.DIM)

        row = f"{tc_num:>20}  {path:<18}  {ua:<23}  {accept:<28}  {status_display:<16}  {body_display}"
        output.append(row)

    output.append(c("-" * 100, Colors.DIM))
    output.append("")

    # Detailed view
    output.append(c("=" * 100, Colors.CYAN))
    output.append(c(" DETAILED VIEW OF EACH TEST CASE", Colors.BOLD + Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")

    for i, sol in enumerate(solutions):
        req_a = parse_request(sol['request_A'])
        req_b = parse_request(sol['request_B'])
        resp_a = parse_response(sol['response_A'])
        resp_b = parse_response(sol['response_B'])

        output.append(c(f"┌{'─' * 98}┐", Colors.CYAN))
        output.append(c(f"│ TEST CASE #{i+1:02d}", Colors.CYAN + Colors.BOLD) + " " * 85 + c("│", Colors.CYAN))
        output.append(c(f"├{'─' * 98}┤", Colors.CYAN))

        # Request A
        output.append(c("│", Colors.CYAN) + c(" REQUEST A (keep-alive):", Colors.GREEN + Colors.BOLD) + " " * 73 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Method:     {c(req_a.get('method', ''), Colors.WHITE)}" + " " * 80 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Path:       {c(req_a.get('path', ''), Colors.BLUE)}" + " " * (80 - len(req_a.get('path', ''))) + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Version:    {c(req_a.get('version', ''), Colors.WHITE)}" + " " * 72 + c("│", Colors.CYAN))

        ua = req_a.get('headers', {}).get('User-Agent', '')
        output.append(c("│", Colors.CYAN) + f"   User-Agent: {c(ua, Colors.MAGENTA)}" + " " * (80 - len(ua)) + c("│", Colors.CYAN))

        accept = req_a.get('headers', {}).get('Accept', '')
        output.append(c("│", Colors.CYAN) + f"   Accept:     {c(accept, Colors.YELLOW)}" + " " * (80 - len(accept)) + c("│", Colors.CYAN))

        conn_a = req_a.get('headers', {}).get('Connection', '')
        output.append(c("│", Colors.CYAN) + f"   Connection: {c(conn_a, Colors.GREEN)}" + " " * (80 - len(conn_a)) + c("│", Colors.CYAN))

        output.append(c("│", Colors.CYAN) + " " * 98 + c("│", Colors.CYAN))

        # Response A
        output.append(c("│", Colors.CYAN) + c(" RESPONSE A:", Colors.GREEN + Colors.BOLD) + " " * 85 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Status:     {c(resp_a.get('status_code', ''), Colors.GREEN)}" + " " * 80 + c("│", Colors.CYAN))

        body_a = resp_a.get('body', '')
        output.append(c("│", Colors.CYAN) + f"   Body:       {c(body_a, Colors.DIM)}" + " " * (80 - len(body_a)) + c("│", Colors.CYAN))

        output.append(c("│", Colors.CYAN) + " " * 98 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + c("─" * 98, Colors.DIM) + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + " " * 98 + c("│", Colors.CYAN))

        # Request B
        output.append(c("│", Colors.CYAN) + c(" REQUEST B (close):", Colors.RED + Colors.BOLD) + " " * 78 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Method:     {c(req_b.get('method', ''), Colors.WHITE)}" + " " * 80 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Path:       {c(req_b.get('path', ''), Colors.BLUE)}" + " " * (80 - len(req_b.get('path', ''))) + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Version:    {c(req_b.get('version', ''), Colors.WHITE)}" + " " * 72 + c("│", Colors.CYAN))

        ua_b = req_b.get('headers', {}).get('User-Agent', '')
        output.append(c("│", Colors.CYAN) + f"   User-Agent: {c(ua_b, Colors.MAGENTA)}" + " " * (80 - len(ua_b)) + c("│", Colors.CYAN))

        accept_b = req_b.get('headers', {}).get('Accept', '')
        output.append(c("│", Colors.CYAN) + f"   Accept:     {c(accept_b, Colors.YELLOW)}" + " " * (80 - len(accept_b)) + c("│", Colors.CYAN))

        conn_b = req_b.get('headers', {}).get('Connection', '')
        output.append(c("│", Colors.CYAN) + f"   Connection: {c(conn_b, Colors.RED)}" + " " * (80 - len(conn_b)) + c("│", Colors.CYAN))

        output.append(c("│", Colors.CYAN) + " " * 98 + c("│", Colors.CYAN))

        # Response B
        output.append(c("│", Colors.CYAN) + c(" RESPONSE B:", Colors.RED + Colors.BOLD) + " " * 85 + c("│", Colors.CYAN))
        output.append(c("│", Colors.CYAN) + f"   Status:     {c(resp_b.get('status_code', ''), Colors.GREEN)}" + " " * 80 + c("│", Colors.CYAN))

        body_b = resp_b.get('body', '')
        output.append(c("│", Colors.CYAN) + f"   Body:       {c(body_b, Colors.DIM)}" + " " * (80 - len(body_b)) + c("│", Colors.CYAN))

        output.append(c("│", Colors.CYAN) + " " * 98 + c("│", Colors.CYAN))

        # Result
        bodies_match = body_a == body_b
        result = c("✓ PASS - Bodies match", Colors.GREEN + Colors.BOLD) if bodies_match else c("✗ FAIL - Bodies differ", Colors.RED + Colors.BOLD)
        output.append(c("│", Colors.CYAN) + f" Result: {result}" + " " * 67 + c("│", Colors.CYAN))

        output.append(c(f"└{'─' * 98}┘", Colors.CYAN))
        output.append("")

    # Final summary
    output.append(c("=" * 100, Colors.CYAN))
    output.append(c(" FINAL SUMMARY", Colors.BOLD + Colors.CYAN))
    output.append(c("=" * 100, Colors.CYAN))
    output.append("")

    passed = sum(1 for sol in solutions if parse_response(sol['response_A']).get('body', '') == parse_response(sol['response_B']).get('body', ''))
    failed = len(solutions) - passed

    output.append(f"   Total test cases:  {c(str(len(solutions)), Colors.BOLD)}")
    output.append(f"   Passed:            {c(str(passed), Colors.GREEN + Colors.BOLD)}")
    output.append(f"   Failed:            {c(str(failed), Colors.RED + Colors.BOLD if failed > 0 else Colors.GREEN)}")
    output.append("")
    output.append(f"   RFC 7230 Compliance: {c('VERIFIED' if failed == 0 else 'ISSUES FOUND', Colors.GREEN + Colors.BOLD if failed == 0 else Colors.RED + Colors.BOLD)}")
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
