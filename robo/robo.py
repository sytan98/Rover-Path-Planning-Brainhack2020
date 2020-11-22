import cv2
import os
import numpy as np
import time
import matplotlib.pyplot as plt
from robo.obstacles import Obstacles
from robo.se_detect import detect_se
from robo.align_image import align
from robo.astarplanner import AStarPlanner

class Robo():
    def __init__(self, 
                actual_s_height = 0.15, 
                actual_s_width = 0.11, 
                grid_size = 40, 
                robot_radius = 96, 
                move_straight=True,
                directory= "./images/check", 
                reference = './images/reference.jpg', 
                buffer = 8, 
                x_buffer = 50, 
                y_buffer = 80, 
                boundaries = [([0, 0, 150], [85, 150, 255]),
                            ([0,180,180],[170,255,255]),
                            ([180,180,180],[255,255,255])],
                choose_smoothing = False):

        self.move_straight = move_straight
        self.actual_s_height = actual_s_height
        self.actual_s_width = actual_s_width
        self.grid_size = grid_size
        self.robot_radius = robot_radius
        self.directory = directory
        self.reference = reference
        self.buffer = buffer
        self.x_buffer = x_buffer
        self.y_buffer = y_buffer
        self.boundaries = boundaries
        self.choose_smoothing = choose_smoothing

    def move(self):
        #Walk through all the images in the image folder
        image = self.findimgwSE()
        cv2.imwrite("./images/outputimages/drone_img.jpg",image)
        # image = self.alignimg(image)
        # cv2.imwrite("./Path_planning/outputimages/aligned.jpg",image)

        #Find S and E in the image
        fin_box = self.findse(image)

        #Get obstacles and colour the grid black as well as cover S and E with a black box
        ox, oy = self.obstacles(image, fin_box)

        #Get Path
        rx, ry = self.findpath(image, ox, oy, fin_box)
        #print(rx)
        #print(ry)
        if self.choose_smoothing == True:
            rx, ry = self.path_smoothing(rx, ry)
        else:
            #need to reverse if nv smooth lines
            rx.reverse()  
            ry.reverse()

        if self.move_straight:
            new_rx, new_ry = self.remove_redundant(rx, ry)
        else:
            new_rx, new_ry = self.get_corners(rx, ry)
        
        #get scale
        s_height = fin_box['S'][-2]  #pixel values 
        s_width = fin_box['S'][-1]  #pixel values

        x_scale = (s_width/self.actual_s_width)
        y_scale = (s_height/self.actual_s_height)

        #scaling down to metres
        scaled_rx = [x / x_scale for x in new_rx] #[m]
        scaled_ry = [y / y_scale for y in new_ry] #[m]

        #converting to form w starting pt as origin
        st_x = scaled_rx[0]
        st_y = scaled_ry[0]
        robot_rx = [x - st_x for x in scaled_rx]
        robot_ry = [y - st_y for y in scaled_ry]

        print("__________________")
        print("rx:", rx)
        print("ry:", ry)
        print("__________________")
        print("new_rx:", new_rx)
        print("new_ry:", new_ry)
        print("__________________")
        print("scaled_rx:", scaled_rx)
        print("scaled_ry:", scaled_ry)
        print("__________________")

        plt.plot(rx, ry, "-r")
        plt.plot(new_rx, new_ry, "-b")
        plt.pause(.0001)
        plt.savefig('./images/outputimages/path1.jpg')
        # plt.show()

        plt.plot(new_rx, new_ry, "-b")
        image = cv2.cvtColor(cv2.flip(image,0), cv2.COLOR_BGR2RGB)
        plt.imshow(image, origin='lower')
        plt.savefig('./images/outputimages/path_w_image1.jpg')
        # plt.show()
    
        return robot_rx, robot_ry


    def mask_img_white(self, image):
        lower = np.array([200,200,200], dtype = "uint8")
        upper = np.array([255,255,255], dtype = "uint8")
        mask = cv2.inRange(image, lower, upper)
        print(mask.shape)
        output = cv2.bitwise_and(image, image, mask=mask)
        print(output.shape)
        gray = cv2.cvtColor(output,cv2.COLOR_BGR2GRAY)
        cv2.imwrite("./images/outputimages/gray.jpg", gray)
        return gray

    def findimgwSE(self):
        for root, dirs, files in os.walk(self.directory, topdown = False):
            for name in files:
                filepath = os.path.join(root, name)
                print(filepath)
                image = cv2.imread(filepath)
                image = cv2.flip(image,0)
                img_h, img_w, _ = image.shape
                scale = 1936 / img_h  
                image = cv2.resize(image, (int(scale * img_w), int(scale * img_h)), interpolation=cv2.INTER_CUBIC)

                #get white portions
                gray = self.mask_img_white(image)
                cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
                cv2.imshow('output', gray)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                #detect letters S&E
                fin_box = detect_se(gray)
                print(fin_box)
                if 'S' in fin_box.keys() and 'E' in fin_box.keys():
                    print("found image w both S and E")
                    return image
                    break
                else:
                    print('no S or E')
                    continue
    
    def alignimg(self, image):
        reference =  cv2.imread(self.reference)
        image, warp_matrix = align(reference, image)
        return image
    
    def findse(self, image):
        gray = self.mask_img_white(image)
        #detect letters S&E
        fin_box = detect_se(gray)
        return fin_box

    def obstacles(self, image, fin_box):

        #Get centre of bboxes for S and E
        sx = fin_box['S'][4]  
        sy = fin_box['S'][5]  
        gx = fin_box['E'][4]  
        gy = fin_box['E'][5]  

        #add rectangle over S and E with buffer
        sbx = sx - fin_box['S'][-1]/2 - self.buffer - self.x_buffer 
        sby = sy - fin_box['S'][6]/2  - self.buffer 
        stx = sx + fin_box['S'][-1]/2 + self.buffer + self.x_buffer
        sty = sy + fin_box['S'][6]/2 + self.buffer + self.y_buffer

        ebx = gx - fin_box['E'][-1]/2 - self.buffer - self.x_buffer
        eby = gy - fin_box['E'][6]/2 - self.buffer - self.y_buffer 
        etx = gx + fin_box['E'][-1]/2 + self.buffer + self.x_buffer 
        ety = gy + fin_box['E'][6]/2 + self.buffer 
        
        print("Image Shape:", image.shape)
        masked_image = cv2.rectangle(image, (int(sbx), int(sby)), (int(stx), int(sty)), (0, 0, 0), -1)
        masked_image = cv2.rectangle(masked_image, (int(ebx), int(eby)), (int(etx), int(ety)), (0, 0, 0), -1)
        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.imshow('output', masked_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # set obstacle positions
        ox, oy = Obstacles(masked_image, self.boundaries).calc_oxy()
        return ox, oy

    def findpath(self, image, ox, oy, fin_box):
        #set proper start and ending positions(they plot from top down)
        sx = fin_box['S'][4]  # [pixels]
        sy = image.shape[0] - fin_box['S'][5]  # [pixels]
        gx = fin_box['E'][4]  # [pixels]
        gy = image.shape[0] - fin_box['E'][5]  # [pixels]

        # if show_animation:  # pragma: no cover
        plt.plot(ox, oy, ".k")
        plt.plot(sx, sy, "og")
        plt.plot(gx, gy, "ob")
        plt.grid(True)
        plt.axis("equal")
        
        a_star = AStarPlanner(ox, oy, self.grid_size, self.robot_radius, self.move_straight)
        rx, ry = a_star.planning(sx, sy, gx, gy)

        plt.plot(rx, ry, "-r")
        plt.pause(0.001)
        plt.show()
        return rx, ry

    def remove_redundant(self, xc, yc):
        xc = xc.copy()
        yc = yc.copy()
        i = 0
        while i < len(xc) - 2:
            triplex = round(xc[i], 2) == round(xc[i+1], 2) and round(xc[i+1], 2) == round(xc[i+2], 2)
            tripley = round(yc[i] == yc[i+1], 2) and round(yc[i+1] == yc[i+2], 2)
            if triplex or tripley:
                xc.pop(i+1)
                yc.pop(i+1)
                i -= 1
            i += 1
        return xc, yc

    def path_smoothing(self, xc, yc):
        dist_threshold = self.grid_size * 2
        win_size = 4 if len(xc) > 16 else 2
        stride = 2

        xc = xc[::-1]   # reverse list
        yc = yc[::-1]

        move_x, move_y = [xc[0]], [yc[0]]
        i = 0

        while i + win_size < len(xc):
            win_x = xc[i:i+win_size]
            win_y = yc[i:i+win_size]

            if max(win_x) - min(win_x) >= dist_threshold:
                move_x.append(xc[i + win_size])
            else:
                move_x.append(move_x[-1])

            if max(win_y) - min(win_y) >= dist_threshold:
                move_y.append(yc[i + win_size])
            else:
                move_y.append(move_y[-1])

            i += stride

        if move_x[-1] != xc[-1] or move_y[-1] != yc[-1]:
            move_x.append(xc[-1])
            move_y.append(yc[-1])

        return move_x, move_y
    
    def get_corners(self, srx, sry):
        new_rx, new_ry = [], []
        for idx,value in enumerate(srx):
            if idx == len(srx)-1:
                new_rx.append(value)
                new_ry.append(sry[idx])
                break
            else:
                diff_x = srx[idx+1]-srx[idx]
                diff_y = sry[idx+1]-sry[idx]
                #print(diff_x,diff_y)
                if value == srx[idx-1] and value == srx[idx+1]:
                    #print(value,ry[idx])
                    continue
                elif sry[idx] == sry[idx-1] and sry[idx] == sry[idx+1]:
                    #print(value,ry[idx])
                    continue
                elif  (diff_x != 0.0 and srx[idx]-srx[idx-1] == diff_x) and (diff_y != 0.0 and sry[idx]-sry[idx-1] == diff_y):
                    continue

                else:
                    new_rx.append(value)
                    new_ry.append(sry[idx])

        return new_rx, new_ry
