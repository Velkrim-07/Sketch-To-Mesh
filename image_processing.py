import cv2
import numpy as np
import os

# this will be called once the images are ready

def prepare_image(image_path):
    
    image = cv2.imread(image_path)

    # temporary file size. adjusting files to the same scale can be beneficial for feature detectors
    resized_image = cv2.resize(image, (800, 600))  
    
    # grayscale reduces computational load
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) 

    # noise reduction
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # canny edge detection emphasizes edges in the image
    # we will most likely be using one of the two as feature detectors: ORB, AKAZE.
    # both feature detection algorithms have positive results from this as they often rely on edge information to find key points.
    edges = cv2.Canny(blurred_image, 50, 150)

    # defines region of interest inside of the image.
    # this will most likely not be necessary.
    
    # mask = np.zeros_like(edges)
    # roi_vertices = np.array([[(50, 600), (750, 600), (400, 100)]], dtype=np.int32)
    # cv2.fillPoly(mask, roi_vertices, 255)
    # masked_edges = cv2.bitwise_and(edges, mask)
    
    try:
        
        # its just going to try to connect and list db collection names
        output_path = os.path.join('C:/Users/RAFAEL MUITO ZIKA/Desktop/Test', 'prepared_image.png')
        cv2.imwrite(output_path, edges)
        print(f"Image prep done.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    

# example usage
# image_path = 'C:/Users/RAFAEL MUITO ZIKA/Pictures/emoji disdcord/pekora fate.png'
# prepared_image = prepare_image(image_path)
