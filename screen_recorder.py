import cv2
import numpy as np
import pyautogui

# screen resolution
SCREEN_SIZE = tuple(pyautogui.size())
# define the codec
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
# frames per second
fps = 12.0
# recording time in seconds
record_seconds = 20
# write object for video
out = cv2.VideoWriter("video.mp4", fourcc, fps, (SCREEN_SIZE))

'''
capture screenshots and write then to a file in a loop until
the seconds are passes or the user clicks the "q" button.
'''

for i in range(int(record_seconds * fps)):

    # create a screenshot
    img = pyautogui.screenshot(region=(0, 0, 500, 900))

    # convert pixels into an numpy array
    frame = np.array(img)

    # convert colors from BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # write the frame
    out.write(frame)

    # show the frame
    cv2.imshow("video frame", frame)

    # if the user clicks q, it exits
    if cv2.waitKey(1) == ord("q"):
        break

# make sure everything is closed when exited
cv2.destroyAllWindows()
out.release()