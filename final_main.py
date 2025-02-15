import os
import random
import cv2
import serial
import subprocess  # For playing videos
import time
import numpy as np
import multiprocessing
from playsound import playsound

# --- Configuration ---
SERIAL_PORT = "COM3"  # Replace with your Arduino's serial port
BAUD_RATE = 9600  # Match your Arduino's baud rate
VIDEO_FOLDER = "videos"  # Replace with the actual path
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi"]  # Add other extensions if needed
MUSIC_NAME = "alone.mp3" # Change to your music's name
WIDTH = 4096
HEIGHT = 2160
COLOR = (0, 0, 0) # Black

previous_state = "0"
p = multiprocessing.Process(target=playsound, args=(MUSIC_NAME,))

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Connected to Arduino at {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

video_files = [
            f for f in os.listdir(VIDEO_FOLDER)
            if os.path.isfile(os.path.join(VIDEO_FOLDER, f)) and
               f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))  # Add more extensions if needed
        ]

#print(video_files)

video_path = []

for video_file in video_files:
            video_path.append(os.path.join(VIDEO_FOLDER, video_file))
    
#print(video_path)

image = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
image[:] = COLOR
cv2.imwrite('blank.jpg', image)

### FUNCTIONS ###

def serial_signal():
    try:
            line = arduino.readline().decode("utf-8").rstrip()  # Read from serial
            print(line)

    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")
        cv2.destroyAllWindows()
    
    return line

def play_video():
    random.shuffle(video_path)
    cap = cv2.VideoCapture(video_path[0])

    if not cap.isOpened():
                print(f"Error opening video: {video_path}")

    while(cap.isOpened()):
    # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
        # Display the resulting frame
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow('window', frame)
            
        # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            cv2.destroyAllWindows()
            break
    
    cv2.destroyAllWindows()
 
### MAIN ###
if __name__ == "__main__":
    while True:
        detection = serial_signal()
 
        if detection == "1":
            if previous_state == "0":
                p.start()
            play_video()
            previous_state = "1"
            arduino.reset_input_buffer()  # Clear any remaining input
            time.sleep(1)  # Pause for 1 second (adjust as needed)
        else:
            if previous_state == "1":
                p.terminate()
            previous_state = "0"