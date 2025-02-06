import glob
import pygame
import numpy as np

class Body():
    def __init__(self,rects,flipped = False):
        self.rects = rects
        self.flipped = flipped
    def check_rectangle_collision(self, rect1, rect2, pos1, pos2):
        x1, y1, w1, h1 = *pos1, *rect1[2:]
        x2, y2, w2, h2 = *pos2, *rect2[2:]
        x1 += rect1[0]
        x2 += rect2[0]
        y1 += rect1[1]
        y2 += rect2[1]
        left1, right1, top1, bottom1 = x1 - w1/2, x1 + w1/2, y1 - h1/2, y1 + h1/2
        left2, right2, top2, bottom2 = x2 - w2/2, x2 + w2/2, y2 - h2/2, y2 + h2/2
        
        return not (right1 < left2 or right2 < left1 or bottom1 < top2 or bottom2 < top1)
    
    def collides(self,other,pos1,pos2):
        for i in self.getRects():
            for j in other.getRects():
                if self.check_rectangle_collision(i,j,pos1,pos2):
                    return True
        return False
    def getRects(self):
        if not self.flipped:
            return self.rects
        else:
            out = []
            for i in self.rects:
                out.append([-(i[0]+i[2]),-(i[1]+i[3]),i[2],i[3]])
        
class Animation():
    def __init__(self, folder_paths, rate, size=(100,100)):
        self.animations = {"N/A":[]}
        self.rects = {}
        self.bodies = {}

        self.rate = rate
        self.size = size

        for folder_path in folder_paths:
            imgs = []
            for file in glob.glob(f"../Sprites/{folder_path}/*.png"):
                img = pygame.image.load(file).convert_alpha()
                img = pygame.transform.scale(img, size)
                img = pygame.transform.flip(img, False, True)
                imgs.append(img)
            self.animations[folder_path] = imgs
            self.rects[folder_path] = eval(open('../Hitboxes/'+folder_path+'.hb').read())
            self.rects[folder_path] = [[[i[0]/500*self.size[0]-self.size[0]/2+i[2]/1000*self.size[0],i[1]/500*self.size[1]-self.size[1]/2+i[3]/1000*self.size[1],i[2]/500*self.size[0],i[3]/500*self.size[1]] for i in j] for j in self.rects[folder_path]]
            self.bodies[folder_path] = [Body(i) for i in self.rects[folder_path]]

        self.current_animation = 'N/A'
        self.current_frame = 0
        self.tick = 0

    def update(self, animation=None, frame=0):
        if animation:
            self.current_animation = animation
            self.current_frame = frame
            self.tick = 0
        else:
            if self.tick == self.rate:
                self.current_frame += 1
                self.tick = 0
            self.tick += 1

    
    def collision(self,pos,otherBody,otherBodyPos):
        return any(i.collides(otherBody,pos,otherBodyPos) for i in self.bodies[self.current_animation][self.current_frame])
    def display(self, screen, pos, flip=False):
        if len(self.animations[self.current_animation]) <= self.current_frame:
            return
        img = self.animations[self.current_animation][self.current_frame]
        if flip: img = pygame.transform.flip(img, True, False)

        
##        for i in self.rects[self.current_animation][self.current_frame]:
##            x,y,height,width = i
##            pygame.draw.rect(screen,(0,255,0),(pos[0]-i[2]/2+x,pos[1]-i[3]/2+y,i[2],i[3]))
##            pygame.draw.rect(screen,(0,255,0),(pos[0]-self.size[0]/2+x,pos[1]-self.size[1]/2+y,i[2],i[3]))

        pos = np.subtract(pos, np.divide(self.size,2))

        screen.blit(img, pos)


