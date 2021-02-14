# sprites for events
import pygame
from pygame.locals import *
import common.constants as constants

class Animation(pygame.sprite.Sprite):
    global IS_SHOOTING
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((screen.get_width(), screen.get_height()))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (screen.get_width()/2, screen.get_height()/2)
        self.target = screen
        self.timer = 0
        self.color = 0
        self.up = True # up or down
    
    def update(self):
        self.image.fill((255,0,0))
        self.image.set_alpha(self.color)
        self.target.blit(self.image,(0,0))
        pygame.display.flip()
        
    def change(self):
        if self.timer == 15: # 15 frames for UP and 15 frames for DOWN
            self.timer = 0
            self.up = not self.up
        self.timer += 1
        if self.up:
            self.color += 30
        else:
            self.color -= 30
        #print(self.up, self.color)

    def show(self) :
        self.color = 128 # not full alpha
        self.update()

    def hide(self) :
        self.color = 0
        self.update()