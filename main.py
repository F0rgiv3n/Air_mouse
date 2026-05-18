import cv2
import pyautogui

from gesture_classifier import Gesture, GestureClassifier
from hand_tracker import HandTracker
from mouse_controller import MouseController

_INDEX_TIP = 8
_WRIST     = 0

_GESTURE_COLORS = {
    Gesture.POINTING: (0, 220, 0),
    Gesture.METAL:    (0, 165, 255),
    Gesture.PEACE:    (255, 80, 80),
    Gesture.FIST:     (60, 60, 255),
    Gesture.OPEN:     (160, 160, 160),
    Gesture.UNKNOWN:  (200, 200, 200),
}


def main() -> None:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    screen_w, screen_h = pyautogui.size()
    tracker    = HandTracker()
    classifier = GestureClassifier()
    controller = MouseController(screen_w, screen_h)

    print("Air Mouse running — press Q to quit")
    print("  ☝  Pointing  → move cursor")
    print("  🤘 Metal     → left click")
    print("  ✌  Peace     → right click")
    print("  ✊ Fist      → scroll")
    print("  ✋ Open hand → neutral")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        landmarks = tracker.process(frame)

        if landmarks:
            gesture = classifier.classify(landmarks)
            lm = landmarks

            if gesture == Gesture.POINTING:
                controller.move_cursor(lm[_INDEX_TIP].x, lm[_INDEX_TIP].y)
                controller.release_click()
                controller.reset_scroll()

            elif gesture == Gesture.METAL:
                controller.left_click()
                controller.reset_scroll()

            elif gesture == Gesture.PEACE:
                controller.right_click()
                controller.reset_scroll()

            elif gesture == Gesture.FIST:
                controller.scroll(lm[_WRIST].y)
                controller.release_click()

            else:
                controller.release_click()
                controller.reset_scroll()

            tracker.draw(frame, landmarks)

            label = gesture.name
            color = _GESTURE_COLORS[gesture]
            cv2.putText(frame, label, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 2, cv2.LINE_AA)
        else:
            controller.release_click()
            controller.reset_scroll()
            cv2.putText(frame, "No hand", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 100), 2)

        cv2.imshow("Air Mouse  [Q = quit]", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
