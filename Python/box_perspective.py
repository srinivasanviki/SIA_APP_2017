# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 20:58:50 2017

@author: naitikshukla
"""

# import the necessary packages
from scipy.spatial import distance as dist
import imutils
import cv2
import numpy as np

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def edgedetect (channel):
	sobelX = cv2.Sobel(channel, cv2.CV_16S, 1, 0)
	sobelY = cv2.Sobel(channel, cv2.CV_16S, 0, 1)
	sobel = np.hypot(sobelX, sobelY)

	sobel[sobel > 255] = 255; # Some values seem to go above 255. However RGB channels has to be within 0-255
	return sobel

def ref_object(frame,width = .90):
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	pixelsPerMetric =None
	center = None

	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the circle
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 20:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 11, 255), 3)
			cv2.circle(frame, center, 5, (200, 0, 255), -1)

			dB = 2*radius
			pixelsPerMetric = dB / width

			dimB = dB / pixelsPerMetric
			cv2.putText(frame, "{:.1f}in".format(dimB),(center[0]-10,center[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255,255) , 2)

			cv2.putText(frame, "Reference",(center[0]+int(radius)-20,center[1]+int(radius)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255,0) , 2)
	return pixelsPerMetric,frame


def main_box(img,pixelsPerMetric):
	blurred = cv2.GaussianBlur(img, (5, 5), 0) # Remove noise
	edgeImg = np.max( np.array([ edgedetect(blurred[:,:, 0]), edgedetect(blurred[:,:, 1]), edgedetect(blurred[:,:, 2]) ]), axis=0 )
	edgeImg = cv2.dilate(edgeImg, None, iterations=2)
	edgeImg = cv2.erode(edgeImg, None, iterations=2)
	mean = np.mean(edgeImg);
	# Zero any value that is less than mean. This reduces a lot of noise.
	edgeImg[edgeImg <= mean] = 0;
	edgeImg_8u = np.asarray(edgeImg, np.uint8)


	cnts = cv2.findContours(edgeImg_8u.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
	screenCnt = None

	# loop over our contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.05 * peri, True)
		#print(approx)
		# if our approximated contour has four points, then
		# we can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break
	pts = screenCnt.reshape(4, 2)
	orig=img.copy()
	cv2.drawContours(orig, [pts], -1, (0, 255, 0), 3)


	# loop over the original points and draw them
	for (x, y) in pts:
		cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = pts
	(tltrX, tltrY) = midpoint(tl, tr)
	(blbrX, blbrY) = midpoint(bl, br)

	# compute the midpoint between the top-left and bottom-left points,
	# followed by the midpoint between the top-righ and bottom-right
	(tlblX, tlblY) = midpoint(tl, bl)
	(trbrX, trbrY) = midpoint(tr, br)

	# draw the midpoints on the image
	cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

	# draw lines between the midpoints
	cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			 (255, 0, 255), 2)
	cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			 (255, 0, 255), 2)

	# compute the Euclidean distance between the midpoints
	dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
	dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

	# if the pixels per metric has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, inches)
	#if pixelsPerMetric is None:
	#	pixelsPerMetric = dB / width

	# compute the size of the object
	dimA = dA / pixelsPerMetric
	dimB = dB / pixelsPerMetric

	# draw the object sizes on the image
	cv2.putText(orig, "{:.1f}in".format(dimA),
				(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
				0.65, (255, 0, 255), 2)
	cv2.putText(orig, "{:.1f}in".format(dimB),
				(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
				0.65, (255, 0, 255), 2)

	return orig,dimA,dimB



def get_dimensions(image):
	import base64
	width = 0.75
	image = cv2.imread(image)
	image = imutils.resize(image, width=600)
	pixelRatio,frame = ref_object(image,width)
	#print("pixel Ratio=",pixelRatio)
	frame,h,w = main_box(frame,pixelRatio)
	#print("width=",w,"height =",h)
	print frame
	cnt = cv2.imencode('.jpg',frame)[1]
	b64 = base64.b64encode(cnt)

	return "width - %s,height - %s,image - %s"%(w,h,b64)
	#cv2.imshow("Final",frame)
	#cv2.waitKey(0)

