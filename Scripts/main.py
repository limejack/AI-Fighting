import pygame,sys,glob
from pygame.locals import *

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
DIMS_MENU = (500,500)
DIMS_MAIN = (500,500)

class Button():
    def __init__(self):
        pass
    def draw(self,screen):
        pass
    def mouseOver(self):
        pass
    def click(self,pos):
        pass

class MenuOption(Button):
    def __init__(self,pos,text):
        self.pos = pos
        self.text = text
    def isInside(self,point):
        if point[0] > self.pos[0] and point[0] < self.pos[0]+DIMS_MENU[0] and point[1] > self.pos[1] and point[1] < self.pos[1]+50:return True
        return False
    def draw(self,screen):
        if self.isInside(pygame.mouse.get_pos()):        pygame.draw.rect(screen,(0,0,0),(*self.pos,DIMS_MENU[0],50),1)
        text_surface = my_font.render(self.text, False, (0, 0, 0,))
        screen.blit(text_surface,self.pos)
    
    def click(self,function):
        if self.isInside(pygame.mouse.get_pos()):
            return function(self)
class MenuManager():
    def __init__(self,function):
        self.function = function
        self.menu = []
        for file in glob.glob("../Sprites/*"):
            self.menu.append(MenuOption((0,50*len(self.menu)),file))
    def draw(self,screen):
        for i in self.menu:
            i.draw(screen)
    def click(self):
        out = []
        for i in self.menu:out.append(i.click(self.function))
        temp = [a for a in out if a]
        if len(temp) > 0:
            return temp[0]
        return 'Menu',None

class DrawBackground():
    def __init__(self,file):
        self.imgs = []
        self.isClicked = None,None
        self.rects = []
        for f in glob.glob(f"{file}/*.png"):
            img = pygame.image.load(f).convert_alpha()
            img = pygame.transform.scale(img, DIMS_MAIN)
            img = pygame.transform.flip(img, False, True)
            self.imgs.append(img)
    def draw(self,screen):
        screen.blit(self.imgs[0],(0,0))

        for i in self.rects: pygame.draw.rect(screen,(0,255,0),i,1)
        if self.isClicked[0]:
            x,y = pygame.mouse.get_pos()
            pygame.draw.rect(screen,(0,255,0),(*self.isClicked,x-self.isClicked[0],y-self.isClicked[1]),1)
    def click(self):
        if self.isClicked[0]:
            x,y = pygame.mouse.get_pos()
            self.rects.append([*self.isClicked,x-self.isClicked[0],y-self.isClicked[1]])
            self.isClicked = None,None
        else:
            self.isClicked = pygame.mouse.get_pos()

def menuButtonClicked(self):
    return 'Draw',self.text

if __name__  == '__main__':
    screen = pygame.display.set_mode(DIMS_MENU)
    screen.fill((255,255,255))
    menu = MenuManager(menuButtonClicked)
    drawing = None

    currentLocation = 'Menu'
    currentFile = None
    while True:
        screen.fill((125,255,255))
        if currentLocation == 'Menu':
            menu.draw(screen)
        else:
            drawing.draw(screen)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if currentLocation == 'Menu':
                    currentLocation,currentFile = menu.click()
                    drawing = DrawBackground(currentFile)
                else:
                    drawing.click()
        pygame.display.update()
