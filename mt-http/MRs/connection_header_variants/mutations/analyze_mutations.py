#!/usr/bin/env python3
"""
Mutation Testing Results Analyzer for Connection Header Variants MR

Reads mutation log files and generates a comprehensive results report.
"""

import re
from pathlib import Path
from datetime import datetime

# ANSI colors
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

# Expected detection results for each mutation
EXPECTED_DETECTION = {
    'NONE': 'NO',   # Baseline should have no violations
    'M1': 'YES',    # Different status codes should be detected
    'M2': 'YES',    # Error status should be detected
    'M3': 'YES',    # 204 No Content should be detected
    'M8': 'YES',    # Empty body should be detected
    'M20': 'NO',    # Different transfer encoding is semantic (shouldn't affect body)
}

def get_script_dir():
    return Path(__file__).parent

def parse_log_file(log_file):
    """Parse a single mutation log file."""
    if not log_file.exists():
        return {
            'passes': 0,
            'violations': 0,
            'status': 'MISSING',
            'total_tests': 0
        }

    with open(log_file, 'r') as f:
        content = f.read()

    # Count passes and violations
    passes = content.count('[PASS]')
    violations = content.count('[VIOLATION]')

    # Check for timeout or error
    if '[TIMEOUT]' in content:
        status = 'TIMEOUT'
    elif '[ERROR]' in content:
        status = 'ERROR'
    else:
        status = 'OK'

    # Extract total test cases from summary
    total_tests = 0
    match = re.search(r'Total test cases generated: (\d+)', content)
    if match:
        total_tests = int(match.group(1))

    return {
        'passes': passes,
        'violations': violations,
        'status': status,
        'total_tests': total_tests
    }

def format_duration(seconds_str):
    """Parse duration string from log."""
    # This is a placeholder - logs already contain formatted duration
    return seconds_str

def generate_report(results, output_file):
    """Generate the mutation testing report."""
    lines = []
    lines.append("=" * 100)
    lines.append(f"MUTATION TESTING RESULTS - Connection Header Variants MR")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")

    # Summary table
    lines.append(f"{'ID':<6} {'Description':<45} {'Tests':<6} {'Pass':<6} {'Viol':<6} {'Status':<10} {'Detected':<10} {'Expected':<10}")
    lines.append("-" * 100)

    detected_count = 0
    total_mutations = 0

    for r in results:
        if r['id'] == 'NONE':
            continue
        total_mutations += 1
        if r['detected']:
            detected_count += 1

    for r in results:
        detected_str = 'YES' if r['detected'] else 'NO'
        lines.append(f"{r['id']:<6} {r['description'][:44]:<45} {r['total_tests']:<6} {r['passes']:<6} {r['violations']:<6} {r['status']:<10} {detected_str:<10} {r['expected']:<10}")

    lines.append("-" * 100)
    lines.append("")

    # Statistics
    expected_detected = sum(1 for r in results if r['id'] != 'NONE' and r['expected'] == 'YES')
    expected_undetected = sum(1 for r in results if r['id'] != 'NONE' and r['expected'] == 'NO')
    killed = sum(1 for r in results if r['id'] != 'NONE' and r['detected'] and r['expected'] == 'YES')

    lines.append("STATISTICS:")
    lines.append(f"  Total mutations tested: {total_mutations}")
    lines.append(f"  Mutations detected (killed): {detected_count}")
    lines.append(f"  Mutations survived: {total_mutations - detected_count}")
    lines.append(f"  Expected detectable: {expected_detected}")
    lines.append(f"  Expected undetectable: {expected_undetected}")
    lines.append("")

    if expected_detected > 0:
        mutation_score = killed / expected_detected * 100
        lines.append(f"  Mutation Score: {killed}/{expected_detected} = {mutation_score:.1f}%")
        lines.append(f"  (Only counting mutations expected to be detected)")
    else:
        lines.append(f"  Mutation Score: N/A (no detectable mutations)")
    lines.append("")

    # Detection analysis
    lines.append("DETECTION ANALYSIS:")
    lines.append("")

    # Correctly detected
    lines.append("  Correctly Detected (Expected YES, Got YES):")
    correctly_detected = [r for r in results if r['expected'] == 'YES' and r['detected']]
    if correctly_detected:
        for r in correctly_detected:
            lines.append(f"    ✓ {r['id']}: {r['description']}")
    else:
        lines.append("    (none)")
    lines.append("")

    # Missed (should have detected but didn't)
    lines.append("  Missed (Expected YES, Got NO):")
    missed = [r for r in results if r['expected'] == 'YES' and not r['detected']]
    if missed:
        for r in missed:
            lines.append(f"    ✗ {r['id']}: {r['description']}")
    else:
        lines.append("    (none)")
    lines.append("")

    # Correctly not detected
    lines.append("  Correctly Not Detected (Expected NO, Got NO):")
    correctly_not_detected = [r for r in results if r['expected'] == 'NO' and not r['detected'] and r['id'] != 'NONE']
    if correctly_not_detected:
        for r in correctly_not_detected:
            lines.append(f"    ✓ {r['id']}: {r['description']}")
    else:
        lines.append("    (none)")
    lines.append("")

    # False positives (expected NO but got YES)
    lines.append("  False Positives (Expected NO, Got YES):")
    false_positives = [r for r in results if r['expected'] == 'NO' and r['detected']]
    if false_positives:
        for r in false_positives:
            lines.append(f"    ⚠ {r['id']}: {r['description']}")
    else:
        lines.append("    (none)")
    lines.append("")

    lines.append("=" * 100)

    # Save report
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    return killed, expected_detected, mutation_score if expected_detected > 0 else 0

