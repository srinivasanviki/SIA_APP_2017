# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 20:58:50 2017

@author: naitikshukla
"""

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

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
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),(0, 235, 255), 1)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

			dB = 2*radius
			pixelsPerMetric = dB / width

			dimB = dB / pixelsPerMetric
			cv2.putText(frame, "{:.1f}in".format(dimB),(center[0]-10,center[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255,255) , 2)

			cv2.putText(frame, "Reference",(center[0]+int(radius)-20,center[1]+int(radius)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255,0) , 2)

	return pixelsPerMetric,frame

def main_box(image,pixelsPerMetric):
	#image = cv2.imread(image)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (7, 7), 0)

	# perform edge detection, then perform a dilation + erosion to
	# close gaps in between object edges
	edged = cv2.Canny(gray, 50, 100)
	edged = cv2.dilate(edged, None, iterations=1)
	edged = cv2.erode(edged, None, iterations=1)

	# find contours in the edge map
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,	cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# sort the contours from left-to-right and initialize the
	# 'pixels per metric' calibration variable
	#(cnts, _) = contours.sort_contours(cnts1)
	#pixelsPerMetric = None
	orig = image.copy()
	# loop over the contours individually
	c = max(cnts, key=cv2.contourArea)
	if cv2.contourArea(c) < 900:
		exit(0)
	box = cv2.minAreaRect(c)
	box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
	box = np.array(box, dtype="int")

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)
	cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

	# loop over the original points and draw them
	for (x, y) in box:
		cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = box
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

	return orig

if  __name__ == '__main__':
	image = "C:\\Users\\naitikshukla\\Downloads\\sia-ref-circle.jpg"
	#image = "C:\\Users\\naitikshukla\\Downloads\\ref1.jpg"
	width = 0.70
	image = cv2.imread(image)
	pixelRatio,frame = ref_object(image,width)
	print(pixelRatio)
	frame = main_box(frame,pixelRatio)
	cv2.imshow("Final",frame)
	cv2.waitKey(0)
