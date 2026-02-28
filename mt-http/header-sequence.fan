
include ("http-grammer-utils.fan")
    
   
<start> ::= <header_order1> "|" <header_order2>

<header_order1> ::= <header_comp><header_comp>
<header_order2> ::= <header_comp><header_comp>
<header_comp> ::= (<header> ",") | (<header> "," <header_comp>)

<header> ::=  "Host: localhost" | "User-Agent: Fandango/1.0" | "Accept: */*"
# <header> ::= "a" | "b" 


where str(<header_order1>) == get_mutation(<header_order2>)
where str(<header_order1>) != str(<header_order2>)
