import matplotlib.pyplot as plt
import cv2
import numpy as np
import boto3


def detect_se(image):

    client=boto3.client('rekognition')

    height, width = image.shape
    retval, buffer = cv2.imencode('.jpg', image)
    byte_im = buffer.tobytes()

    response = client.detect_text(Image={'Bytes': byte_im})
    
    textDetections=response['TextDetections']
    print ('Detected text\n----------')
    bbox = []
    for text in textDetections:
            print ('Detected text:' + text['DetectedText'])
            print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
            print ('Id: {}'.format(text['Id']))
            print ('Bbox: {}'.format(text['Geometry']["BoundingBox"]))
            box = text['Geometry']["BoundingBox"]
            if text['DetectedText'] in ['S','E'] and text['Type'] == "WORD":
                bbox.append([box['Left'], box['Top'], box['Left']+ box['Width'], box['Top']+ box['Height'],
                             box['Left']+ box['Width']/2, box['Top']+ box['Height']/2,
                             text['DetectedText']])
            print ('Type:' + text['Type'])
            print()

    fin_box = {}
    for (startX, startY, endX, endY, c_x, c_y, letter) in bbox:
        x1 = int(startX * width)
        y1 = int(startY * height)
        x2 = int(endX * width)
        y2 = int(endY * height)
        c_x = int(c_x * width)
        c_y = int(c_y * height)
        box_height = int(y2 - y1)
        box_width = int(x2 - x1)
        fin_box[letter] = [startX, startY, endX, endY, c_x, c_y, box_height, box_width]

    return fin_box