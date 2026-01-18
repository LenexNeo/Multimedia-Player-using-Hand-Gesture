Universal Media Player using Hand Gesture Control
Control media playback such as VLC and YouTube using hand gestures detected via your webcam.
This project uses Python, OpenCV, and MediaPipe for real-time hand tracking and gesture recognition.
 Features
•	 Play / Pause using hand gesture
•	 Volume Up / Down by moving fingers vertically
•	 Fullscreen Toggle using both hands
•	 Real-time webcam hand tracking
•	 Smooth gesture response
•	 Works with most media players (VLC, YouTube, etc.)
 Technologies Used
•	Python
•	OpenCV
•	MediaPipe
•	PyAutoGUI
•	PyGetWindow
•	NumPy
 Installation
1️ Clone the repository
git clone https://github.com/LenexNeo/Multimedia-Player-using-Hand-Guesture.git
cd Multimedia-Player-using-Hand-Guesture

2️ Create and activate a virtual environment
python -m venv .venv
Windows
.\.venv\Scripts\activate

3️ Install dependencies
pip install opencv-python mediapipe pyautogui pygetwindow numpy

 Run the Application
python main2.py

 Gesture Controls
The media player can be controlled using hand gestures detected through the webcam. 
Opening all fingers along with the thumb will toggle play and pause. 
Raising only the index and middle fingers and moving the hand upward increases the volume, while moving it downward decreases the volume. 
Showing both hands with only the index fingers raised toggles fullscreen mode. 
When no hand is detected, the system remains in an idle state.

 Calibration
•	Automatic calibration runs at startup
•	Hold index and middle fingers steady during calibration
•	Improves gesture accuracy and volume control

 Notes
•	Run the program before opening VLC or YouTube
•	Ensure the media player window is active
•	Good lighting improves detection accuracy
•	Requires a working webcam

Author
Lehan Madhusankha
