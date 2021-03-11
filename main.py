from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
import os, sys
from Cryptodome.Random import get_random_bytes
import pygame as pg
import easygui

clock, pwbox, selfile, screen, COLOR_INACTIVE, COLOR_ACTIVE, FONT, FONT2, button = 0,0,0,0,0,0,0,0,0

class InputBox:
    def __init__(self, pos, font, text='', name='',win=0):
        self.rect = pg.Rect(pos, (200,font.get_height()+13))
        self.color = COLOR_INACTIVE
        self.name = name
        self.text = name
        self.txt_surface = FONT.render(name, True, self.color)
        self.active = False
        self.win = win

    def press_return(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == 1073741912:
                return True
        return False

    def reset(self):
        self.color = COLOR_INACTIVE
        self.text = ''
        self.txt_surface = FONT.render(self.name, True, self.color)

    def handle(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                self.color = COLOR_ACTIVE
                if self.text == self.name:
                    self.text = '' + event.unicode
                elif event.key == pg.K_BACKSPACE:
                    if self.text == '':
                        return
                    self.text = self.text[:-1]
                    if self.text == '':
                        self.reset()
                elif self.press_return(event):
                    txt = self.text
                    self.text = self.name
                    return txt
                else:
                    self.text += event.unicode

            self.txt_surface = FONT.render(self.text, True, self.color)
        self.update()
            
    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.color, self.rect, 2)

class Button:
    def __init__(self, win, pos, img):
        self.win = win
        self.pos = pos
        self.img = pg.image.load(resource_path(img))
        self.rect = pg.Rect(pos,self.img.get_size())
        self.on = False
        self.text = ''

    def handle(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.on = True
                return True
        else:
            self.on = False
    
    def draw(self):
        self.win.blit(self.img,self.pos)
        
class FileSel(Button):
    def __init__(self, win, pos, img):
        self.win = win
        self.pos = pos
        self.img = pg.image.load(resource_path(img))
        self.rect = pg.Rect(pos,self.img.get_size())
        self.file = ''
     
    def handle(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.file = easygui.fileopenbox()
    
    def draw(self):
        self.win.blit(self.img,self.pos)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clear_screen(screen, color = pg.Color('grey10')):
    size = screen.get_size()
    rect = pg.Rect((0,0),size)
    pg.draw.rect(screen, color, rect)

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
    
    os.remove(filedest)

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

def enter(event):
    if event.type == pg.KEYDOWN and (event.key == pg.K_RETURN or event.key == 1073741912):
        return True
    return False

def set_icon(resource):
    img = pg.image.load(resource_path(resource))
    pg.display.set_icon(img)

def setup():
    global clock, pwbox, selfile, screen, COLOR_INACTIVE, COLOR_ACTIVE, FONT, FONT2, button
    pg.init()
    screen = pg.display.set_mode((340, 70))
    pg.display.set_caption('FileEncrypt')
    set_icon(r'icon.png')
    COLOR_INACTIVE = pg.Color('purple4')
    COLOR_ACTIVE = pg.Color('purple1')
    FONT = pg.font.Font(None, 32)
    FONT2 = pg.font.Font(None, 20)
    clock = pg.time.Clock()
    selfile = FileSel(screen,(0,0),r'explorer.png')
    pwbox = InputBox((70,13), FONT, name='password',win=screen)
    button = Button(screen, (275,0), r'startbutton.png')
    
    selfile.draw()
    button.draw()

def main():
    txt = FONT2.render('Select file', True, pg.Color('darkgreen'))
    done = False
    wrong_data = False
    pw = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            clear_screen(screen)
            selfile.handle(event)
            pw = pwbox.handle(event)
            button.handle(event)
            
            if selfile.file:
                if selfile.file[-4:] == '.txt':
                    txt = FONT2.render('Set Password', True, pg.Color('darkgreen'))
                    if pwbox.text and (enter(event) or button.on):
                        encrypt_file(selfile.file,pwbox.text)
                        selfile.file = ''

                elif selfile.file[-3:] == '.lc':
                    txt = FONT2.render('Enter Password', True, pg.Color('darkgreen'))
                    if pwbox.text and (enter(event) or button.on):
                        try:
                            enc_dict = gen_dict(selfile.file)
                            if not enc_dict:
                                txt = FONT2.render('File corrupted', True, pg.Color('darkred'))
                            else:
                                decrypted = decrypt(enc_dict,pwbox.text)
                        except ValueError:
                            pwbox.color = pg.Color('darkred')
                        else:
                            with open(selfile.file[:-3]+'.txt','w') as file:
                                file.write(decrypted.decode('utf8'))
                                file.close()
                            os.remove(selfile.file)
                            selfile.file = ''

                else:
                    txt = FONT2.render('.txt or .lc accepted', True, pg.Color('darkred'))
                
            else:
                txt = FONT2.render('Select file', True, pg.Color('darkgreen'))

            if pw:
                pwbox.reset()

            screen.blit(txt, (70,50))
            pwbox.draw(screen)
            button.draw()
            selfile.draw()

        pg.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    setup()
    main()
    pg.quit()