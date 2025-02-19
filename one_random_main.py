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
VIDEO_NAME = "videos"  # Replace with the actual path
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi"]  # Add other extensions if needed
BLANK_VIDEO = "black_footage.mp4"
MUSIC_NAME = "alone.mp3" # Change to your music's name
WIDTH = 4096
HEIGHT = 2160
COLOR = (0, 0, 0) # Black

previous_state = "0"

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Connected to Arduino at {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

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

def play_video(p):
    cap = cv2.VideoCapture(VIDEO_NAME)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not cap.isOpened():
                print(f"Error opening video: {VIDEO_NAME}")

    if total_frames <= 0:  # Handle cases where frame count is unavailable
            print("Warning: Could not determine total frame count. Playing from beginning.")
            start_frame = 0
    else:
        start_frame = random.randint(0, total_frames - 1)  # Choose a random frame

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Seek to the random frame

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:  # Check if a frame was successfully read
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow('window', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):  # Exit on 'q' press
                break
        
            detection = serial_signal()

            if detection == "0":
                cap.release()  # Stop the video
                cv2.destroyAllWindows() # Close the window
                if p is not None:
                    p.terminate()
                    p.join()
                    p = None
                return  # Exit the video playing function
            
        else:
            cv2.destroyAllWindows()
            break
        
    cv2.destroyAllWindows()
 
def play_blank():
    cap = cv2.VideoCapture(BLANK_VIDEO)

    if not cap.isOpened():
                print(f"Error opening video: {VIDEO_NAME}")

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
            
            detection = serial_signal()

            if detection == "1":
                cap.release()  # Stop the video
                cv2.destroyAllWindows() # Close the window
                return  # Exit the video playing function

        else:
            cv2.destroyAllWindows()
            break
    
    cv2.destroyAllWindows()


### MAIN ###
if __name__ == "__main__":
    p = None
    while True:
        detection = serial_signal()
 
        if detection == "1":
            if previous_state == "0":
                if p is None:
                    p = multiprocessing.Process(target=playsound, args=(MUSIC_NAME,))
                    p.start()
            play_video(p)
            previous_state = "1"
            arduino.reset_input_buffer()  # Clear any remaining input
            time.sleep(1)  # Pause for 1 second (adjust as needed)
        else:
            #play_blank()
            cv2.destroyAllWindows()
            if previous_state == "1":
                if p is not None:
                    p.terminate()
                    p.join()
                    p = None
            previous_state = "0"