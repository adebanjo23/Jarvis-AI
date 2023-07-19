######################################
import socket

################################################### SOCKET DECLARATION

ip = "192.168.0.199"
port = 80

#################################################### OUTPUT PIN DECLARATIONS
room_light = 2
kitchen_light = 0
compound_light = 18
toilet_light = 17
switch = 32
step_light = 16
balcony_light = 33
shower_light = 5
lights = [room_light, kitchen_light, compound_light, toilet_light, switch, step_light, balcony_light, shower_light]

##################################################### LIGHT DEFINITIONS

import cv2
import time
import os
import HandTrackingModule as htm
#######################################
def main():
    wCam, hCam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0
    detector = htm.handDetector(detectionCon=0.75)
    tipIds = [4, 8, 12, 16, 20]


    def key_pressed(key):
        if key == ord(' '):
            cap.release()


    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            fingers = []
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            totalFingers = fingers.count(1)
            # ################################################ room_light
            # if totalFingers == 1:
            #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     s.connect((ip, port))
            #     s.send(f"{room_light},1".encode())
            #     s.close()
            #
            # ############################################### kitchen light
            # elif totalFingers == 2:
            #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     s.connect((ip, port))
            #     s.send(f"{kitchen_light},1".encode())
            #     s.close()
            #
            # ############################################### shower light
            # elif totalFingers == 3:
            #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     s.connect((ip, port))
            #     s.send(f"{shower_light},1".encode())
            #     s.close()
            #
            # ############################################# step light
            # elif totalFingers == 4:
            #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     s.connect((ip, port))
            #     s.send(f"{step_light},1".encode())
            #     s.close()
            #
            # ############################################# all lights
            # elif totalFingers == 5:
            #     for light in lights:
            #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #         s.connect((ip, port))
            #         s.send(f"{light},1".encode())
            #         s.close()
            #
            # elif totalFingers == 0:
            #     for light in lights:
            #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #         s.connect((ip, port))
            #         s.send(f"{light},0".encode())
            #         s.close()
            cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN,
                        10, (255, 0, 0), 25)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 0, 0), 3)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        key_pressed(key)

if __name__ == "__main__":
    main()