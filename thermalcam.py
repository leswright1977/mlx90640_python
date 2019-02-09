import cv2
import time
import numpy
import random
import math

#a hack to wake our bus if it hangs....
import subprocess
p = subprocess.run(['i2cdetect', '-y','1', '0x33', '0x33'])
#######################################

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np


camera = PiCamera()
camera.resolution = (288, 368) #start with a slightly larger image so we can crop and align later!
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(288, 368)) 

# allow the camera to warmup
time.sleep(0.1)

nmin = 0
nmax = 255
alpha1 = 0.5
alpha2 = 0.5

prevData = []

for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
	# Capture frame-by-frame
	frame = frame.array
	frame = cv2.flip( frame, 0 ) #flip if neccesary

	#crop and align visible image...
	#crop image y start yend, xstart xend
	frame = frame[5:325, 10:250]

	heatmap = np.zeros((32,24,3), np.uint8) #create the blank image to work from

	data = np.fromfile('/tmp/heatmap.csv', dtype=float, count=-1, sep=',') #get the data
	if np.array_equal(data,prevData):
		print('Data stall...Probing i2c')
		p = subprocess.run(['i2cdetect', '-y','1', '0x33', '0x33'])
				
	prevData = data

	index = 0
	#add to the image
	if len(data) == 768:
		for y in range (0,32):
			for x in range (0,24):
				val = (data[index]*10)-100
				if math.isnan(val):
					val = 0
				if val > 255:
					val=255
				#print(index)
				#print(data)

				heatmap[y,x] = (val,val,val)
			
				if(y == 16) and (x == 12):
					temp = data[index]
				index+=1
		heatmap = cv2.flip(heatmap, -1 ) #flip heatmap to match image
		prev_heatmap = heatmap #save the heatmap in case we get a data miss
	
	else:
		print("Data miss...Loading previous thermal image")
	try:
		heatmap = prev_heatmap
	except:
		print("Previous heatmap does not exist!")

	heatmap = cv2.normalize(heatmap,None,nmin,nmax,cv2.NORM_MINMAX)
	heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
	heatmap = cv2.resize(heatmap,(240,320),interpolation=cv2.INTER_CUBIC)


	# Display the resulting frame
	cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)

	#Sharpen the image up so we can see edges under the heatmap
	kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	frame = cv2.filter2D(frame, -1, kernel)

	frame = cv2.addWeighted(frame,alpha1,heatmap,alpha2,0) #combine the images

	cv2.line(frame,(120,150),(120,170),(0,0,0),1) #vline
	cv2.line(frame,(110,160),(130,160),(0,0,0),1) #hline

	cv2.putText(frame,'Temp: '+str(temp), (10, 10),\
	cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0, 255, 255), 1, cv2.LINE_AA)

	cv2.imshow('Thermal',frame)
	
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	res = cv2.waitKey(1)
	#print(res)
	
	if res == 113: #q
		break
	if res == 97: #a
		nmin += 10
		print(nmin)
	if res == 122: #z
		nmin -= 10
		print(nmin)
	if res == 115: #s
		nmax += 10
		print(nmax)
	if res == 120: #x
		nmax -= 10
		print(nmax)
	if res == 100: #d
		alpha1 += 0.1
		alpha2 -= 0.1
	if res == 99: #c
		alpha1 -= 0.1
		alpha2 += 0.1



cv2.destroyAllWindows()




