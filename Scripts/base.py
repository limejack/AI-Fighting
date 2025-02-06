import pygame,sys
import numpy as np

from type_aliases import Rectangle
from animation import Animation
from animation import Body

SCALE = 1.5
DT = 0.1
G = 20
COLORS = {
    'bg':(140,190,170),
    'ground':(70,100,90),
    'player':(20,20,20),
    'blue':(50,50,150),
    'green':(50,150,50)
}


class Attack():
    def __init__(self,parent):
        self.parent = parent
        self.animation = Animation(["test"], rate=2, size=(150,150))
    def collide(self,other):
        pass
class NeutralAttack(Attack):
    def __init__(self,parent):
        super().__init__(parent)
        self.animation.update(animation='test', frame=0)
        self.bodies = self.animation.bodies['test']
        self.body = self.bodies[self.animation.current_frame]
        self.pos = self.parent.pos
        self.collided = set()

        self.cool_down = 50
    def update(self):
        self.animation.update()

        if self.animation.current_frame >= len(self.bodies):
            self.delete()
            return

        self.pos = self.parent.pos
        self.body = self.bodies[self.animation.current_frame]
        self.cool_down -= 1
    def delete(self):
        self.parent.attacks.remove(self)
        self.parent.parent.collidables.remove(self)
    def display(self):
        self.animation.display(self.parent.parent.surface, self.parent.pos, flip=(self.parent.facing==-1))
    def collides(self,other):
        if other == self.parent or other in self.collided or other == self: return False
        else:
            return self.body.collides(other.body,self.pos,other.pos)
    def collide(self,other):
        self.collided.add(other)
        if type(other) == Player:
            other.vel += np.array([500,50])
        
