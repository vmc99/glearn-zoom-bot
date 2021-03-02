import pyautogui
import time
import cv2
import numpy as np
import imutils

def ImageDetection(temp_img,threshold,img_type):

	image = pyautogui.screenshot()
	img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
	img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) 
	# 0 is for grayscale
	template = cv2.imread(temp_img,0) 
	temp_bgr = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)
	temp_gray = cv2.cvtColor(temp_bgr, cv2.COLOR_BGR2GRAY)
	temp_edged = cv2.Canny(temp_gray, 50, 200)
	w, h = template.shape[::-1]
	found = None



	if img_type == "grayscale":
		selected_img = img_gray
		selected_temp_img = temp_gray


	if img_type == "edged":
		selected_img = img_gray
		selected_temp_img = temp_edged



	for scale in np.linspace(0.2, 1.0, 20)[::-1]: 
	  
	    # resize the image according to the scale, and keep track 
	    # of the ratio of the resizing 
		resized = imutils.resize(selected_img, width = int(selected_img.shape[1] * scale)) 
		r = selected_img.shape[1] / float(resized.shape[1]) 

	    # if the resized image is smaller than the template, then break 
	    # from the loop 
	    # detect edges in the resized, grayscale image and apply template  
	    # matching to find the template in the image edged  
	    # if we have found a new maximum correlation value, then update 
	    # the found variable if found is None or maxVal > found[0]: 
		if resized.shape[0] < h or resized.shape[1] < w:
			break

		if img_type == "edged":
			img_edged = cv2.Canny(resized, 50, 200)
			resized = img_edged


		result = cv2.matchTemplate(resized, selected_temp_img, cv2.TM_CCOEFF_NORMED)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

		if found is None or maxVal > found[0]:
	        # print(maxVal,maxLoc,r)
			if maxVal > threshold:
				found = (maxVal, maxLoc, r)



	# unpack the found varaible and compute the (x, y) coordinates 
	# of the bounding box based on the resized ratio 
	if not(type(found) == type(None)):
        
		(_, maxLoc, r) = found 
		# print("final :",found)
		(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r)) 
		(endX, endY) = (int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r)) 
	  

		x = (startX + endX)/2
		y = (startY + endY)/2

		return x,y


	else:

		return None