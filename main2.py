import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import pygetwindow as gw

# ================= CONFIG =================
pyautogui.FAILSAFE = False
SCROLL_INTERVAL = 0.05   # seconds between volume adjustments
PLAY_PAUSE_DELAY = 1     # seconds between play/pause
CALIBRATION_FRAMES = 50  # frames for calibration
FULLSCREEN_COOLDOWN = 1  # seconds between fullscreen toggles

# ================= VARIABLES =================
prev_y = None
scroll_direction = 0
last_scroll_time = 0
last_play_pause_time = 0
last_fullscreen_time = 0
volume_level = 50  # overlay simulation
fps_time = time.time()
fps = 0
scroll_threshold = 5  # will be updated after calibration

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Camera not accessible")
    exit()
h_cam, w_cam = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

# ================= MEDIAPIPE =================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ================= UI =================
def draw_status(frame, text, color, volume=None, fps=None):
    cv2.rectangle(frame, (10, 10), (550, 100), (0, 0, 0), -1)
    cv2.putText(frame, f"Action: {text}", (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    if volume is not None:
        cv2.putText(frame, f"Volume: {volume}%", (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    if fps is not None:
        cv2.putText(frame, f"FPS: {int(fps)}", (450, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

print("Universal Gesture Controller Running | ESC or ❌ to exit")
print("Calibration in progress... raise index+middle fingers steadily")

# ================= CALIBRATION =================
calib_deltas = []
calib_count = 0
cv2.namedWindow("Universal Gesture Controller", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Universal Gesture Controller", cv2.WND_PROP_TOPMOST, 1)  # Make window topmost during calibration
while calib_count < CALIBRATION_FRAMES:
    success, frame = cap.read()
    if not success:
        continue
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            index_tip = lm[8]
            middle_tip = lm[12]
            delta = abs(index_tip.y - middle_tip.y)
            calib_deltas.append(delta)
            calib_count += 1
            cv2.putText(frame, f"Calibrating... {calib_count}/{CALIBRATION_FRAMES}",
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow("Universal Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

if calib_deltas:
    scroll_threshold = np.mean(calib_deltas) * 15
print(f"Calibration done. Scroll threshold set to {scroll_threshold:.3f}")

# After calibration, minimize window after 2 seconds and activate VLC or YouTube
time.sleep(1)
controller_window = gw.getWindowsWithTitle("Universal Gesture Controller")
if controller_window:
    controller_window[0].minimize()

# Activate VLC or YouTube
vlc_windows = gw.getWindowsWithTitle("VLC")
youtube_windows = gw.getWindowsWithTitle("YouTube")
if vlc_windows:
    vlc_windows[0].activate()
elif youtube_windows:
    youtube_windows[0].activate()

# ================= MAIN LOOP =================
while True:
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    action = "Idle"
    gesture_active = False
    current_time = time.time()
    hand_visible = False

    if result.multi_hand_landmarks:
        hand_visible = True

        # ---------- Fullscreen gesture (both hands, index-only) ----------
        if len(result.multi_hand_landmarks) == 2:
            both_index_only = True
            for hand_landmarks in result.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                index_up = lm[8].y < lm[6].y
                middle_up = lm[12].y < lm[10].y
                ring_up = lm[16].y < lm[14].y
                pinky_up = lm[20].y < lm[18].y
                if not (index_up and not middle_up and not ring_up and not pinky_up):
                    both_index_only = False
                    break
            if both_index_only and (current_time - last_fullscreen_time > FULLSCREEN_COOLDOWN):
                try:
                    active_win = gw.getActiveWindow()
                    if active_win:
                        pyautogui.press("f")
                        action = "Fullscreen Toggle"
                        last_fullscreen_time = current_time
                except:
                    pass

        # ---------- Process each hand ----------
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            index_tip = lm[8]
            middle_tip = lm[12]
            ring_tip = lm[16]
            pinky_tip = lm[20]
            thumb_tip = lm[4]

            # Finger states
            index_up = index_tip.y < lm[6].y
            middle_up = middle_tip.y < lm[10].y
            ring_up = ring_tip.y < lm[14].y
            pinky_up = pinky_tip.y < lm[18].y
            thumb_out = thumb_tip.x < lm[3].x

            active_win = gw.getActiveWindow()
            active_title = active_win.title if active_win else ""

            # ---------- Play/Pause gesture ----------
            if all([index_up, middle_up, ring_up, pinky_up]) and thumb_out:
                if current_time - last_play_pause_time > PLAY_PAUSE_DELAY:
                    if active_win:  # any active player
                        pyautogui.press("playpause")
                        last_play_pause_time = current_time
                        action = "Play / Pause"
                        scroll_direction = 0
                        prev_y = None

            # ---------- Volume gesture ----------
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture_active = True
                cy = int(index_tip.y * h)
                if prev_y is None:
                    prev_y = cy
                    scroll_direction = 0
                else:
                    delta = prev_y - cy
                    if abs(delta) > scroll_threshold:
                        scroll_direction = 1 if delta > 0 else -1
                        action = "Volume Up" if scroll_direction == 1 else "Volume Down"
                    prev_y = cy
            else:
                gesture_active = False
                if action not in ["Play / Pause", "Fullscreen Toggle"]:
                    action = "Idle"
                scroll_direction = 0
                prev_y = None

            # ---------- Visual cursor ----------
            cx = int(index_tip.x * w)
            cy = int(index_tip.y * h)
            color = (0,255,0)
            if action in ["Play / Pause","Volume Up","Volume Down","Fullscreen Toggle"]:
                color = (0,255,255)
            cv2.circle(frame, (cx, cy), 10, color, -1)

    # ---------- Stop scrolling if no hand ----------
    if not hand_visible:
        scroll_direction = 0
        prev_y = None
        if action not in ["Play / Pause", "Fullscreen Toggle"]:
            action = "Idle"

    # ---------- Execute volume smoothly ----------
    if scroll_direction != 0 and current_time - last_scroll_time > SCROLL_INTERVAL:
        active_win = gw.getActiveWindow()
        if active_win:
            if scroll_direction == 1:
                pyautogui.press("volumeup")
                volume_level = min(volume_level+1, 100)
            else:
                pyautogui.press("volumedown")
                volume_level = max(volume_level-1, 0)
        last_scroll_time = current_time

    # ---------- FPS ----------
    fps = 1 / (current_time - fps_time)
    fps_time = current_time

    # ---------- Overlay ----------
    draw_status(frame, action, (0,255,0), volume=volume_level, fps=fps)

    cv2.imshow("Universal Gesture Controller", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    if cv2.getWindowProperty("Universal Gesture Controller", cv2.WND_PROP_VISIBLE) < 1:
        break

# ================= CLEANUP =================
cap.release()
cv2.destroyAllWindows()