def main():
    script_dir = get_script_dir()
    logs_dir = script_dir / 'logs'

    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 80)
    print(" MUTATION TESTING RESULTS ANALYZER")
    print("=" * 80)
    print(f"{Colors.RESET}")

    if not logs_dir.exists():
        print(f"{Colors.RED}Error: logs/ directory not found. Run 'python run_mutations.py' first.{Colors.RESET}")
        return

    # Define mutations (must match run_mutations.py)
    MUTATIONS = [
        ('NONE', 'Baseline (no mutation)'),
        ('M1', 'Different status for close (201 vs 200)'),
        ('M2', 'Error on close (500)'),
        ('M3', 'Return 204 No Content'),
        ('M8', 'Empty body'),
        ('M20', 'Different transfer encoding'),
    ]

    results = []

    print("Reading log files...")
    for mutation_id, description in MUTATIONS:
        log_file = logs_dir / f'log_{mutation_id}.txt'

        if not log_file.exists():
            print(f"{Colors.YELLOW}  Warning: logs/{log_file.name} not found{Colors.RESET}")
            continue

        parsed = parse_log_file(log_file)

        # Determine if mutation was detected
        detected = parsed['violations'] > 0 or parsed['status'] == 'TIMEOUT'

        expected = EXPECTED_DETECTION.get(mutation_id, 'UNKNOWN')

        results.append({
            'id': mutation_id,
            'description': description,
            'passes': parsed['passes'],
            'violations': parsed['violations'],
            'status': parsed['status'],
            'total_tests': parsed['total_tests'],
            'detected': detected,
            'expected': expected
        })

        # Print status
        status_color = Colors.GREEN if parsed['status'] == 'OK' else Colors.YELLOW
        detected_color = Colors.GREEN if detected else Colors.RED
        print(f"  {mutation_id}: {status_color}{parsed['status']}{Colors.RESET}, "
              f"Detected: {detected_color}{detected}{Colors.RESET}")

    print()

    if not results:
        print(f"{Colors.RED}No log files found in logs/. Run 'python run_mutations.py' first.{Colors.RESET}")
        return

    # Generate report
    output_file = script_dir / 'mutation_results.txt'
    killed, expected, score = generate_report(results, output_file)

    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    print(f"{Colors.RESET}")

    if expected > 0:
        score_color = Colors.GREEN if score >= 80 else Colors.YELLOW if score >= 60 else Colors.RED
        print(f"  Mutation Score: {score_color}{score:.1f}%{Colors.RESET} ({killed}/{expected} detected)")
    else:
        print(f"  Mutation Score: N/A")

    print(f"  Total mutations: {len(results) - 1}")  # Exclude baseline
    print()
    print(f"{Colors.GREEN}Results saved to: {output_file}{Colors.RESET}")
    print()

if __name__ == '__main__':
    main()
