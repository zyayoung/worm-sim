import cv2
import numpy as np
from worm import Worm

size = 512

pos = np.ones((2,))*size//2
angle_t = 0
angle = 0
worn = Worm()

history = [pos.copy() for _ in range(50)]

while True:
    action = worn.step(np.random.randint(12,27))
    if action == 1:
        pos += np.array([np.cos(angle), np.sin(angle)]) * worn.speed / 25
    elif action == 2:
        pos -= np.array([np.cos(angle), np.sin(angle)]) * worn.speed / 25
    elif action == 3:
        angle_t -= 0.5
    elif action == 4:
        angle_t += 0.5
    angle = angle_t
    history.append(pos.copy())
    history.pop(0)
    
    frame = np.zeros((size,size,3))
    for pos in history[5:-5]:
        try:
            # frame[int(pos[0]), int(pos[1])] = 255
            cv2.circle(frame, (int(pos[0]), int(pos[1])), 5, (255, 255, 255), -1)
        except IndexError:
            pass
    for idx, pos in enumerate(history[:5]):
        try:
            # frame[int(pos[0]), int(pos[1])] = 255
            cv2.circle(frame, (int(pos[0]), int(pos[1])), 1+idx, (255, 255, 255), -1)
        except IndexError:
            pass
    for idx, pos in enumerate(history[-5:]):
        try:
            cv2.circle(frame, (int(pos[0]), int(pos[1])), 5-idx, (255, 255, 255), -1)
        except IndexError:
            pass
    cv2.imshow("Oto Video", frame)
    cv2.waitKey(1)