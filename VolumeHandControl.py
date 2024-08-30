import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#################
wCam, hCam = 640, 480
#################

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0
detector = htm.HandDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
vol =0
volBar =400
volPer =0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw = False)

    if len(lmList) >= 9:
        #print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img,(x1,y1), 9, (0,255,0),cv2.FILLED)
        cv2.circle(img,(x2,y2),9,(0,255,0),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2), (0,255,0), 2)
        cv2.circle(img,(cx,cy), 7,(0,255,0),cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        if length<30:
            cv2.circle(img, (cx, cy), 5, (0, 0,255), cv2.FILLED)

        vol = np.interp(length,[30,300],[minVol,maxVol])
        volBar = np.interp(length,[30,300],[400,150])
        volPer = np.interp(length, [30,300], [0,100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)

    cv2.rectangle(img,(50,150), (85,400),(255,200,0),3)
    cv2.rectangle(img,(50,int(volBar)), (85,400),(255,200,0),cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (53, 420), cv2.FONT_HERSHEY_PLAIN, 1, (255,0 , 0), 2)


    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10,70), cv2.FONT_HERSHEY_PLAIN, 1,(0,255,0), 2)
    cv2.imshow("Img", img)
    cv2.waitKey(1)

