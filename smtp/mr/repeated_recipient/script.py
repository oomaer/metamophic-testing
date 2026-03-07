from fandango.evolution import GeneratorWithReturn
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
    print("=" * 60)
    print("Metamorphic Test: Repeated Recipient Invariance")
    print("A: Single RCPT TO (one recipient)")
    print("B: Multiple RCPT TO with SAME address (repeated recipient)")
    print("Relation: Both should succeed with identical response codes")
    print("=" * 60)
    
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
            for line in captured_output.split('\n'):
                if '[VIOLATION]' in line:
                    solution_violations.append(line.strip())
            
            if solution_violations:
                violations[f"solution{solution_index + 1}"] = solution_violations
            
            print("-------------------------------------------------------------")
    finally:
        sys.stdout = old_stdout
        
    print("=" * 60)
    print(f"Total test cases generated: {len(solutions)}")
    if violations:
        print(f"Solutions with violations: {len(violations)}")
        print("Violations per solution:")
        for sol_key, sol_violations in violations.items():
            print(f"  {sol_key}:")
            for v in sol_violations:
                print(f"    - {v}")
    else:
        print("No violations detected for any of the test cases")
    print("=" * 60)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(script_dir, "grammar.fan")
    run_fandango(grammar_path)


if __name__ == "__main__":
    main()
