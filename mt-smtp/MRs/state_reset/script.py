from fandango.evolution.algorithm import Fandango, LoggerLevel
from fandango.language.grammar import FuzzingMode
from fandango.language.parse.parse import parse
import os


def run_fandango(grammar_path):
    print(f"Running Fandango with grammar: {grammar_path}")
    with open(grammar_path) as f:
        grammar, constraints = parse(f, use_stdlib=False)
    assert grammar is not None
    fandango = Fandango(
        grammar=grammar,
        constraints=constraints,
        logger_level=LoggerLevel.INFO,
    )

    solutions = []
    for solution in fandango.generate(mode=FuzzingMode.IO):
        solutions.append(solution)
        print("-------------------------------------------------------------")

    print("total test cases generated:", len(solutions))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(script_dir, "grammar.fan")
    run_fandango(grammar_path)


if __name__ == "__main__":
    main()


# how to continue with next solution if one does not satisfy the contraints