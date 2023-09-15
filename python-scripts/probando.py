import threading
import os

import cv2
import dlib
import time
from deepface import DeepFace


script_dir = os.path.dirname(os.path.realpath(__file__))
predictor_path = os.path.join(script_dir, "shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

detector = dlib.get_frontal_face_detector()

face_positions = ["front", "top", "bottom", "right", "left"]
current_position_index = 0

position_hold_counter = 0
position_hold_required = 10

def guide_user(position):
    if position == "front":
        return "Look directly at the camera."
    elif position == "top":
        return "Tilt your head upwards."
    elif position == "bottom":
        return "Tilt your head downwards."
    elif position == "right":
        return "Turn your head to your right."
    elif position == "left":
        return "Turn your head to your left."


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


cap =cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

counter =0

face_match = False

some_threshold = 100000

upward_tilt_sensitivity = 1.1

last_capture_time = None
capture_timeout = 1

results_dir = os.path.join(script_dir, "results")
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
reference_img_path = os.path.join(script_dir, "reference.jpg")
reference_img = cv2.imread(reference_img_path)



def check_face(frame):
    global face_match
    try:
        if DeepFace.verify(frame, reference_img.copy())['verified']:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False



def capture_photo(position, frame, x, y, w, h):
    global current_position_index
    sub_img = frame[y:y+h, x:x+w]
    
    if sub_img.size == 0 or sub_img is None:
        print("Sub-image is empty. Not saving.")
        return

    filename = os.path.join(results_dir, f"reference_{position}.jpg")
    cv2.imwrite(filename, frame[y_new:y_new+h_new, x_new:x_new+w_new])
    current_position_index += 1
    global last_capture_time
    last_capture_time = time.time()


def get_guidance(position):
    guidance_messages = {
        "front": "Look directly at the camera.",
        "top": "Tilt your head upwards.",
        "bottom": "Tilt your head downwards.",
        "right": "Turn your head to your right.",
        "left": "Turn your head to your left."
    }
    return guidance_messages.get(position, "")


while True:
    ret, frame = cap.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Using dlib's face detector
        detections = detector(gray)
        faces = [(d.left(), d.top(), d.width(), d.height()) for d in detections]

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()
            except ValueError:
                pass

        counter += 1

        if face_match:
            guidance = get_guidance(face_positions[current_position_index])
            cv2.putText(frame, guidance, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if len(faces) > 0:
                (x, y, w, h) = faces[0]

                expansion_ratio = 0.2
                margin_w = int(w * expansion_ratio)
                margin_h = int(h * expansion_ratio)

                x_new = max(0, x - margin_w)
                y_new = max(0, y - margin_h)
                w_new = w + 2 * margin_w
                h_new = h + 2 * margin_h

                # Obtain landmarks for the detected face
                shape = predictor(gray, detections[0])
                # Calculate the mid-point between the two eyes
                eye_left = (shape.part(36).x, shape.part(36).y)
                eye_right = (shape.part(45).x, shape.part(45).y)
                midpoint_eyes = ((eye_left[0] + eye_right[0]) // 2, (eye_left[1] + eye_right[1]) // 2)

                # Calculate the center of the bounding box
                center_face = (x + w // 2, y + h // 2)

                # Calculate the distance from the midpoint of the eyes to the center of the bounding box
                distance_to_center = center_face[0] - midpoint_eyes[0]

                # Calculating ratios
                nose_tip_y = shape.part(33).y
                distance_nose_to_top = nose_tip_y
                distance_nose_to_bottom = frame.shape[0] - nose_tip_y
                tilt_up_ratio_nose = distance_nose_to_top / distance_nose_to_bottom

                eyebrow_avg_y = (shape.part(21).y + shape.part(22).y) / 2
                chin_y = shape.part(8).y
                distance_eyebrows_to_top = eyebrow_avg_y
                distance_chin_to_bottom = frame.shape[0] - chin_y   # <-- Define this before using

                current_time = time.time()
                if last_capture_time and current_time - last_capture_time < capture_timeout:
                    continue

                

                # Sensitivity values; you can adjust these based on testing
                left_sensitivity = 15
                right_sensitivity = -15

                if distance_to_center > left_sensitivity:
                    position_hold_counter += 1
                else:
                    position_hold_counter = 0  # Reset the counter if the condition isn't met

                if face_positions[current_position_index] == "left" and position_hold_counter >= position_hold_required:
                    capture_photo("left", frame, x, y, w, h)
                    position_hold_counter = 0  # Reset the counter after capturing

                # Check for right condition
                if distance_to_center < right_sensitivity:
                    position_hold_counter += 1
                else:
                    position_hold_counter = 0  # Reset the counter if the condition isn't met

                if face_positions[current_position_index] == "right" and position_hold_counter >= position_hold_required:
                    capture_photo("right", frame, x, y, w, h)
                    position_hold_counter = 0 

                # Check for bottom condition
                if tilt_up_ratio_nose > 1.5:  # Adjusted threshold
                    position_hold_counter += 1
                else:
                    position_hold_counter = 0  # Reset the counter if the condition isn't met

                if face_positions[current_position_index] == "bottom" and position_hold_counter >= position_hold_required:
                    capture_photo("bottom", frame, x, y, w, h)
                    position_hold_counter = 0  # Reset the counter after capturing


                if distance_to_center > left_sensitivity:
                    # Face is turned to the left
                    if face_positions[current_position_index] == "left" and w > h:
                        capture_photo("left", frame, x, y, w, h)

                elif distance_to_center < right_sensitivity:
                    # Face is turned to the right
                    if face_positions[current_position_index] == "right" and w < h:
                        capture_photo("right", frame, x, y, w, h)

                else:
                    # Face is front-facing
                    if face_positions[current_position_index] == "front" and w*h > some_threshold:
                        capture_photo("front", frame, x, y, w, h)

                if distance_chin_to_bottom != 0:
                    tilt_up_ratio_eyebrows = distance_eyebrows_to_top / distance_chin_to_bottom
                else:
                    tilt_up_ratio_eyebrows = float('10000000') 

                # Checking conditions for capturing photos
                if face_positions[current_position_index] == "front" and w*h > some_threshold:
                    capture_photo("front", frame, x_new, y_new, w_new, h_new)

                elif face_positions[current_position_index] == "top" and tilt_up_ratio_nose < 0.7:
                    capture_photo("top", frame, x, y, w, h)

                elif face_positions[current_position_index] == "bottom" and tilt_up_ratio_nose > 1.5:  # Adjusted threshold
                    capture_photo("bottom", frame, x, y, w, h)

                elif distance_to_center > left_sensitivity:
                    if face_positions[current_position_index] == "left":
                        capture_photo("left", frame, x, y, w, h)

                elif distance_to_center < right_sensitivity:
                    if face_positions[current_position_index] == "right":
                        capture_photo("right", frame, x, y, w, h)

                if current_position_index >= len(face_positions):
                    cv2.putText(frame, "All photos captured!", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        else:
            cv2.putText(frame, "Face not detected", (20,450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)

        cv2.imshow("video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cv2.destroyAllWindows()