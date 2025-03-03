import pygame,sys,glob,math
from pygame.locals import *

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
DIMS_MENU = (500,500)
DIMS_MAIN = (500,500)

PIXEL_COUNT = (200,200)
WIDTH = (DIMS_MENU[0]/PIXEL_COUNT[0],DIMS_MENU[1]/PIXEL_COUNT[1])

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
        if self.isInside(pygame.mouse.get_pos()):pygame.draw.rect(screen,(0,0,0),(*self.pos,DIMS_MENU[0],50),1)
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
    def scroll(self,y):
        pass

class DrawBackground():
    def __init__(self,file):
        self.imgs = []
        self.pos = [0,0]
        self.isClicked = None,None
        self.name = file.split('\\')[-1]
        for f in glob.glob(f"{file}/*.png"):
            img = pygame.image.load(f).convert_alpha()
            img = pygame.transform.scale(img, DIMS_MAIN)
            img = pygame.transform.flip(img, False, True)
            self.imgs.append(img)
        self.rects = self.load(self.name)
        self.scale = 0
        self.image = 0
        self.surface = pygame.Surface((500,500))
        self.clickPos = None,None
        self.eraseMode = False
    def draw(self,screen):

        self.surface.fill((0,0,0))
        self.surface.blit(self.imgs[self.image],(0,0))
        x,y = self.relativeToAbsolute(pygame.mouse.get_pos())

        for i in self.rects[self.image]:
            if self.eraseMode and self.isInside((x,y),i):
                pygame.draw.rect(self.surface,(255,0,0),i,int(WIDTH[0]/2))
            else:
                pygame.draw.rect(self.surface,(0,255,0),i,int(WIDTH[0]/2))

        if self.isClicked[0]:
            x = x//WIDTH[0]*WIDTH[0]+WIDTH[0]
            y = y//WIDTH[1]*WIDTH[1]+WIDTH[1]
            pygame.draw.rect(self.surface,(0,255,0),(*self.isClicked,x-self.isClicked[0],y-self.isClicked[1]),int(WIDTH[0]/2))

        if self.clickPos[0]:
            x,y = pygame.mouse.get_pos()
            self.pos[0] = x-self.clickPos[0]
            self.pos[1] = y-self.clickPos[1]

        temp = pygame.transform.scale(self.surface,self.scaleList(DIMS_MAIN))
        screen.blit(temp,self.pos)
    def isInside(self,point,rect):
        if point[0] > rect[0] and point[0] < rect[0]+rect[2] and point[1] > rect[1] and point[1] < rect[1]+rect[3]:return True
        return False

    def scaleThing(self,number):
        return number*math.e**self.scale
    def scaleList(self,lis):
        return [self.scaleThing(i) for i in lis]
    def toggleMode(self):
        self.eraseMode = not self.eraseMode
    def absoluteToRelative(self,point):
        x = self.scaleThing(point[0])+self.pos[0]
        y = self.scaleThing(point[1])+self.pos[1]
        return [x,y]
    def relativeToAbsolute(self,point):
        x = self.inverseScaleThing(point[0]-self.pos[0])
        y = self.inverseScaleThing(point[1]-self.pos[1])
        return [x,y]
    def inverseScaleThing(self,number):
        return number/math.e**self.scale
    def inverseScaleList(self,lis):
        return [self.inverseScaleThing(i) for i in lis]
    def click(self,button):
        if button == 3:
            self.clickPos = pygame.mouse.get_pos()
            self.clickPos = (self.clickPos[0]-self.pos[0],self.clickPos[1]-self.pos[1])
            return
        if self.eraseMode:
            toErase = -1
            x,y = self.relativeToAbsolute(pygame.mouse.get_pos())
            for i in range(len(self.rects[self.image])):
                if self.isInside((x,y),self.rects[self.image][i]):
                    toErase = i
            if toErase != -1:
                del self.rects[self.image][toErase]
            self.save(self.rects,self.name)
            return
        if self.isClicked[0]:
            x,y = self.relativeToAbsolute(pygame.mouse.get_pos())
            x = x//WIDTH[0]*WIDTH[0]+WIDTH[0]
            y = y//WIDTH[1]*WIDTH[1]+WIDTH[1]
            self.rects[self.image].append([*self.isClicked,x-self.isClicked[0],y-self.isClicked[1]])
            self.isClicked = None,None
            self.save(self.rects,self.name)
        else:
            self.isClicked = self.relativeToAbsolute(pygame.mouse.get_pos())
            self.isClicked[0] = (self.isClicked[0]//WIDTH[0])*WIDTH[0]
            self.isClicked[1] = (self.isClicked[1]//WIDTH[1])*WIDTH[1]
    def unclick(self,button):
        if button == 3:self.clickPos = None,None
    def scroll(self,y):
        m = pygame.mouse.get_pos()
        temp = self.inverseScaleList((m[0]-self.pos[0],m[1]-self.pos[1]))
        self.scale += y
        if self.scale > 3:
            self.scale = 3
        if self.scale < 0:
            self.scale = 0
        self.pos[0] = m[0]-self.scaleThing(temp[0])
        self.pos[1] = m[1]-self.scaleThing(temp[1])
    def tab(self):
        self.image += 1
        self.image = self.image%len(self.imgs)
    def utab(self):
        self.image -= 1
        self.image = self.image%len(self.imgs)
    def undo(self):
        if len(self.rects[self.image]) > 0:
            self.rects[self.image].pop()
        self.save(self.rects,self.name)
    def save(self,rects,animationName):
        with open('../Hitboxes/'+animationName+'.hb','w') as outfile:
            outfile.write(str(rects))
    def load(self,animationName):
        try:
            with open('../Hitboxes/'+animationName+'.hb') as infile:
                return eval(infile.read())
        except FileNotFoundError:
            return [[] for i in self.imgs]

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
                if event.button == 5 or event.button == 4:continue
                if currentLocation == 'Menu':
                    currentLocation,currentFile = menu.click()
                    drawing = DrawBackground(currentFile)
                else:
                    drawing.click(event.button)
            elif event.type == MOUSEWHEEL:
                if currentLocation == 'Menu':
                    menu.scroll(event.y)
                else:
                    drawing.scroll(event.y)
            elif event.type == KEYDOWN:
                if currentLocation != 'Menu':
                    if event.key == K_TAB and event.mod == 0:
                        drawing.tab()
                    if event.key == K_TAB and event.mod == 1:
                        drawing.utab()
                    if event.key == K_z and event.mod == 64:
                        drawing.undo()
                    if event.key == K_r:
                        drawing.toggleMode()
            elif event.type == MOUSEBUTTONUP:
                if currentLocation != 'Menu':
                    drawing.unclick(event.button)
        pygame.display.update()
