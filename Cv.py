import cv2
import numpy as np
import tkinter as tk
import os
from tkinter import filedialog


#def select_image():
#    """Open a file dialog to select an image and return its file path."""
#    root = tk.Tk()
#    root.withdraw()  # Hides the main Tkinter window.
#    file_path = filedialog.askopenfilename()  # Show an "Open" dialog box and return the path to the selected file.
#   root.destroy()  # Destroy the Tk root window explicitly to avoid hanging.
#    return file_path

def outline_image(image_path, ImgName, Filedirectory):
    """Read an image from a path, outline it, calculate the center of mass for the outlines, and draw a blue dot there."""
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found or unable to load.")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours were found
    if contours:
        # Draw contours on the original image
        cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

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
            cv2.circle(image, (cX, cY), 5, (255, 0, 0), -1)
        else:
            print("Error: Combined center of mass could not be calculated.")
    else:
        print("Error: No contours found.")

    os.chdir(Filedirectory) #changes the directory to the folder where we are going to save the file
    cv2.imwrite(ImgName, image) #saves the image
    # cv2.imshow("Outlined Image with Center Dot", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

#def main():
#    """Main function to execute the script logic."""
#    image_file = select_image()
#    if image_file:
#        outline_image(image_file)
#    else:
#        print("No image selected.")
