
from Cryptodome.Random import get_random_bytes
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Cipher import AES
from base64 import b64encode, b64decode
from time import perf_counter_ns as clockns
import hashlib, os, easygui

ext = '.lk'
buffer_size = 2**16
salt = b'\xcf\xa3\\[\x9b\x05\xa6\x070\x1cq\xa7r\xd1:\x19\xf7\xc1\x8d$\xb0\x80\xce\xdd\xf8\x9d\xb4\xa5-\x16\x03\xe1'

def encrypt_file(filedest, password):
    key = PBKDF2(password, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_CFB)
    hashval = file_hash(filedest)
    with open(filedest,'rb') as in_file:
        with open(filedest+ext,'wb') as out_file:
            out_file.write(cipher.iv)
            out_file.write(b64decode(hashval))
            buffer = in_file.read(buffer_size)
            while len(buffer) > 0:
                ctext = cipher.encrypt(buffer)
                out_file.write(ctext)
                buffer = in_file.read(buffer_size)
    os.remove(filedest)
    return file_hash(filedest+ext)

def decrypt_file(filedest, password):
    key = PBKDF2(password, salt, dkLen=32)
    with open(filedest,'rb') as in_file:
        with open(filedest+'.temp','wb') as out_file:
            iv = in_file.read(16)
            hashval = in_file.read(48)
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
            buffer = in_file.read(buffer_size)
            while len(buffer) > 0:
                ctext = cipher.decrypt(buffer)
                out_file.write(ctext)
                buffer = in_file.read(buffer_size)
    stored = b64encode(hashval).decode('utf8')
    generated = file_hash(filedest+'.temp')
    if stored == generated:
        os.rename(filedest+'.temp',filedest[:-len(ext)])
        os.remove(filedest)
        return file_hash(filedest[:-len(ext)])
    else:
        os.remove(filedest+'.temp')
        return False

def file_hash(file_path):
    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        fb = f.read(buffer_size)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(buffer_size)
    return file_hash.hexdigest()

if __name__ == '__main__':
    filedest = easygui.fileopenbox()
    if filedest[-3:] == '.lk':
        pw = input('Enter Password: ')
        success = decrypt_file(filedest,pw)
        if not success:
            print('Error decrypting')
        else:
            print(f'Eecrypted successfully')
    else:
        pw = input('Set Password: ')
        encrypt_file(filedest,pw)
        