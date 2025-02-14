import os
import random
import cv2
import serial
import subprocess  # For playing videos
import time


# --- Configuration ---
SERIAL_PORT = "/dev/ttyACM0"  # Replace with your Arduino's serial port
BAUD_RATE = 9600  # Match your Arduino's baud rate
VIDEO_FOLDER = "videos"  # Replace with the actual path
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi"]  # Add other extensions if needed
MUSIC_NAME = "alone.mp3" # Change to your music's name

music_process = None

def play_music(music_path):
    global music_process  # Access the global variable
    if music_path:
        try:
            music_process = subprocess.Popen(["vlc", music_path])  # Store the process
            print(f"Playing music: {music_path}")
        except FileNotFoundError:
            print(f"Error: Media player not found.")
        except Exception as e:
            print(f"Error playing music: {e}")

def stop_music():
    global music_process
    if music_process:
        try:
            music_process.terminate()  # Stop the video process
            music_process = None  # Reset the process variable
            print("Music stopped.")
        except Exception as e:
            print(f"Error stopping music: {e}")

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"Connected to Arduino at {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

def play_random_videos(directory):
    """Plays videos in a given directory in a random order.

    Args:
        directory: The path to the directory containing the videos.
    """

    try:
        video_files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and
               f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))  # Add more extensions if needed
        ]

        if not video_files:
            print(f"No video files found in {directory}")
            return

        random.shuffle(video_files)  # Shuffle the list of video files

        for video_file in video_files:
            video_path = os.path.join(directory, video_file)
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                print(f"Error opening video: {video_path}")
                continue  # Skip to the next video

            cv2.namedWindow(video_file, cv2.WINDOW_NORMAL) # Create a named window
            cv2.setWindowProperty(video_file, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) # Set it to fullscreen

            ret, frame = cap.read()
            if not ret:  # End of video
                break

            cv2.imshow(video_file, frame) # Display the video with the filename as title

            if cv2.waitKey(25) & 0xFF == ord('q'): # Press 'q' to quit the current video
                break

            cap.release()
            cv2.destroyAllWindows()  # Close the window after the video finishes or 'q' is pressed

    except FileNotFoundError:
        print(f"Directory not found: {directory}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        try:
            line = arduino.readline().decode("utf-8").rstrip()  # Read from serial

            if line == "1" and previous_state == "0":
                play_music(MUSIC_NAME)

            if line == "1": # Object detected (rising edge)
                print("Object detected!")
                play_random_videos(VIDEO_FOLDER)
                previous_state = "1"  # Update state to avoid immediate re-triggering
                time.sleep(3)
                break

            elif line == "0": # Object no longer detected
                stop_music()
                cv2.destroyAllWindows()
                previous_state = "0"

        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            cv2.destroyAllWindows()
            break  # Exit the loop if there's a problem

        except Exception as e:
            print(f"An error occurred: {e}")
            cv2.destroyAllWindows()
            break

        time.sleep(0.1)  # Small delay

    arduino.close()  # Close the serial connection when done
    print("Program finished.")