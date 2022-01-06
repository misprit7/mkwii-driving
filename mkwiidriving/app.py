import time
import os

import cv2
import numpy as np

import mss
import pyautogui

from controls.pad import Pad, Stick, Trigger, Button


def find_dolphin_dir():
    """Attempts to find the dolphin user directory. None on failure."""
    candidates = ['~/.dolphin-emu', '~/.local/share/dolphin-emu']
    for candidate in candidates:
        path = os.path.expanduser(candidate)
        if os.path.isdir(path):
            return path
    return None

dolphin_path = find_dolphin_dir()
if dolphin_path == None:
    print('No Dolphin path found, exiting')
print(dolphin_path)


with mss.mss() as sct, Pad(str(dolphin_path) + '/Pipes/pipe1') as pad:
    pad.press_button(Button.A)
    pad.tilt_stick(Stick.MAIN, 0.5, 0.5)

    # Part of the screen to capture
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

    last_time = time.time()
    previous_center = 0.5
    while True:
        # Run 10 times a second
        if time.time() - last_time < 0.1:
            continue

        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))

        # cv2.imwrite('../scripts/track.png', img)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower = np.array([12, 23, 61])
        upper = np.array([45, 84, 133])
        mask = cv2.inRange(hsv, lower, upper)

        center = [ np.average(indices) for indices in np.where(mask[:1080//2] >= 1) ]
        p = center[1] / 1920
        p = 0.5 + (p - 0.5) * 25
        d = (center[1]-previous_center) / (time.time() - last_time)
        d *= 0.003
        tilt = min(p+d, 1)
        tilt = max(tilt, 0)
        # if tilt > 0.52:
        #     tilt = 0.8
        # elif tilt < 0.48:
        #     tilt = 0.2
        print(f'tilt: {tilt:.2f}, p:{p:.2f}, d:{d:.2f}')

        pad.tilt_stick(Stick.MAIN, tilt, 0.5)
        previous_center = center[1]
        

        # Display the picture
        cv2.imshow("view", mask[:1080//2])

        last_time = time.time()
        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            pad.reset()
            break

