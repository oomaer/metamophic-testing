from fandango.evolution import GeneratorWithReturn
from fandango.evolution.algorithm import Fandango, LoggerLevel
from fandango.language.grammar import FuzzingMode
from fandango.language.parse.parse import parse
import os


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
    violations = []
    
    for solution in fandango.generate(mode=FuzzingMode.IO):
        solutions.append(solution)

    fandango = Fandango(
        grammar=grammar,
        constraints=constraints,
        logger_level=LoggerLevel.INFO,
    )
    global_variables, local_variables = fandango.grammar.get_spec_env()
    global_variables['do_ignore_response_constraints'] = False
    for solution in solutions:
        gen = GeneratorWithReturn(fandango.evaluator.evaluate_individual(solution))
        gen.collect()
        fitness, failing_trees, suggestions = gen.return_value
        if fitness < 1.0:
            print(f"[VIOLATION] Found a violation for solution: {failing_trees}")
 
        print("-------------------------------------------------------------")
        
    print("=" * 60)
    print(f"Total test cases generated: {len(solutions)}")
    print("=" * 60)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(script_dir, "grammar.fan")
    run_fandango(grammar_path)


if __name__ == "__main__":
    main()
