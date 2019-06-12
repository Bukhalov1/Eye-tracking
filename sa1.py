import cv2
import numpy as np
import dlib
from math import hypot
import sql_eye as sql

print('import predictor...')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
font = cv2.FONT_HERSHEY_PLAIN



def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio


def get_gaze_ratio(eye_points, facial_landmarks, frame, gray, Threshold, thrTurn, eyeReg):
    eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [eye_region], True, 255, 2)
    cv2.fillPoly(mask, [eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])

    gray_eye = eye[min_y: max_y, min_x: max_x]
    threshold = Threshold                                                                            # THRESHOLD
    #print(threshold)
    _, threshold_eye = cv2.threshold(gray_eye, threshold, 255, cv2.THRESH_BINARY)

    if thrTurn == 1:
        threshold_eye = cv2.resize(threshold_eye, None, fx=15, fy=15)
        cv2.imshow("Threshold", threshold_eye)
        sql.addCalibr(Threshold)

    if eyeReg == 1:
        cv2.polylines(frame, [eye_region], True, (200, 50, 30), 2) 
        # cv2.polylines(frame, [np_aim], True, (200, 50, 30), 1)
        cv2.imshow('EyeRegion', frame)

    height, width = threshold_eye.shape

    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)

    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero(right_side_threshold)
    try:
        gaze_ratio = round(left_side_white / right_side_white, 3)
        return gaze_ratio
    except ZeroDivisionError:
        return "ZeroDivisionError"

def mainfunc(frame, Threshold, thrTurn, eyeReg):
    g = str('empty')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for face in faces:
        landmarks = predictor(gray, face)

        # Detect blinking
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        if blinking_ratio > 5.7:
            cv2.putText(frame, "Blink", (200, 100), font, 3, (255, 0, 0))
        
        # Gaze detection
        gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks, frame, gray, Threshold, thrTurn, eyeReg)
        gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks, frame, gray, Threshold, thrTurn, eyeReg)

        if type(gaze_ratio_left_eye) == str:
            gaze_ratio_left_eye = gaze_ratio_right_eye
        if type(gaze_ratio_right_eye) == str:
            gaze_ratio_right_eye = gaze_ratio_left_eye
        try:
            gaze_ratio_average = round((gaze_ratio_left_eye + gaze_ratio_right_eye)/2, 3)
            g = gaze_ratio_average
            sql.addValue(g)
            #frame = cv2.putText(frame, str(gaze_ratio_average), (50, 150), font, 2, (0, 0, 255), 3)

        except TypeError:
            g = 404
            sql.addValue(g)

if __name__ == "__main__":
    vid = cv2.VideoCapture(0)
    while True:
        _, frame = vid.read()
        mainfunc(frame)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            sql.closeCursor()
            break