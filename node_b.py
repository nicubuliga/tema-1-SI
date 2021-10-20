import zmq
from Crypto.Cipher import AES

k_prim = b"abcdefghqazwsxed"
iv = b"abababcdcdcdzzzz"

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def decrypt_key(encrypted_key):
    cipher = AES.new(k_prim, AES.MODE_ECB)
    return cipher.decrypt(encrypted_key)

def request_mode_and_key():
    socket.send_string("get_mode:")
    mode = socket.recv_string()

    socket.send_string("get_key:")
    key = decrypt_key(socket.recv())

    return mode, key

def start_communication():
    socket.send_string("start:")
    socket.recv_string()

def wait_message():
    while True:
        socket.send_string("wait-msg:")

        resp = socket.recv_string()
        if resp != "wait:":
            return resp

def decrypt_text(ciphertext, mode, key):
    plaintext = b""
    cipher = AES.new(key, AES.MODE_ECB)
    blocks = [ciphertext[i:i+16]for i in range(0, len(ciphertext), 16)]
    
    if mode == "ECB":
        for block in blocks:
            plaintext += cipher.decrypt(block)
    
    return plaintext


mode, key = request_mode_and_key()
start_communication()
ciphertext = wait_message()
plaintext = decrypt_text(eval(ciphertext), mode, key)
print(plaintext.decode())