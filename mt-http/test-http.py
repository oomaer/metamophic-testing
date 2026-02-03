# ======================
# Phase 1: Run Fadnango with spec header_list.fan -> Generates a list of header ["A", "B", "C"]
#          a, b, c
# Phase 2: gen_grammar.py -> Read list of header from pghase 1 and genrates grammar accordingly
#          <headers> :: = "a" <header_wo_a> | "b" <header_wo_b> | "c" <header_wo_c>
#         # <header_wo_a> :: = "b" <header_wo_ab> | "c" <header_wo_ac>
# Phase 3: Call fandango api with generated grammar 

# func gen
# find ::GEN_GRAMMER:: replaces mygengarmmer()

# call fandango api

# ======================
from fandango.evolution.algorithm import Fandango, LoggerLevel
from fandango.language.grammar import FuzzingMode
from fandango.language.parse.parse import parse


from itertools import permutations as permute
from itertools import combinations
import tempfile
import subprocess
import os

def generate_header_pairs_efficiently(headers):
    # This uses a generator to avoid loading everything into RAM
    # It yields pairs (seq1, seq2) where seq1 != seq2
    
    # Get all unique permutations
    unique_perms = permute(headers)
    
    # combinations(iterable, 2) gives us all possible pairs without duplicates
    # or comparing a sequence to itself.
    for seq1, seq2 in combinations(unique_perms, 2):
        yield [list(seq1), list(seq2)]

def main():
    headers = [
        "Host: localhost",
        "User-Agent: Fandango/1.0",
        "Accept: */*"
    ]
    # We use a generator to process one pair at a time
    for pair in generate_header_pairs_efficiently(headers):
        # Process pair (e.g., send to a fuzzer or printer)
        fandango_talk(pair)


def fandango_talk(header_pair):
    # run command fandango talk with header_pair
    print("Fandango talk with header pair:", header_pair)
    # read http-multipartygrammer.fan and replace ::header_order_1:: and ::header_order_2:: with header_pair[0] and header_pair[1]
    # call fandango api to run the grammar with the replaced headers

    with open("http-multipartygrammer.fan", "r") as f:
        grammar = f.read()

        
    header1_str = '"' + "\\r\\n".join(header_pair[0]) + "\\r\\n" + '"'
    header2_str = '"' + "\\r\\n".join(header_pair[1]) + "\\r\\n" + '"'
    
    grammar = grammar.replace("->header_order_1", header1_str)
    grammar = grammar.replace("->header_order_2", header2_str)
    # print("Generated Grammar:\n", grammar)
        # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fan', delete=False) as tmp_file:
        tmp_file.write(grammar)
        tmp_filename = tmp_file.name
    
    try:
        # Run fandango talk command with the temporary file
        result = subprocess.run(
            ['fandango', '-v', 'talk', '-f', tmp_filename, '-n', '1'],
            capture_output=True,
            text=True
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    finally:
        # Clean up the temporary file
        os.unlink(tmp_filename)

    


main()