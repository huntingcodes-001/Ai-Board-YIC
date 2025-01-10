import serial
import time
from PIL import ImageGrab
import webbrowser
import os


# Arduino serial port and baud rate
arduino_port = 'COM3'
baud_rate = 9600


# Open the serial connection
ser = serial.Serial(arduino_port, baud_rate, timeout=1)


def take_screenshot():
   
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot_entire_screen.png")


   
    x1, y1, x2, y2 = 23, 34, 67, 47
    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screenshot.save("screenshot_window.png")


def open_browser():
   
    url = "https://www.google.com"


    # Open the URL in a new tab using the default web browser
    webbrowser.open_new(url)


def open_webcam():
    # Open the Windows Camera app using the command line
    os.startfile("microsoft.windows.camera:")


try:
    while True:
        # Read a line from the Arduino
        line = ser.readline().decode('utf-8').strip()
        print(line)


        if line:
            # Process the received message
            if 'LED A is ON' in line:
                print("SS Taken")
                take_screenshot()
            elif 'LED B is ON' in line:
                print("Opened Browser")
                open_browser()
            elif 'LED C is ON' in line:
                print("Opened Webcam")
                open_webcam()


except KeyboardInterrupt:
    # Close the serial connection on keyboard interrupt
    ser.close()
    print("Serial connection closed.")