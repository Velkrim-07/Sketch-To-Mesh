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
    

def match_features(descriptors1, descriptors2, method='ORB'):
    # using ORB and AKAZE for testing
    if method == 'ORB':
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    else:  
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    # knn Matching descriptors
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    
    # RATIO TEST
    good_matches = []
    for m, n in matches:
        if m.distance < 0.5 * n.distance:  # Ratio test
            good_matches.append(m)
    
    return good_matches

def draw_matches(image1, keypoints1, image2, keypoints2, matches):

    matched_image = cv2.drawMatches(image1, keypoints1, image2, keypoints2, matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    return matched_image


def detect_and_describe_akaze(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        raise IOError("Could not open the image from path: {}".format(image_path))
    
    akaze = cv2.AKAZE_create()
    keypoints = akaze.detect(image, None)
    
    # compute descriptors for the detected keypoints
    keypoints, descriptors = akaze.compute(image, keypoints)
    
    return keypoints, descriptors

def test():

    img_path1 = 'C:/Users/RAFAEL MUITO ZIKA/Desktop/Test/front.png'
    img_path2 = 'C:/Users/RAFAEL MUITO ZIKA/Desktop/Test/side.png'
    img_path3 = 'C:/Users/RAFAEL MUITO ZIKA/Desktop/Test/sidee.png' 

    # detect
    keypoints1, descriptors1 = detect_and_describe_akaze(img_path1)
    keypoints2, descriptors2 = detect_and_describe_akaze(img_path2)
    keypoints3, descriptors3 = detect_and_describe_akaze(img_path3)

    # match
    matches12 = match_features(descriptors1, descriptors2, method='AKAZE')
    matches23 = match_features(descriptors2, descriptors3, method='AKAZE')
    matches13 = match_features(descriptors1, descriptors3, method='AKAZE')

    # visualize
    image1 = cv2.imread(img_path1)
    image2 = cv2.imread(img_path2)
    image3 = cv2.imread(img_path3)

    matched_image12 = draw_matches(image1, keypoints1, image2, keypoints2, matches12)
    matched_image23 = draw_matches(image2, keypoints2, image3, keypoints3, matches23)
    matched_image13 = draw_matches(image1, keypoints1, image3, keypoints3, matches13)

    # display
    cv2.imshow('Matches between Image 1 and Image 2', matched_image12)
    cv2.imshow('Matches between Image 2 and Image 3', matched_image23)
    cv2.imshow('Matches between Image 1 and Image 3', matched_image13)

    cv2.waitKey(0)  # Wait for a key press to exit
    cv2.destroyAllWindows()  # Close all the opened windows

# example usage
#image_path = 'C:/Users/RAFAEL MUITO ZIKA/Pictures/emoji disdcord/pekora fate.png'
#prepared_image = prepare_image(image_path)


