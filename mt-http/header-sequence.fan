
import random

def get_mutation(order):
    hash_id = hash(order.get_root())
    headers = [h.strip() for h in order.split(',') if h.strip()]
    # Use the hash as a seed for deterministic permutation
    # Ensure the seed is positive and within a reasonable range
    seed = abs(hash_id) % (2**31 - 1)
    
    # Create a random number generator with the seed
    rng = random.Random(seed)
    
    # Create a copy and shuffle it deterministically
    permuted_headers = headers.copy()
    rng.shuffle(permuted_headers)
    
    # Return the permutation as a comma-separated string
    # return ','.join(permuted_headers)
    permuted_header = (",".join(permuted_headers) + ",")
    return permuted_header
   
    
    
   
<start> ::= <header_order1> "|" <header_order2>
# <header_order1> ::= <header_a><header_b><header_c>
# <header_order2> ::= <header_b><header_a><header_c>
# <header_a> ::= <header>","
# <header_b> ::= <header>","
<header_order1> ::= <header_comp><header_comp>+
<header_order2> ::= <header_comp><header_comp>+
<header_comp> ::= <header>","

<header> ::=  "Host: localhost" | "User-Agent: Fandango/1.0" | "Accept: */*"


where str(<header_order1>) == get_mutation(<header_order2>)
where str(<header_order1>) != str(<header_order2>)
