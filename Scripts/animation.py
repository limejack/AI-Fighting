import glob
import pygame
import numpy as np

class Animation():
    def __init__(self, folder_paths, rate, size=(100,100)):
        self.animations = {"N/A":[]}
        for folder_path in folder_paths:
            imgs = []
            for file in glob.glob(f"../Sprites/{folder_path}/*.png"):
                img = pygame.image.load(file).convert_alpha()
                img = pygame.transform.scale(img, size)
                img = pygame.transform.flip(img, False, True)
                imgs.append(img)
            self.animations[folder_path] = imgs
        
        self.rate = rate
        self.size = size

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

    def display(self, screen, pos, flip=False):
        if len(self.animations[self.current_animation]) <= self.current_frame:
            return
        img = self.animations[self.current_animation][self.current_frame]
        if flip: img = pygame.transform.flip(img, True, False)
        pos = np.subtract(pos, np.divide(self.size,2))
        screen.blit(img, pos)


