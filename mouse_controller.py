import time

import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

_MARGIN      = 0.15   # ignore outer 15% of camera frame edges
_SENSITIVITY = 1.8    # amplifies movement from center (>1 = less hand movement needed)
_ALPHA       = 0.35   # exponential smoothing: lower = smoother but more lag
_COOLDOWN    = 0.7    # seconds between clicks
_SCROLL_THRESHOLD = 0.008


class MouseController:
    def __init__(self, screen_w: int, screen_h: int):
        self._sw = screen_w
        self._sh = screen_h

        self._smooth_x: float | None = None
        self._smooth_y: float | None = None

        self._last_click = 0.0
        self._clicking   = False

        self._scroll_prev_y: float | None = None
        self._scroll_acc = 0.0

    # ------------------------------------------------------------------
    def move_cursor(self, norm_x: float, norm_y: float) -> None:
        # 1. Amplify position relative to frame center
        ax = (norm_x - 0.5) * _SENSITIVITY + 0.5
        ay = (norm_y - 0.5) * _SENSITIVITY + 0.5

        # 2. Remove margins and map to [0, 1]
        mx = (ax - _MARGIN) / (1 - 2 * _MARGIN)
        my = (ay - _MARGIN) / (1 - 2 * _MARGIN)
        mx = max(0.0, min(1.0, mx))
        my = max(0.0, min(1.0, my))

        target_x = mx * self._sw
        target_y = my * self._sh

        # 3. Exponential smoothing (less lag than moving average)
        if self._smooth_x is None:
            self._smooth_x, self._smooth_y = target_x, target_y
        else:
            self._smooth_x += _ALPHA * (target_x - self._smooth_x)
            self._smooth_y += _ALPHA * (target_y - self._smooth_y)

        pyautogui.moveTo(int(self._smooth_x), int(self._smooth_y))

    # ------------------------------------------------------------------
    def left_click(self) -> None:
        now = time.monotonic()
        if not self._clicking and (now - self._last_click) > _COOLDOWN:
            pyautogui.click()
            self._last_click = now
            self._clicking = True

    def release_click(self) -> None:
        self._clicking = False

    def right_click(self) -> None:
        now = time.monotonic()
        if (now - self._last_click) > _COOLDOWN:
            pyautogui.rightClick()
            self._last_click = now

    # ------------------------------------------------------------------
    def scroll(self, norm_y: float) -> None:
        if self._scroll_prev_y is None:
            self._scroll_prev_y = norm_y
            return

        delta = norm_y - self._scroll_prev_y
        self._scroll_prev_y = norm_y

        if abs(delta) < _SCROLL_THRESHOLD:
            return

        self._scroll_acc += delta
        steps = int(self._scroll_acc * 60)
        if steps:
            pyautogui.scroll(-steps)
            self._scroll_acc -= steps / 60

    def reset_scroll(self) -> None:
        self._scroll_prev_y = None
        self._scroll_acc    = 0.0
