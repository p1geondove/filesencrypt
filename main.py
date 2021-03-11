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

def encrypt_file(filedest,key):
    with open(filedest,'r') as file:
        ctext = ''

        for x in file.readlines():
            ctext = ctext + x

        cryp = encrypt(ctext,key)
        clist = []

        for x in cryp:
            clist.append(cryp[x]+'\n')
        
    with open(filedest[:-4]+'.lc','w') as file:
        for x in clist:
            file.write(x)

def gen_dict(filedest):
    seq = ['cipher_text','salt','nonce','tag']
    with open(filedest,'r') as file:
        content =  file.readlines()
        enc_dict = {}
        try:
            for x in range(len(seq)):
                enc_dict[seq[x]] = content[x].translate({ord('\n'): None})
        except IndexError:
            print('File Corrupted!')
            return False
        
        return enc_dict

def main():
    print('Open a file to en/decrypt (.txt/.lc)')
    filedest = easygui.fileopenbox()

    if filedest[-4:] == '.txt':
        key = input('Set password: ')
        encrypt_file(filedest,key)

    elif filedest[-3:] == '.lc':
        enc_dict = gen_dict(filedest)
        if not enc_dict:
            return

        on = True
        while on:
            key = input('Enter password: ')
            try:
                decrypted = decrypt(enc_dict,key)
            except ValueError:
                print('Wrong password or file destroyed\n')
            else:
                on = False
                print(bytes.decode(decrypted))
        
if __name__ == '__main__':
    main()
    input('Press enter to close the window')