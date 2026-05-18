import math
from enum import Enum, auto


class Gesture(Enum):
    POINTING = auto()   # index up only         → move cursor
    METAL    = auto()   # index + pinky up       → left click
    PEACE    = auto()   # index + middle up      → right click
    FIST     = auto()   # all fingers down       → scroll
    OPEN     = auto()   # all fingers up         → neutral
    UNKNOWN  = auto()


# MediaPipe landmark indices
_INDEX_TIP  = 8;  _INDEX_PIP  = 6
_MIDDLE_TIP = 12; _MIDDLE_PIP = 10
_RING_TIP   = 16; _RING_PIP   = 14
_PINKY_TIP  = 20; _PINKY_PIP  = 18

_STABILITY = 2  # consecutive frames to confirm a gesture change


def _up(lm, tip, pip) -> bool:
    return lm[tip].y < lm[pip].y


class GestureClassifier:
    def __init__(self):
        self._current   = Gesture.UNKNOWN
        self._candidate = Gesture.UNKNOWN
        self._count     = 0

    def classify(self, landmarks) -> Gesture:
        raw = self._raw(landmarks)

        if raw == self._candidate:
            self._count += 1
        else:
            self._candidate = raw
            self._count = 1

        if self._count >= _STABILITY:
            self._current = self._candidate

        return self._current

    def _raw(self, landmarks) -> Gesture:
        lm = landmarks

        index_up  = _up(lm, _INDEX_TIP,  _INDEX_PIP)
        middle_up = _up(lm, _MIDDLE_TIP, _MIDDLE_PIP)
        ring_up   = _up(lm, _RING_TIP,   _RING_PIP)
        pinky_up  = _up(lm, _PINKY_TIP,  _PINKY_PIP)

        # 🤘 metal: index + pinky up, middle + ring down
        if index_up and not middle_up and not ring_up and pinky_up:
            return Gesture.METAL

        # ✌ peace: index + middle up, ring + pinky down
        if index_up and middle_up and not ring_up and not pinky_up:
            return Gesture.PEACE

        # ☝ pointing: only index up
        if index_up and not middle_up and not ring_up and not pinky_up:
            return Gesture.POINTING

        # ✊ fist: all down
        if not index_up and not middle_up and not ring_up and not pinky_up:
            return Gesture.FIST

        # ✋ open: all up
        if index_up and middle_up and ring_up and pinky_up:
            return Gesture.OPEN

        return Gesture.UNKNOWN
