import zmq
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

k_prim = b"abcdefghqazwsxed"
iv = b"abababcdcdcdzzzz"
key = get_random_bytes(16)
started = False
got_msg = False
msg = ""

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def encrypt_key():
    cipher = AES.new(k_prim, AES.MODE_ECB)
    return cipher.encrypt(key)

key = encrypt_key()

while True:
    #  Wait for next request from client
    message = socket.recv_string()
    
    prot, arg = message.split(":", 1)

    if prot == "mode":
        socket.send(key)
        mode = arg
    elif prot == "get_key":
        socket.send(key)
    elif prot == "get_mode":
        socket.send_string(mode)
    elif prot == "wait-start":
        if started:
            socket.send_string("start:")
        else:
            socket.send_string("wait:")
    elif prot == "start":
        started = True
        socket.send_string("ok:")
    elif prot == "msg":
        got_msg = True
        msg = arg
        socket.send_string("ok:")
    elif prot == "wait-msg":
        if got_msg:
            print(msg)
            socket.send_string(msg)
        else:
            socket.send_string("wait:")

