from Cryptodome.Random import get_random_bytes
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Cipher import AES
from base64 import b64encode, b64decode
import pygame as pg
import file_encryp as fc
import os, sys, hashlib, easygui

clock, pwbox, selfile, screen, COLOR_INACTIVE, COLOR_ACTIVE, FONT, FONT2, FONT3, button = 0,0,0,0,0,0,0,0,0,0
salt = b'\xcf\xa3\\[\x9b\x05\xa6\x070\x1cq\xa7r\xd1:\x19\xf7\xc1\x8d$\xb0\x80\xce\xdd\xf8\x9d\xb4\xa5-\x16\x03\xe1'

"""
TODO

"""

class InputBox:
    def __init__(self, pos, font, text='', name='',win=0):
        self.rect = pg.Rect(pos, (200,font.get_height()+8))
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
                self.active = True
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
                    return self.text
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
        self.cursor = False

    def handle(self,event):
             
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.cursor = True
            if event.type == pg.MOUSEBUTTONDOWN:
                self.on = True
                return True
            else:
                    self.on = False
        else:
            self.cursor = False
    
    def draw(self):
        self.win.blit(self.img,self.pos)
        
class FileSel(Button):
    def __init__(self, win, pos, img):
        self.win = win
        self.pos = pos
        self.img = pg.image.load(resource_path(img))
        self.rect = pg.Rect(pos,self.img.get_size())
        self.file = ''
        self.cursor = False
     
    def handle(self, event):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.cursor = True
            if event.type == pg.MOUSEBUTTONDOWN:
                file = easygui.fileopenbox()
                if file:
                    self.file = file
        else:
            self.cursor = False
            
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

def enter(event):
    if event.type == pg.KEYDOWN and (event.key == pg.K_RETURN or event.key == 1073741912):
        return True
    return False

def set_icon(resource):
    img = pg.image.load(resource_path(resource))
    pg.display.set_icon(img)

def pstr(string,mlen=35):
    if len(string) > mlen:
        return string[:mlen//2] + ' ... ' + string[-mlen//2:]
    return string

def setup():
    global clock, pwbox, selfile, screen, COLOR_INACTIVE, COLOR_ACTIVE, FONT, FONT2, FONT3, button
    pg.init()
    screen = pg.display.set_mode((340, 75))
    pg.display.set_caption('FileEncrypt')
    set_icon(r'icon.png')
    COLOR_INACTIVE = pg.Color('purple4')
    COLOR_ACTIVE = pg.Color('purple1')
    FONT = pg.font.Font(None, 32)
    FONT2 = pg.font.Font(None, 20)
    FONT3 = pg.font.Font(None, 70)
    clock = pg.time.Clock()
    selfile = FileSel(screen,(0,0),r'explorer.png')
    pwbox = InputBox((70,13), FONT, name='Password',win=screen)
    button = Button(screen, (275,0), r'startbutton.png')
    
    selfile.draw()
    button.draw()

def main():
    txt = FONT2.render('Select file', True, pg.Color('darkgreen'))
    done = False
    wrong_data = False
    while not done:
        error = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            clear_screen(screen)
            
            button.handle(event)
            selfile.handle(event)

            if selfile.file:
                pw = pwbox.handle(event)
                size = os.path.getsize(selfile.file)

                if size > 10**8:
                    if size > 10**9:
                        filecolor = 'darkred'
                        size = str(size//10**7/100) + ' gb'
                    else:
                        filecolor = 'yellow3'
                        size = str(size//10**6) + ' mb'
                elif size > 10**5:
                    filecolor = 'darkgreen'
                    size = str(size//10**4/100) + ' mb'
                else:
                    filecolor = 'darkgreen'
                    size = str(size//10/100) + ' kb'

                filename = FONT2.render(pstr(selfile.file), True, pg.Color('purple3'))
                filesize = FONT2.render(size, True, pg.Color(filecolor))

                if selfile.file[-3:] == '.lk':
                    txt = FONT2.render(f'Enter Password for:', True, pg.Color('darkgreen'))
                    if pwbox.text and (enter(event) or button.on):
                        txt = FONT3.render('Decrypting', True, pg.Color('Yellow3'))
                        screen.blit(txt, (35,7))
                        pg.display.flip()
                        success = fc.decrypt_file(selfile.file,pwbox.text)
                        selfile.file = ''
                        if not success:
                            clear_screen(screen)
                            txt = FONT2.render('Error decrypting', True, pg.Color('darkred'))
                            pwbox.color = pg.Color('darkred')
                            error = True

                else:
                    txt = FONT2.render(f'Set Password to encrypt:', True, pg.Color('darkgreen'))
                    if pwbox.text and (enter(event) or button.on):
                        txt = FONT3.render('Encrypting', True, pg.Color('Yellow3'))
                        screen.blit(txt, (35,7))
                        pg.display.flip()
                        fc.encrypt_file(selfile.file,pwbox.text)
                        selfile.file = ''
            else:
                txt = FONT2.render('Select file', True, pg.Color('darkgreen'))
                filename = FONT2.render('', True, pg.Color('darkgreen'))
                filesize = FONT2.render('', True, pg.Color('darkgreen'))

            if selfile.cursor or button.cursor:
                pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_HAND)
            else:
                pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW) 

            screen.blit(txt, (70,47))
            screen.blit(filename, (70,60))
            screen.blit(filesize, (5,60))
            pwbox.draw(screen)
            button.draw()
            selfile.draw()

            if error:
                pg.display.flip()
                pg.time.delay(1000)
            
        pg.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    setup()
    main()
    pg.quit()