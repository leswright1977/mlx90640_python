Based on code from: https://github.com/pimoroni/mlx90640-library

An ugly but working hack for the raspberry pi 3 so we can build a thermal cam in python and openCV

mlx90640_driver.cpp

When compiled, the executable can be called with: sudo ./mlx90640_driver 8
Where 8 is the required FPS (4,8 and 16 work)

This program continually overwrites frame data to /tmp/heatmap.csv, where it can be read by other programs.

Note: Modify /etc/fstab to mount /tmp in to RAM, else this program will hammer your SD card!

thermalcam.py

And example program that reads data from /tmp/heatmap.csv and generates an image from it.
This image is scaled using bicubic interpolation and overlayed on a video stream from the picam.

