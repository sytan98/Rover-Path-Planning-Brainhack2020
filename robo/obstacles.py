"""

Image Processing to get obstacles outs

"""

#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import math
import sys

class Obstacles:
    def __init__(self, image, boundaries):
        self.image = image
        self.boundaries = boundaries

    def calc_oxy (self):
        image = self.image
        """
        # filter for our version
        boundaries = [([0, 0, 150], [85, 150, 255]),
                    ([0,180,180],[170,255,255]),
                    ([150,150,150],[255,255,255]),
                    ]
        
        #filters for actual cones
        boundaries = [([0, 0, 150], [85, 150, 255]),
              ([0,180,180],[170,255,255]),
              ([180,180,180],[255,255,255]),
             ]
        """     
        i = 0
        masks = []
        for (lower, upper) in self.boundaries:
            # create NumPy arrays  from the boundaries
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            # find the colors within the specified boundaries and apply
            # the mask
            mask = cv2.inRange(image, lower, upper)
            output = cv2.bitwise_and(image, image, mask = mask)
            masks.append(output)
            filename = "./Path_planning/outputimages/output" +str(i) +".png"
            cv2.imwrite(filename, output)
            i += 1

        #Get Obstacles by combining all the outputs
        bit_or = cv2.bitwise_or(masks[0], masks[1])
        bit_or = cv2.bitwise_or(masks[2], bit_or)
        gray = cv2.cvtColor(bit_or,cv2.COLOR_BGR2GRAY)

        cv2.namedWindow("output", cv2.WINDOW_NORMAL) 
        cv2.imshow('output', gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        ox,oy = [],[]
        (height, width)= gray.shape
        
        whitepts = np.argwhere(gray >= 50)
        i = 0
        for pts in whitepts:
            if i%50 == 0:  
                pts = pts.tolist()
                ox.append(pts[1])
                oy.append(height - pts[0])
            i += 1
        

        return ox,oy