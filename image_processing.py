import cv2
import numpy as np
import os

# this will be called once the images are ready
def prepare_image(image_path):
      """Read an image from a path, outline it, calculate the center of mass for the outlines, and draw a blue dot there."""
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Image not found or unable to load.")
        return
    
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
    
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours were found
    if contours:
        # Draw contours on the original image
        cv2.drawContours(resized_image, contours, -1, (0, 255, 0), 2)
        # Calculate the combined center of mass for all contours
        totalX, totalY, totalArea = 0, 0, 0

        for contour in contours:
            M = cv2.moments(contour)

            if M["m00"] != 0:
                totalX += int(M["m10"])
                totalY += int(M["m01"])
                totalArea += M["m00"]

        if totalArea != 0:
            cX = int(totalX / totalArea)
            cY = int(totalY / totalArea)
            # Draw a blue dot at the combined center of mass
            cv2.circle(resized_image, (cX, cY), 5, (255, 0, 0), -1)
        else:
            print("Error: Combined center of mass could not be calculated.")
    else:
        print("Error: No contours found.")

    try:
        os.chdir(Filedirectory) #changes the directory to the folder where we are going to save the file
        cv2.imwrite(ImgName + Extension, resized_image) #saves the image
        os.chdir("..\\") #goes back one directory   
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
    # filters out weak matches by comparing the distance of the closes neighbor to that of the second closest neighbor.
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:  # Ratio test
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

def test_feature_detection():
    img_path1 = 'C:/Users/Rafael/Desktop/Exampel/side.png'
    img_path2 = 'C:/Users/Rafael/Desktop/Exampel/sidee.png'
    img_path3 = 'C:/Users/Rafael/Desktop/Exampel/front.png' 

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

    cv2.waitKey(0)  
    cv2.destroyAllWindows()  

# example usage
#image_path = 'C:/Users/RAFAEL MUITO ZIKA/Pictures/emoji disdcord/pekora fate.png'
#prepared_image = prepare_image(image_path)


