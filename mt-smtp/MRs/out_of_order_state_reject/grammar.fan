include ("/Users/i7949486/Downloads/docker/metamorphic-testing/mt-smtp/smtp-utils.fan")

# Out-of-Order State Rejection Test (Negative MR - RFC 5321)
# Tests "Symmetry of Rejection" - server must reject RCPT TO when not in proper state
#
# A: Attempt RCPT TO before MAIL FROM (no prior transaction)
#    Expected: 503 Bad sequence of commands
#
# B: Complete valid transaction → RSET → Attempt RCPT TO
#    Expected: Same 503 error (server should be in same state as A)
#
# Relation: Both must receive identical rejection error codes

<start> ::= <Interation1> <ChangeConnection> <Interation2> 

# 1. Setup Phase: Connect and EHLO
<Interation1> ::= <ServerA:response_setup><ClientA:request_ehlo><ServerA:response_ehlo><state_logged_out_A>
<Interation2> ::= <ServerB:response_setup><ClientB:request_ehlo><ServerB:response_ehlo><state_logged_out_B>
<ChangeConnection> ::= r".*" := changeConnection()

# 2. Login Phase
<state_logged_out_A> ::= <exchange_login_valid_A>
<state_logged_out_B> ::= <exchange_login_valid_B>

# 3. Test Scenarios
# A: Directly attempt RCPT TO without MAIL FROM (out-of-order)
<state_logged_in_A> ::= <exchange_invalid_rcpt_A><exchange_quit_A>

# B: Complete valid transaction, reset, then attempt invalid RCPT TO
<state_logged_in_B> ::= <exchange_send_email_B><exchange_reset_B><exchange_invalid_rcpt_B><exchange_quit_B>

# --- Detailed Exchanges for A (Invalid Sequence - No Prior Transaction) ---

<exchange_login_valid_A> ::= <ClientA:request_auth><ServerA:response_auth_expect_user><ClientA:request_auth_user><ServerA:response_auth_expect_pass><ClientA:request_auth_pass><ServerA:response_auth_success><state_logged_in_A>

# Attempt RCPT TO without MAIL FROM - should get 503 error
<exchange_invalid_rcpt_A> ::= <ClientA:request_rcpt_to><ServerA:response_rcpt_error_A>

<exchange_quit_A> ::= <ClientA:request_quit><ServerA:response_quit>

# --- Detailed Exchanges for B (Invalid Sequence - After Valid Transaction) ---

<exchange_login_valid_B> ::= <ClientB:request_auth><ServerB:response_auth_expect_user><ClientB:request_auth_user><ServerB:response_auth_expect_pass><ClientB:request_auth_pass><ServerB:response_auth_success><state_logged_in_B>

# Complete a valid email transaction first
<exchange_send_email_B> ::= <ClientB:request_mail_from><ServerB:response_mail_from><ClientB:request_rcpt_to><ServerB:response_rcpt_to><ClientB:request_data><ServerB:response_data><ClientB:email_content><ServerB:response_email_sent>

# Reset to clear state (back to waiting for MAIL FROM)
<exchange_reset_B> ::= <ClientB:request_rset><ServerB:response_rset>

# Now attempt RCPT TO without MAIL FROM - should get same 503 error as A
<exchange_invalid_rcpt_B> ::= <ClientB:request_rcpt_to><ServerB:response_rcpt_error_B>

<exchange_quit_B> ::= <ClientB:request_quit><ServerB:response_quit>

# --- Static Definitions ---

<request_ehlo> ::= 'EHLO localhost\r\n'
<response_ehlo> ::= r"250-.+\r\n(250-.+\r\n)*250 .+\r\n"
<response_setup> ::= r"220 .+\r\n"

<request_auth> ::= 'AUTH LOGIN\r\n'
<response_auth_expect_user> ::= r"334 [A-Za-z0-9+/=]+\r\n"
<request_auth_user> ::= 'dGhlX3VzZXI=\r\n'
<response_auth_expect_pass> ::= r"334 [A-Za-z0-9+/=]+\r\n"
<request_auth_pass> ::= 'dGhlX3Bhc3N3b3Jk\r\n'
<response_auth_success> ::= r"235 .+\r\n"

# Email sending commands
<request_mail_from> ::= 'MAIL FROM:<sender@example.com>\r\n'
<response_mail_from> ::= r"250 .+\r\n"

<request_rcpt_to> ::= 'RCPT TO:<recipient@example.com>\r\n'
<response_rcpt_to> ::= r"250 .+\r\n"

# Error responses for out-of-order RCPT TO (expect 503)
<response_rcpt_error_A> ::= r"5[0-9]{2} .+\r\n"
<response_rcpt_error_B> ::= r"5[0-9]{2} .+\r\n"

<request_data> ::= 'DATA\r\n'
<response_data> ::= r"354 .+\r\n"

<email_content> ::= 'Subject: Test Email\r\n\r\nThis is a test email.\r\n.\r\n'
<response_email_sent> ::= r"250 .+\r\n"

# RSET command
<request_rset> ::= 'RSET\r\n'
<response_rset> ::= r"250 .+\r\n"

<request_quit> ::= 'QUIT\r\n'
<response_quit> ::= r"221 .+\r\n"


where validateRejectionSymmetry(<response_rcpt_error_A>, <response_rcpt_error_B>)


def validateRejectionSymmetry(responseA, responseB):
    # Both should return the same error code (503 Bad sequence)
    codeA = str(responseA)[:3]
    codeB = str(responseB)[:3]
    if codeA == codeB:
        print(f"✓ Symmetry of Rejection: Both returned {codeA}")
        return True
    else:
        print(f"✗ Rejection asymmetry: A={codeA}, B={codeB}")
        return False
