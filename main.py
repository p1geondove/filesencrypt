from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os
from Cryptodome.Random import get_random_bytes
import easygui

def encrypt(plain_text, password):
    salt = get_random_bytes(AES.block_size)
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    cipher_config = AES.new(private_key, AES.MODE_GCM)
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))

    return {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }

def decrypt(enc_dict, password):
    salt = b64decode(enc_dict['salt'])
    cipher_text = b64decode(enc_dict['cipher_text'])
    nonce = b64decode(enc_dict['nonce'])
    tag = b64decode(enc_dict['tag'])
    
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(cipher_text, tag)

    return decrypted

def gen_dict(filename):
    with open(filename,'r') as file:
        out, text = [],''

        for char in file.read():
            if char == '@' or char == '\n':
                out.append(text)
                text = ''
            else:
                text = text + char

        enc_dict = {}
        for x in range(0,len(out),2):
            enc_dict[out[x]] = out[x+1]
        
        return enc_dict

def encrypt_file(filename,key):
    with open(filename,'r') as file:
        ctext = ''

        for x in file.readlines():
            ctext = ctext + x

        cryp = encrypt(ctext,key)
        clist = []

        for x in cryp:
            clist.append(x+'@'+cryp[x]+'\n')
        
    with open('test.lc','w') as file:
        for x in clist:
            file.write(x)

def main():
    filedest = easygui.fileopenbox()

    if filedest[-4:] == '.txt':
        key = input('Set password: ')
        encrypt_file(filedest,key)

    elif filedest[-3:] == '.lc':
        enc_dict = gen_dict(filedest)

        on = True
        while on:
            key = input('Password: ')
            try:
                decrypted = decrypt(enc_dict,key)
            except ValueError:
                print('Wrong Key!\n')
            else:
                on = False
                print(bytes.decode(decrypted))
        
if __name__ == '__main__':
    main()