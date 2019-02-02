import cv2
import time
import numpy
import random

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np


camera = PiCamera()
camera.resolution = (240, 320)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(240, 320)) 

# allow the camera to warmup
time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
	# Capture frame-by-frame
	frame = frame.array
	frame = cv2.flip( frame, 0 ) #flip if neccesary


	heatmap = np.zeros((32,24,3), np.uint8) #create the blank image to work from

	data = np.fromfile('/tmp/heatmap.csv', dtype=float, count=-1, sep=',') #get the data
	#print(len(data))
	index = 0
	#add to the image
	if len(data) == 768:
		for y in range (0,32):
			for x in range (0,24):
				val = (data[index]*10)-100
				if val > 255:
					val=255
				#print(index)
				#print(data)
				heatmap[y,x] = (val,val,val)
			
				if(y == 16) and (x == 12):
					temp = data[index]
				index+=1
		prev_heatmap = heatmap #save the heatmap in case we get a data miss
	else:
		print("Data miss...Loading previous thermal image")
	try:
		heatmap = prev_heatmap
	except:
		print("Previous heatmap does not exist!")

	heatmap = cv2.normalize(heatmap,None,0,255,cv2.NORM_MINMAX)
	heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
	heatmap = cv2.resize(heatmap,(240,320),interpolation=cv2.INTER_CUBIC)


	# Display the resulting frame
	cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)

	frame = cv2.addWeighted(frame,0.5,heatmap,0.5,0) #combine the images

	cv2.line(frame,(120,150),(120,170),(0,0,0),1) #vline
	cv2.line(frame,(110,160),(130,160),(0,0,0),1) #hline

	cv2.putText(frame,'Temp: '+str(temp), (10, 10),\
	cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0, 255, 255), 1, cv2.LINE_AA)

	cv2.imshow('Thermal',frame)
	
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


cv2.destroyAllWindows()



