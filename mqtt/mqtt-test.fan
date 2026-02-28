include("mqtt-utils.fan")
# --- 1. Pure Data Terminals ---
<CONNECT_DATA>   ::= "\x10" <remaining_length> <protocol_name> <connect_flags> <keep_alive> <client_id>
<CONNACK_DATA>   ::= "\x20\x02\x00\x00" 
<SUBSCRIBE_DATA> ::= "\x82" <remaining_length_sub> <packet_id> <topic_filter> <requested_qos>
<SUBACK_DATA>    ::= "\x90\x03" <packet_id> "\x00" 
<PINGREQ_DATA>   ::= "\xc0\x00"
<PINGRESP_DATA>  ::= "\xd0\x00"
<PUBLISH_DATA>   ::= "\x30" <remaining_length_pub> <topic_name> <payload>

# --- 2. High-Level Interaction Logic ---
<start> ::= <mqtt_session>

<mqtt_session> ::= <connect_handshake><interaction_body>

<connect_handshake> ::= <Client:Broker:CONNECT_DATA> <Broker:Client:CONNACK_DATA>

# Sending a Ping ensures the connection stays "warm" before the test
<heartbeat> ::= <Client:Broker:PINGREQ_DATA> <Broker:Client:PINGRESP_DATA>

<interaction_body> ::= <subscribe_redundant> <publish_sequence>

<subscribe_redundant> ::= <sub_exchange> <sub_exchange> 

<sub_exchange> ::= <Client:Broker:SUBSCRIBE_DATA> <Broker:Client:SUBACK_DATA>

<publish_sequence> ::= <Client:Broker:PUBLISH_DATA>

# --- 3. Shared Terminals ---
<keep_alive>    ::= "\x00\x3C" # 60 seconds - standard and stable
<remaining_length>     ::= "\x0C"
<remaining_length_sub> ::= "\x0D"
<remaining_length_pub> ::= "\x15"
<packet_id>            ::= "\x00\x01"
<topic_filter>         ::= "\x00\x09test/topic"
<topic_name>           ::= "\x00\x09test/topic"
<requested_qos>        ::= "\x00"
<payload>              ::= "Hello MQTT"
<protocol_name>        ::= "\x00\x04MQTT\x04"
<connect_flags>        ::= "\x02"
<client_id>            ::= "\x00\x08test_cli"



