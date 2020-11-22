import cv2
import os
import time
from drone.Tello_api import Tello

class Drone():
    def __init__(self, autonomous=True , img_folder="./Path_planning/images/test", height_d=130, forward_dist=70, num_images=10):
        self.IMG_FOLDER = img_folder
        self.DEF_IMG = "./Path_planning/maze.jpg" # name of image captured by tello
        self.speed = 60
        self.fly_height = 100
        self.dist_bet_pads = 100
        self.capture_height = self.fly_height + height_d
        self.height_increment = 20
        self.back_increment = 20
        self.forward_dist = forward_dist
        self.AUTONOMOUS = autonomous
        self.NUM_IMAGES = num_images

        assert os.path.isdir(img_folder), "WARNING: Folder not detected"

        self.tello = Tello()
        print("----- Drone initialised -----")

    def fly(self):
        self.tello.startvideo()
        self.tello.startstates()
        self.tello.get_height()
        
        if self.AUTONOMOUS:
            img = cv2.imread(self.DEF_IMG)
            cv2.imshow('0', img)

        while self.tello.frame is None:
            pass

        print("----- Taking off -----")
        self.tello._sendcommand('takeoff')
        self.tello.start_pad_det()

        image_taken = False
        reached_m2 = False
        reached_height = False
        img_count = 0

        while True:
            if self.AUTONOMOUS:
                if not image_taken:
                    if not reached_m2:
                        m2padreply = self.tello._sendcommand(
                            f'jump {self.dist_bet_pads} 0 {self.fly_height} {self.speed} 0 m1 m2')  # x y z speed yaw pad_ids
                        if m2padreply == "ok":
                            print("Reached m2")
                            reached_m2 = True
                    else:
                        if not reached_height:
                            if self.tello.height < self.capture_height - self.height_increment:
                                self.tello._sendcommand(f'up {self.height_increment}')
                                print("Increasing height to capture map.")
                            else:
                                reached_height = True
                        else:
                            self.tello._sendcommand(f'forward {self.forward_dist}')

                            print("Capturing Image")
                            for i in range(self.NUM_IMAGES):
                                SAVE_IMG_PATH = os.path.join(self.IMG_FOLDER, f'maze-{i}.jpg')
                                cv2.imwrite(SAVE_IMG_PATH, self.tello.frame)
                                #cv2.imshow('Saved Image', self.tello.frame)
                                print(f'Saved as {SAVE_IMG_PATH}!')

                                if i != self.NUM_IMAGES - 1:
                                    time.sleep(1)

                            image_taken = True

                    k = cv2.waitKey(16) & 0xFF
                    if k == 13:  # enter to retrieve drone, land and continue
                        print("Enter Button Pressed..GOING BACK")
                        m1padreply = self.tello._sendcommand(
                            f'jump -{self.dist_bet_pads} 0 {self.fly_height} {self.speed} 0 m2 m1')  # x y z self.speed yaw pad_ids
                        if m1padreply == "ok":
                            print("Reached m1")
                            print('Landing...')
                            self.tello.exit()
                        else:
                            print('Landing...')
                            self.tello.exit()
                        break
                    elif k == 32:  # spacebar to enter manual mode
                        print("going to manual")
                        self.AUTONOMOUS = False

                else:
                    # return to m1
                    print("Image taken. Going back")
                    self.tello._sendcommand(f'back {self.forward_dist}')

                    m1padreply = self.tello._sendcommand(f'jump -{self.dist_bet_pads} 0 {self.fly_height} {self.speed} 0 m2 m1')  # x y z self.speed yaw pad_ids
                    if m1padreply == "ok":
                        print("Reached m1")
                        print('Landing...')
                        self.tello.exit()
                        break
                    else:
                        print("Marker 1 not found. Moving backwards and then landing.")
                        self.tello._sendcommand(f'back {self.back_increment}')
                        self.tello.exit()

                    k = cv2.waitKey(16) & 0xFF
                    if k == 13:  # enter to retrieve drone, land and continue
                        print("Enter Button Pressed..GOING BACK")
                        m1padreply = self.tello._sendcommand(
                            f'jump -{self.dist_bet_pads} 0 {self.fly_height} {self.speed} 0 m2 m1')  # x y z self.speed yaw pad_ids
                        if m1padreply == "ok":
                            print("Reached m1")
                            print('Landing...')
                            self.tello.exit()
                        else:
                            print('Landing...')
                            self.tello.exit()
                        break
                    elif k == 32:  # spacebar to enter manual mode
                        print("going to manual")
                        self.AUTONOMOUS = False

            else:
                cv2.namedWindow('Tello video', cv2.WINDOW_NORMAL)
                cv2.imshow('Tello video', self.tello.frame)
                
                k = cv2.waitKey(16) & 0xFF
                if k == 32:  # spacebar to capture image
                    SAVE_IMG_PATH = os.path.join(self.IMG_FOLDER, f'maze-manual-{img_count}.jpg')
                    img_count += 1
                    cv2.imwrite(SAVE_IMG_PATH, self.tello.frame)
                    print(f'Saved as {SAVE_IMG_PATH}!')
                    #cv2.imshow('Saved Image', self.tello.frame)

                elif k == 13:  # enter to retrieve drone, land and continue
                    #padreply = self.tello._sendcommand(f'jump -{self.dist_bet_pads} 0 {self.fly_height} {self.speed} 0 m2 m1')  # x y z self.speed yaw pad_ids
                    #if padreply == "ok":
                        #print("Reached m1")
                    print('Landing...')
                    self.tello.exit()
                    break

                elif k != -1:  # press wasdqe to adjust position of drone, uj to adjust height
                    self.tello.act(k)

        cv2.destroyAllWindows()
