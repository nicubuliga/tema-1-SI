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


def get_mode_and_send():
    mode = str(input("Modul ECB/OFB: "))

    socket.send_string("mode:" + mode)
    encrypted_key = socket.recv()

    return mode, decrypt_key(encrypted_key)

def wait_start():
    while True:
        socket.send_string("wait-start:")

        if socket.recv_string() == "start:":
            break

def pad(plaintext):
    new_text = plaintext

    while len(new_text) % 16:
        new_text += " "
    return new_text

def xor(x ,y):
    return bytes(a ^ b for (a, b) in zip(x, y))

def encrypt_text(plaintext, mode, key):
    ciphertext = b""
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = pad(plaintext)
    blocks = [plaintext[i:i+16]for i in range(0, len(plaintext), 16)]
    
    if mode == "ECB":
        for block in blocks:
            ciphertext += cipher.encrypt(block.encode())
    elif mode == "OFB":
        for block in blocks:
            encrypted_iv = cipher.encrypt(iv)
            ciphertext += xor(encrypt_text, block)
            global iv
            iv = iv[len(iv)//2:-1] + encrypted_iv[0:len(encrypted_iv)//2]
    print(ciphertext)
    return ciphertext


def send_message(mode, key):
    with open("message.txt", "r") as fd:
        plaintext = fd.read()
    
    socket.send_string("msg:" + str(encrypt_text(plaintext, mode, key)))
    socket.recv_string()


mode, key = get_mode_and_send()
wait_start()
send_message(mode, key)
