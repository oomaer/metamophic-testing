from fandango.evolution.algorithm import Fandango, LoggerLevel
from fandango.language.grammar import FuzzingMode
from fandango.language.parse.parse import parse
import os
import io
import sys


class TeeStream:
    """Stream that writes to both original stdout and captures output."""
    def __init__(self, original_stdout):
        self.original = original_stdout
        self.captured = io.StringIO()

    def write(self, data):
        self.original.write(data)
        self.captured.write(data)

    def flush(self):
        self.original.flush()

    def getvalue(self):
        return self.captured.getvalue()

    def reset(self):
        """Reset captured buffer and return previous content."""
        content = self.captured.getvalue()
        self.captured = io.StringIO()
        return content


def run_fandango(grammar_path):
    print(f"Running Fandango with grammar: {grammar_path}")
    print("=" * 70)
    print("Metamorphic Test: Connection Header Variants (RFC 7230)")
    print("A: HTTP request with 'Connection: keep-alive'")
    print("B: HTTP request with 'Connection: close'")
    print("Relation: Response body and status code must be identical")
    print("=" * 70)

    with open(grammar_path) as f:
        grammar, constraints = parse(f, use_stdlib=False)
    assert grammar is not None

    fandango = Fandango(
        grammar=grammar,
        constraints=constraints,
        logger_level=LoggerLevel.INFO,
    )

    solutions = []
    violations = {}  # {solution_index: [violations]}
    passes = 0

    # Capture stdout during generation to detect violation logs
    old_stdout = sys.stdout
    tee_stream = TeeStream(old_stdout)
    sys.stdout = tee_stream

    try:
        for solution in fandango.generate(mode=FuzzingMode.IO):
            solution_index = len(solutions)
            solutions.append(solution)

            # Extract violations for this solution from captured output
            captured_output = tee_stream.reset()
            solution_violations = []
            has_pass = False

            for line in captured_output.split('\n'):
                if '[VIOLATION]' in line:
                    solution_violations.append(line.strip())
                if '[PASS]' in line:
                    has_pass = True

            if solution_violations:
                violations[f"solution{solution_index + 1}"] = solution_violations
            if has_pass:
                passes += 1

            print("-" * 70)
    finally:
        sys.stdout = old_stdout

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total test cases generated: {len(solutions)}")
    print(f"Passed: {passes}")
    print(f"Violations: {len(violations)}")

    if violations:
        print("\nViolations per solution:")
        for sol_key, sol_violations in violations.items():
            print(f"  {sol_key}:")
            for v in sol_violations:
                print(f"    - {v}")
    else:
        print("\nAll solutions passed - Connection header invariance holds!")

    print("=" * 70)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(script_dir, "grammar.fan")
    run_fandango(grammar_path)


if __name__ == "__main__":
    main()
