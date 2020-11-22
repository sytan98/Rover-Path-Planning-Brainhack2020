import cv2
import os
import time

from drone.Tello_api import Tello

tello = Tello()

tello.startvideo()
tello.startstates() # to read height of tello
tello.get_height()

while tello.frame is None: # this is for video warm up. when frame is received, this loop is exited.
	pass

while True:
	cv2.namedWindow('Tello video', cv2.WINDOW_NORMAL)
	cv2.imshow('Tello video', tello.frame)

	k = cv2.waitKey(16) & 0xFF
	if k == 27: # press esc to stop
		tello.exit()
		break

cv2.destroyAllWindows()