class Environment:
    def __init__(self):
        self.screen_size = (800, 400)
        # everything is drawn onto surface and scaled up onto the screen
        self.surface = pygame.Surface(self.screen_size, pygame.SRCALPHA) 
        self.screen = pygame.display.set_mode(np.multiply(self.screen_size, SCALE))
        self.clock = pygame.time.Clock()
        self.max_tick = 120 # supports cycles of 1,2,3,4,5,6,8,9,...
        self.tick = 0

        self.player = Player(self)
        self.player2 = Player(self)

        self.collidables = {self.player,self.player2}


        self.death_zone = (1000, -200)
        self.platforms = [
            Platform(self, (400,150), (300,20)),
            Platform(self, (550,250), (20,200)),
            Platform(self, (500,210), (20,20)),
            Platform(self, (300,220), (100,20)),
            Platform(self, (270,290), (40,20))
        ]

        self.reset()

    def reset(self):
        self.tick = 0
        self.player.reset()
        self.player2.reset()
        self.collidables = {self.player,self.player2}

    # take input and process frame
    def step(self, actions, display=False):
        self.tick += 1
        if self.tick == self.max_tick: self.tick = 0
        self.player.step(actions)
        self.player2.step([1,0,0,0])
        if abs(self.player.pos[0]) > self.death_zone[0] or self.player.pos[1] < self.death_zone[1]:
            self.reset()

        if display: self.display()
        
    def display(self):
        pygame.event.pump()
        self.surface.fill(COLORS['bg'])

        for platform in self.platforms:
            platform.display()

        self.player.display()
        self.player2.display()

        self.surface = pygame.transform.flip(self.surface, False, True)
        pygame.transform.scale(self.surface, (np.multiply(self.screen_size, SCALE)), self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    # //////////////////////////////////////GAME FUNCS//////////////////////////////////////

    def move(self, pos, upd, scale=1):
        return np.rint(np.add(pos, np.multiply(upd,scale)))

    def update_position(self, player):
        player.pos = self.move(player.pos, (0,player.vel[1]), scale=DT)
        update_vec = (0,[-1,1][player.vel[1] < 0])
        # move player pos down one pixel to check for ground
        move_up = False
        if player.vel[1] < 0:
            player.pos = self.move(player.pos, (0,-1))
            move_up = True # if no platforms touched, move the player pos back up a pixel
        for platform in self.platforms:
            while self.check_rectangle_collision(player.get_rect(), platform.get_rect()):
                move_up = False
                player.pos = self.move(player.pos, update_vec)
                player.vel = player.vel[0], 0
                if update_vec[1] > 0:
                    player.jump_flag = True
                    player.double_jump_flag = True
                    player.dash_flag = True
        if move_up: player.pos = self.move(player.pos, (0,1))

        player.pos = self.move(player.pos, (player.vel[0],0), scale=DT)
        update_vec = ([-1,1][player.vel[0] < 0],0)
        for platform in self.platforms:
            while self.check_rectangle_collision(player.get_rect(), platform.get_rect()):
                player.pos = self.move(player.pos, update_vec)
                player.vel = 0, player.vel[1]

        #collisions
        for i in self.collidables:
            for j in self.collidables:
                if i.collides(j) and j.collides(i): #Both sides have to agree that a collision occured
                    i.collide(j)
                    j.collide(i)

    def check_directions(self, rect): pass
    

    def check_point_rectangle_collision(self, pos, rect):
        x,y = position
        rect_x, rect_y, rect_w, rect_h = *rect.pos, *rect.dim

        return rect_x-rect_w/2 < x < rect_x-rect_w/2 and rect_y-rect_2/2 < y < rect_y+rect_h/2
        

    def check_rectangle_collision(self, rect1, rect2):
        x1, y1, w1, h1 = *rect1.pos, *rect1.dim
        x2, y2, w2, h2 = *rect2.pos, *rect2.dim
        left1, right1, top1, bottom1 = x1 - w1/2, x1 + w1/2, y1 - h1/2, y1 + h1/2
        left2, right2, top2, bottom2 = x2 - w2/2, x2 + w2/2, y2 - h2/2, y2 + h2/2

        return not (right1 < left2 or right2 < left1 or bottom1 < top2 or bottom2 < top1)


class Platform:
    # inputs: parent, center, (w,h)
    def __init__(self, parent, pos, dims):
        self.parent = parent
        self.pos = pos
        self.dims = dims

    def display(self):
        rect = pygame.Rect(self.pos[0]-self.dims[0]/2, self.pos[1]-self.dims[1]/2, *self.dims)
        pygame.draw.rect(self.parent.surface, COLORS['ground'], rect)

    def get_rect(self):
        return Rectangle(self.pos, self.dims)


class Player:
    def __init__(self, parent):
        self.parent = parent
        self.pos = 0, 0
        self.dims = 20, 30
        self.vel = 0, 0
        self.body = Body([[0,0, *self.dims]])
        self.attacks = []
        self.nonInteractables = {self}


        self.walk_speed = 15
        self.jump_power = 50
        self.friction = 0.6 # what x velocity is multiplied by each frame
        self.dash_speed = 125
        self.dash_time = 6 # num frames in dash
        self.dash_cooldown = 25 # num frames to wait after dash
    def collide(self,other):
        pass
    def collides(self,other):
        if self == other: return False
        return self.body.collides(other.body,self.pos,other.pos)
    def reset(self):
        self.pos = 400, 200
        self.vel = 0, 0
        
        self.facing = 1 # left:-1   right:1
        self.jump_flag = False # flag for if jump is available
        self.double_jump_flag = False # flag for if double jump is available
        self.jumping_flag = False # flag for whether jump button is being held to extend jump height
        self.dash_flag = False # flag for if dash is available
        self.dash_timer = 0 # how many frames left in dash
        self.dash_cooldown_timer = 0

        for i in self.attacks:
            i.delete()

    def step(self, actions):
        self.vel = (np.multiply(self.vel[0], self.friction),
                    self.vel[1])
        actions[0] -= 1
        self.vel = np.add(self.vel, (actions[0]*self.walk_speed, 0))

        if self.vel[1] < 0:
            self.jump_flag = False
            self.jumping_flag = False

        # if jump pressed and not dashing
        if actions[1] == 2 and self.dash_timer == 0:
            if self.jump_flag:
                self.jump_flag = False
                self.vel = (self.vel[0],self.jump_power)
            elif self.double_jump_flag:
                self.double_jump_flag = False
                self.vel = (self.vel[0],self.jump_power)
            self.jumping_flag = True
        elif actions[1] == 0:
            # if jump button let go, remove all vertical velocity for snappiness
            if self.jumping_flag:
                self.vel = (self.vel[0], 0)
            self.jumping_flag = False

        if actions[0] != 0 and not self.dash_timer:
            self.facing = actions[0]

        # handle dash input and dash cooldown
        # if jump pressed and can dash and isn't on cooldown
        if actions[2] == 1 and self.dash_flag and self.dash_cooldown_timer == 0:
            # if on the ground dash is reenabled
            if not self.jump_flag: self.dash_flag = False
            self.dash_timer = self.dash_time
            self.dash_cooldown_timer = self.dash_time + self.dash_cooldown

        if self.dash_timer:
            self.vel = (self.dash_speed*self.facing, 0.001)
            self.dash_timer -= 1

        if self.dash_cooldown_timer: self.dash_cooldown_timer -=1
            
        self.vel = np.add(self.vel, (0,-G*DT))
        # gravity has stronger effect when falling down
        if self.vel[1] < 0: self.vel = np.add(self.vel, (0,-G*DT*0.5))

        #Basically attack input
        if actions[3] == 1:
            canAttack = True
            for i in self.attacks:
                if type(i) == NeutralAttack and i.cool_down >= 0:
                    canAttack = False
                    print('a')
            if canAttack:
                self.attacks.append(NeutralAttack(self))
                self.parent.collidables.add(self.attacks[-1])
        for i in self.attacks:
            i.update()
            print(i.cool_down)


        self.actions = actions
        self.parent.update_position(self)
        
    def display(self):
        rect = pygame.Rect(self.pos[0]-self.dims[0]/2, self.pos[1]-self.dims[1]/2, *self.dims)
        pygame.draw.rect(self.parent.surface, COLORS['player'], rect)
        for i in self.attacks:
            i.display()

    def get_rect(self):
        return Rectangle(self.pos, self.dims)


z_hold = False
x_hold = False
c_hold = False
def get_user_actions():
    global z_hold, x_hold, c_hold
    # left:0   _:1   right:2
    # _:0   hold:1   jump:2
    # _:0   dash:1
    # _:0   attack:1
    actions = [1,0,0,0]
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        actions[0] += -1
    if keys[pygame.K_RIGHT]:
        actions[0] += 1
        
    if keys[pygame.K_z]:
        if not z_hold:
            actions[1] = 1
        z_hold = True
        actions[1] += 1
    else: z_hold = False

    if keys[pygame.K_x]:
        if not x_hold:
            actions[3] = 1
        x_hold = True
    else: x_hold = False

    if keys[pygame.K_c]:
        if not c_hold:
            actions[2] = 1
        c_hold = True
    else: c_hold = False

    return actions


        
if __name__ == '__main__':
    pygame.init()
    env = Environment()
    while True:
        actions = get_user_actions()
        _ = env.step(actions, display=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

