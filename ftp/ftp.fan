include("ftp-utils.fan")

#  Multi-Party FTP Grammar: Dual Interactions
<start> ::= <setup_communication>

<setup_communication> ::= <session_interaction_one>

# --- Interaction One: ClientA to ServerA ---
<session_interaction_one> ::= <greeting_one> <auth_one> 

<greeting_one> ::= <ServerA:ClientA:response_welcome_one>
<response_welcome_one> ::= "220 " r".*" "\r\n"

<auth_one> ::= <user_one> <pass_one>
<user_one> ::= <ClientA:ServerA:req_user_one> <ServerA:ClientA:res_user_ok>
<req_user_one> ::= "USER " <username_one> "\r\n"
<res_user_ok>  ::= "331 " <generic_text> "\r\n"

<pass_one> ::= <ClientA:ServerA:req_pass_one> <ServerA:ClientA:res_auth_ok>
<req_pass_one> ::= "PASS " <password_one> "\r\n"
<res_auth_ok>  ::= "230 " <generic_text> "\r\n"

# <upload_one> ::= <ClientA:ServerA:req_stor_one> <ServerA:ClientA:res_start> <ClientDataA:ServerDataA:data_one> <ServerA:ClientA:res_done>
# <req_stor_one> ::= "STOR file_interaction_one.txt\r\n"

# --- Interaction Two: ClientB to ServerB ---
<session_interaction_two> ::= <greeting_two> <auth_two>

<greeting_two> ::= <ServerB:ClientB:response_welcome_two>
<response_welcome_two> ::= "220 " <generic_text> "\r\n"

<auth_two> ::= <user_two> <pass_two>
<user_two> ::= <ClientB:ServerB:req_user_two> <ServerB:ClientB:res_user_ok>
<req_user_two> ::= "USER " <username_two> "\r\n"

<pass_two> ::= <ClientB:ServerB:req_pass_two> <ServerB:ClientB:res_auth_ok>
<req_pass_two> ::= "PASS " <password_two> "\r\n"

# <upload_two> ::= <ClientB:ServerB:req_stor_two> <ServerB:ClientB:res_start> <ClientDataB:ServerDataB:data_two> <ServerB:ClientB:res_done>
# <req_stor_two> ::= "STOR file_interaction_two.txt\r\n"

# --- Verification Phase ---
<verification_phase> ::= <ClientA:ServerA:req_list> <ServerA:ClientA:res_list_start> <ServerDataA:ClientDataA:list_payload> <ServerA:ClientA:res_done>

# --- Shared Terminals ---
<res_start> ::= "150 " <generic_text> "\r\n"
<res_done>  ::= "226 " <generic_text> "\r\n"
<req_list>  ::= "LIST\r\n"
<res_list_start> ::= "150 Opening data connection\r\n"

<username_one> ::= "user"
<password_one> ::= "12345"
<username_two> ::= "user2"
<password_two> ::= "password2"

<data_one>     ::= "Data from the first interaction\n"
<data_two>     ::= "Data from the second interaction\n"
<list_payload> ::= r'[\x20-\x7E\s]+'
<generic_text> ::= r'[\x20-\x7E]+'