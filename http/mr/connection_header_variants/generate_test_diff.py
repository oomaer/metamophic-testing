#!/usr/bin/env python3
"""
Parse Fandango test output and generate a colored diff showing how test cases differ from each other.
Uses ANSI colors for terminal output.
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
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'


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
        # Detect request A
        if 'ClientA:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_A'] = match.group(1)

        # Detect response A
        elif 'ServerA: <response_A>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_A'] = match.group(1)

        # Detect request B
        elif 'ClientB:' in line and "'" in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['request_B'] = match.group(1)

        # Detect response B
        elif 'ServerB: <response_B>' in line:
            match = re.search(r"'(.+)'$", line)
            if match:
                current_solution['response_B'] = match.group(1)

        # Starting new protocol run means save current and reset
        elif 'Starting new protocol run' in line:
            if current_solution['request_A'] and current_solution['request_B']:
                solutions.append(current_solution.copy())
            current_solution = {
                'request_A': None,
                'response_A': None,
                'request_B': None,
                'response_B': None,
            }

    # Don't forget the last solution
    if current_solution['request_A'] and current_solution['request_B']:
        solutions.append(current_solution.copy())

    return solutions


def parse_request(raw_request):
    """Parse raw request string into components."""
    lines = raw_request.replace('\\r\\n', '\n').strip().split('\n')
    if not lines:
        return {}

    # Parse request line
    request_line = lines[0]
    parts = request_line.split(' ')
    method = parts[0] if len(parts) > 0 else ""
    path = parts[1] if len(parts) > 1 else ""
    version = parts[2] if len(parts) > 2 else ""

    # Parse headers
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
        'raw': raw_request
    }


def parse_response(raw_response):
    """Parse raw response string into components."""
    lines = raw_response.replace('\\r\\n', '\n').strip().split('\n')
    if not lines:
        return {}

    # Parse status line
    status_line = lines[0]
    match = re.match(r'HTTP/[\d.]+ (\d+) (.+)', status_line)
    status_code = match.group(1) if match else ""
    status_text = match.group(2) if match else ""

    # Find body (after empty line or in chunked format)
    body = ""
    json_match = re.search(r'\{[^}]+\}', raw_response)
    if json_match:
        body = json_match.group(0)

    return {
        'status_code': status_code,
        'status_text': status_text,
        'body': body,
        'raw': raw_response
    }


def colorize(text, color):
    """Wrap text with color codes."""
    return f"{color}{text}{Colors.RESET}"


def print_header(text):
    """Print a colored header."""
    print(colorize("=" * 80, Colors.CYAN))
    print(colorize(f" {text}", Colors.BOLD + Colors.CYAN))
    print(colorize("=" * 80, Colors.CYAN))


def print_subheader(text):
    """Print a colored subheader."""
    print(colorize("-" * 60, Colors.DIM))
    print(colorize(f" {text}", Colors.YELLOW))
    print(colorize("-" * 60, Colors.DIM))


def generate_test_case_comparison(solutions):
    """Generate comparison showing how test cases differ from each other."""

    print_header("TEST CASE VARIATION REPORT")
    print()
    print(f"Total test cases: {colorize(str(len(solutions)), Colors.GREEN + Colors.BOLD)}")
    print()

    # Extract unique values for each dimension
    methods = set()
    paths = set()
    user_agents = set()
    accepts = set()
    response_bodies = set()

    parsed_solutions = []
    for sol in solutions:
        req = parse_request(sol['request_A'])
        resp = parse_response(sol['response_A'])
        methods.add(req.get('method', ''))
        paths.add(req.get('path', ''))
        user_agents.add(req.get('headers', {}).get('User-Agent', ''))
        accepts.add(req.get('headers', {}).get('Accept', ''))
        response_bodies.add(resp.get('body', ''))
        parsed_solutions.append({'request': req, 'response': resp, 'raw': sol})

    # Print dimension summary
    print_subheader("TEST DIMENSIONS")
    print(f"  {colorize('Methods:', Colors.BOLD)}      {colorize(', '.join(sorted(methods)), Colors.GREEN)}")
    print(f"  {colorize('Paths:', Colors.BOLD)}        {colorize(', '.join(sorted(paths)), Colors.BLUE)}")
    print(f"  {colorize('User-Agents:', Colors.BOLD)}  {colorize(', '.join(sorted(user_agents)), Colors.MAGENTA)}")
    print(f"  {colorize('Accept:', Colors.BOLD)}       {colorize(', '.join(sorted(accepts)), Colors.YELLOW)}")
    print(f"  {colorize('Responses:', Colors.BOLD)}    {colorize(str(len(response_bodies)) + ' unique bodies', Colors.CYAN)}")
    print()

    # Create a matrix view of test cases
    print_subheader("TEST CASE MATRIX")
    print()

    # Group by path
    by_path = {}
    for i, ps in enumerate(parsed_solutions):
        path = ps['request'].get('path', '')
        if path not in by_path:
            by_path[path] = []
        by_path[path].append((i + 1, ps))

    for path, cases in sorted(by_path.items()):
        print(f"  {colorize('Path:', Colors.BOLD)} {colorize(path, Colors.BLUE + Colors.BOLD)}")
        print()

        # Sub-group by User-Agent
        by_ua = {}
        for idx, ps in cases:
            ua = ps['request'].get('headers', {}).get('User-Agent', '')
            if ua not in by_ua:
                by_ua[ua] = []
            by_ua[ua].append((idx, ps))

        for ua, ua_cases in sorted(by_ua.items()):
            ua_short = ua.split('/')[0] if '/' in ua else ua
            print(f"    {colorize('User-Agent:', Colors.DIM)} {colorize(ua_short, Colors.MAGENTA)}")

            for idx, ps in ua_cases:
                accept = ps['request'].get('headers', {}).get('Accept', '')
                status = ps['response'].get('status_code', '')
                body_preview = ps['response'].get('body', '')[:30]

                status_color = Colors.GREEN if status == '200' else Colors.RED
                print(f"      #{colorize(str(idx).zfill(2), Colors.CYAN)} "
                      f"Accept: {colorize(accept.ljust(20), Colors.YELLOW)} "
                      f"→ {colorize(status, status_color)} "
                      f"{colorize(body_preview, Colors.DIM)}...")
            print()
        print()

    # Show pairwise differences between consecutive test cases
    print_subheader("PAIRWISE DIFFERENCES (consecutive test cases)")
    print()

    for i in range(min(10, len(parsed_solutions) - 1)):  # Show first 10 pairs
        curr = parsed_solutions[i]
        next_sol = parsed_solutions[i + 1]

        curr_req = curr['request']
        next_req = next_sol['request']

        diffs = []

        # Compare each dimension
        if curr_req.get('path') != next_req.get('path'):
            diffs.append(f"Path: {colorize(curr_req.get('path', ''), Colors.RED)} → {colorize(next_req.get('path', ''), Colors.GREEN)}")

        curr_ua = curr_req.get('headers', {}).get('User-Agent', '')
        next_ua = next_req.get('headers', {}).get('User-Agent', '')
        if curr_ua != next_ua:
            curr_ua_short = curr_ua.split('/')[0] if '/' in curr_ua else curr_ua
            next_ua_short = next_ua.split('/')[0] if '/' in next_ua else next_ua
            diffs.append(f"User-Agent: {colorize(curr_ua_short, Colors.RED)} → {colorize(next_ua_short, Colors.GREEN)}")

        curr_accept = curr_req.get('headers', {}).get('Accept', '')
        next_accept = next_req.get('headers', {}).get('Accept', '')
        if curr_accept != next_accept:
            diffs.append(f"Accept: {colorize(curr_accept, Colors.RED)} → {colorize(next_accept, Colors.GREEN)}")

        if diffs:
            print(f"  {colorize(f'#{i+1}', Colors.CYAN)} → {colorize(f'#{i+2}', Colors.CYAN)}: ", end="")
            print(" | ".join(diffs))
        else:
            print(f"  {colorize(f'#{i+1}', Colors.CYAN)} → {colorize(f'#{i+2}', Colors.CYAN)}: {colorize('(identical request parameters)', Colors.DIM)}")

    if len(parsed_solutions) > 11:
        print(f"  {colorize(f'... and {len(parsed_solutions) - 11} more pairs', Colors.DIM)}")

    print()

    # Show unique test configurations
    print_subheader("UNIQUE TEST CONFIGURATIONS")
    print()

    seen_configs = set()
    unique_configs = []

    for i, ps in enumerate(parsed_solutions):
        config = (
            ps['request'].get('path', ''),
            ps['request'].get('headers', {}).get('User-Agent', ''),
            ps['request'].get('headers', {}).get('Accept', '')
        )
        if config not in seen_configs:
            seen_configs.add(config)
            unique_configs.append((i + 1, config, ps['response'].get('body', '')))

    print(f"  {colorize('Unique configurations:', Colors.BOLD)} {colorize(str(len(unique_configs)), Colors.GREEN + Colors.BOLD)} out of {len(parsed_solutions)} test cases")
    print()

    for idx, (num, config, body) in enumerate(unique_configs):
        path, ua, accept = config
        ua_short = ua.split('/')[0] if '/' in ua else ua
        body_preview = body[:40] if body else "(empty)"

        print(f"  {colorize(f'Config {idx + 1}', Colors.CYAN + Colors.BOLD)} (first seen in #{num}):")
        print(f"    {colorize('Path:', Colors.BLUE)}       {path}")
        print(f"    {colorize('User-Agent:', Colors.MAGENTA)} {ua_short}")
        print(f"    {colorize('Accept:', Colors.YELLOW)}     {accept}")
        print(f"    {colorize('Response:', Colors.GREEN)}   {body_preview}")
        print()


def main():
    script_dir = Path(__file__).parent
    log_file = script_dir / "test_output.log"

    if not log_file.exists():
        print(f"{Colors.RED}Error: {log_file} not found. Run the test first.{Colors.RESET}")
        sys.exit(1)

    solutions = parse_test_output(log_file)

    if not solutions:
        print(f"{Colors.RED}No solutions found in the log file.{Colors.RESET}")
        sys.exit(1)

    generate_test_case_comparison(solutions)

    # Also save to file (without colors)
    # Save colored version with ANSI codes for terminal viewing
    output_file = script_dir / "test_case_diff.txt"

    # Redirect stdout to capture output
    import io
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    generate_test_case_comparison(solutions)
    output = buffer.getvalue()
    sys.stdout = old_stdout

    with open(output_file, 'w') as f:
        f.write(output)

    print()
    print(colorize(f"Report saved to: {output_file}", Colors.DIM))


if __name__ == "__main__":
    main()
