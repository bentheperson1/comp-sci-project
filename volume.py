import cv2
import numpy as np
import hand_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 1280, 720

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    finger_one = 4
    finger_two = 12

    if len(lmList) != 0:
        x1, y1 = lmList[finger_one][1], lmList[finger_one][2]
        x2, y2 = lmList[finger_two][1], lmList[finger_two][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    if cv2.waitKey(5) == 27:
        break

    cv2.rectangle(img, (50, 150), (85, 400), (0, 150, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 255), cv2.FILLED)

    cv2.imshow("Volume", img)
    cv2.waitKey(1)
