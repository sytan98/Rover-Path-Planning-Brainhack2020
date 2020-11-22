# Rover-Path-Planning-Brainhack2020

This was WASD++'s attempt for the finals of the [DSTA BrainHack 2020] (https://www.dsta.gov.sg/brainhack)
Contributors: Daryl Lee, Ming Chong, Alvin, Wei Xiong, Kang Liang and Si Yu (me!)

## Purpose
We are given a Tello API drone and a DJI Robomaster EP rover. The objective was to use the drone to fly and capture a bird's eye view of the arena and to plot out a path for the rover. The arena has routes that are black in colour which the rover is allowed to travel on and has obstacles littered around the arena. Thus, we will need to process the picture taken by the drone and plan a path from the start point to the end point that avoids the obstacles.

## How it works
### [main.py] (main.py)
There are several components involved in this project. We have the drone component as well as the rover component and this script ties everything together. 
Running this will launch the following actions:
1. Initiate the drone to start flying and to take the picture.
2. Run through the frames taken and look for a frame that AWS Rekognition is able to identify both the letter "S" and "E" which stands for the start and end position for the rover.
3. Run through the A Star algorithm to plot a path
4. Send commands to Rover to travel to end point.

### Drone
[drone.py] (drone/drone.py)
This contains the drone object which upon initialising it, we can use a .fly() function for the drone to take off and it will take a few shots once it has reached a certain height. It allows for a switch to manual mode in the event that the autonomous mode does not work. It uses the Tello_API provided by DSTA to send commands to the Tello Drone.

### Robo
[robo.py] (robo/robo.py)
This contains the robo object which has been designed to allow quick adjustments to the attributes for tuning of the robo on the real arena itself.
1. Find S and E in the image. We tried using some OCR models such as using tesseract ocr, but the results were poor compared to using AWS Rekognition. So we went for it and will require boto3 client to be set up before running the script.
2. Get obstacles and colour the grid black as well as cover S and E with a black box
3. Get Path

### Potential Improvements (Not Fully Implemented)
1. Auto Aligning of frames taken by drone based on a reference image.