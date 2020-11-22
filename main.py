from EP_api import Robot, findrobotIP
from robo.robo import Robo
from drone.drone import Drone
import cv2
import time
import math

img_folder = "./images/check"
#img_folder = "./Path_planning/images/test"

#Drone(autonomous=True, img_folder=img_folder, height_d=150, forward_dist=20, num_images=10).fly()
#NEED TO MAKE SURE YOU CLICK ON VIDEO FEED WINDOW WHEN PRESSING KEYS TO CONTROL

Robo = Robo(directory= img_folder, 
			choose_smoothing=False, 
			grid_size  = 40 ,
			robot_radius =100, 
			boundaries= [([0, 0, 150], [85, 150, 255]),
						([0,180,180],[170,255,255]),
						([200,200,200],[255,255,255])],  #remember to change white_img_mask in robo.py
			actual_s_height = 0.15, 
			actual_s_width = 0.12,
			buffer = 8, 
			x_buffer = 50, 
			y_buffer = 80)
						
robot_rx, robot_ry = Robo.move()

print("robot_rx:", robot_rx)
print("__________________")
print("robot_ry:", robot_ry)

#get relative movement --> returns a list of list
rel_movement = []

for idx, x in enumerate(robot_rx):
	if idx == 0:
		continue
	else:
		rel_x = round(robot_rx[idx] - robot_rx[idx-1],4) 
		rel_y = round(robot_ry[idx] - robot_ry[idx-1],4)
		rel_movement.append([rel_x,rel_y])

print('rel_movement:', rel_movement)


# #connect to robot
# robot = Robot(findrobotIP()) # router
# #robot = Robot('192.168.1.111')
# #x = forward, y = right for robot sdk but initially x is x-axis, y is y-axis for rel_movement

# #retract arm
# robot._sendcommand('robotic_arm moveto x 0 y 150')
# time.sleep(2)

# #move to starting position
# robot.move('x 0.4 y 0.0 vxy 0.3')  #adjust x value
# time.sleep(2)

# time_scale = 3.5
# def round_movement(val, grid_dist=0.8):
# 	return float(grid_dist * round(val/grid_dist))

# #move based on plotted path
# for i, movement in enumerate(rel_movement):
# 	if i != 0 and i != len(rel_movement) - 1:
# 		# x is VERTICAL DIRECTION!
# 		move_x = round_movement(movement[1]) * 1
# 		# y is HORI DIRECTION!
# 		move_y = round_movement(movement[0]) * 1
# 	else:
# 		move_x = movement[1]
# 		move_y = movement[0]
# 	mvt_string = 'x '+ str(move_x) +' y ' + str(move_y) + ' vxy 0.3'
# 	dist = math.sqrt(move_x**2 + move_y**2)
# 	print(mvt_string)
# 	robot.move(mvt_string)
# 	if move_y == 0:
# 		time.sleep(time_scale * dist)
# 	else: 
# 		time.sleep(time_scale * dist * 1.5)
# 	print("Instruction Sent")

# robot.exit()