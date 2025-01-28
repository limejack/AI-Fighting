import pygame

class Animation():
    def __init__(self,images,rate,size=(0,0)):
        if type(images[0]) == str:
            self.images = self.get_images(images,size)
        else:
            self.images = images
        self.counter = 0
        self.rate = rate

    def get_images(self,images,size):
        out = []
        for i in images:
            picture = pygame.image.load(i)
            picture = pygame.transform.scale(picture, size)
            out.append(picture)
        return out

    def tick(self):
        self.counter += 1
        self.counter = self.counter

    def draw(self,screen,pos):
        if type(self.rate) == list:
            place = self.counter%sum(self.rate)
            for i in range(len(self.rate)):
                place -= self.rate[i]
                if place < 0:
                    temp = i
                    break
            img = self.images[temp]
        elif type(self.rate) == int:
            img = self.images[(self.counter//self.rate)%len(self.images)]


        rect = img.get_rect()
        self.tick()

        rect = rect.move(pos)
        screen.blit(img,rect)


if __name__ == '__main__':
    import pygame,sys
    from pygame.locals import *

    WHITE = (255,255,255)

    screen = pygame.display.set_mode((500,500))

    animation = Animation(['../TestAnimation/Pac-man1.png','../TestAnimation/Pac-man2.png','../TestAnimation/Pac-man3.png'],[120,240,5000],(100,50))

    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        animation.draw(screen,(100,100))
        pygame.display.update()

