#!/usr/bin/python

import os
import pygame

drivers = ('directfb', 'fbcon', 'svgalib')

found = False
for driver in drivers:
	print "Trying \'" + driver + "\'",
	if not os.getenv('SDL_VIDEODRIVER'):
		os.putenv('SDL_VIDEODRIVER',driver)
	try:
		pygame.display.init()
	except pygame.error:
		print 'failed'
		continue
	found = True
	break
if not found:
	raise Exception('No suitable video driver found.')

print "success"
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)