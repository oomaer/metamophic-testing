include("ftp-utils.fan")

# --- Multi-Party FTP Grammar: Dual Interactions ---
<start> ::= <setup_communication>

<setup_communication> ::= <session_interaction_one>

# --- Interaction One: ClientA to ServerA ---
<session_interaction_one> ::= <greeting_one> <auth_one> <metamorphic_rename_sequence>

<greeting_one> ::= <ServerA:ClientA:response_welcome_one>
<response_welcome_one> ::= "220 " r".*" "\r\n"

<auth_one> ::= <user_one> <pass_one>
<user_one> ::= <ClientA:ServerA:req_user_one> <ServerA:ClientA:res_user_ok>
<req_user_one> ::= "USER " <username_one> "\r\n"
<res_user_ok>  ::= "331 " <generic_text> "\r\n"

<pass_one> ::= <ClientA:ServerA:req_pass_one> <ServerA:ClientA:res_auth_ok>
<req_pass_one> ::= "PASS " <password_one> "\r\n"
<res_auth_ok>  ::= "230 " <generic_text> "\r\n"

# --- Metamorphic Relation: Redundant RNFR ---
# This defines: RNFR fileA -> RNFR fileB -> RNTO final
<metamorphic_rename_sequence> ::= <abandoned_rnfr> <valid_rename_pair>

<abandoned_rnfr> ::= <ClientA:ServerA:req_rnfr_a> <ServerA:ClientA:res_rn_pending>
<valid_rename_pair> ::= <ClientA:ServerA:req_rnfr_b> <ServerA:ClientA:res_rn_pending> <ClientA:ServerA:req_rnto> <ServerA:ClientA:res_rn_success>

# --- Command Terminals ---
<req_rnfr_a>     ::= "RNFR " <filename_a> "\r\n"
<req_rnfr_b>     ::= "RNFR " <filename_b> "\r\n"
<req_rnto>       ::= "RNTO " <filename_final> "\r\n"

# --- Response Terminals ---
<res_rn_pending> ::= "350 " <generic_text> "\r\n"
<res_rn_success> ::= "250 " <generic_text> "\r\n"

# --- Shared Terminals & Data ---
<username_one>   ::= "user"
<password_one>   ::= "12345"
<filename_a>     ::= "renamed_result.txt"
<filename_b>     ::= "renamed_result.txt"
<filename_final> ::= "renamed_result.txt"
<generic_text>   ::= r'[\x20-\x7E]+'