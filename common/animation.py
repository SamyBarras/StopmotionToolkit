# sprites for events
import pygame
from pygame.locals import *

class Animation(pygame.sprite.Sprite):
    def __init__(self, res, col, _alpha, message=""):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(res)
        self.color = col
        self.default_alpha = _alpha
        self.timer = 0
        self.alpha = 0
        self.up = True # up or down
        # initiate fill color
        self.image.fill(self.color)
        if message is not None :
            self.m = pygame.font.SysFont(pygame.font.get_default_font(), 30).render(message, True, (255, 255, 255))
        else :
            self.m = None
    
    def update(self, trgt, cntr):
        trgt.fill(0)
        trgt.blit(self.image, cntr)
        if self.m is not None :
            trgt.blit(self.m, (trgt.get_width()/2-self.m.get_rect().w/2,trgt.get_height()/2-self.m.get_rect().h/2))
        #pygame.display.flip()
        
    def show(self, trgt, cntr) :
        self.image.set_alpha(self.default_alpha)
        self.update(trgt, cntr)

    def hide(self, trgt, cntr) :
        self.image.set_alpha(0) # set alpha to 0
        self.update(trgt, cntr)


    ########### unused for now
    def change(self):
        if self.timer == 15: # 15 frames for UP and 15 frames for DOWN
            self.timer = 0
            self.up = not self.up
        self.timer += 1
        if self.up:
            self.alpha += 30
        else:
            self.alpha -= 30
        self.update(trgt, cntr)