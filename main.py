# copyright (C) 2024 sirococoa.

from typing import Any

import pyxel

import js

WINDOW_W = 256
WINDOW_H = 256


def distance(a: list[float], b: list[float]) -> float:
    return pyxel.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def subtraction(a: list[float], b: list[float]) -> list[float]:
    return [x - y for x, y in zip(a, b)]


class Hand:
    POINT_SIZE = 7
    POINT_COLOR = 7

    def __init__(self, landmarks: Any, aspect: float, time: float) -> None:
        self.points = []
        for landmark in landmarks:
            x, y, z = landmark['x'] - 0.5, landmark['y'] - 0.5, landmark['z']
            if aspect < 1:
                y = y / aspect
            else:
                x = x * aspect
            x, y = x + 0.5, y + 0.5
            self.points.append([1 - x, y, z])
        self.time = time

    def draw(self) -> None:
        for point in self.points:
            pyxel.circ(
                point[0] * WINDOW_W,
                point[1] * WINDOW_H,
                self.POINT_SIZE,
                self.POINT_COLOR,
            )


class MediapipeManager:
    def __init__(self) -> None:
        self.connect_flag = False
        self.detect_flag = False
        self.videoAspect = 1
        self.before_video_time = -1
        self.processing_time = 0
        self.hands = []

    def connect(self) -> None:
        enable_webcam_flag = js.webcamRunning
        enable_detection_flag = js.detectionRunning
        if enable_webcam_flag and enable_detection_flag:
            videoWidth = js.videoWidth
            videoHeight = js.videoHeight
            self.videoAspect = videoWidth / videoHeight
            self.connect_flag = True

    def update(self) -> None:
        videoWidth = js.videoWidth
        videoHeight = js.videoHeight
        self.videoAspect = videoWidth / videoHeight

        self.get_landmarks()

    def get_landmarks(self) -> None:
        results = js.results.to_py()
        print(results)
        video_time = results['videoTime']
        landmarks = results['landmarks']
        if self.before_video_time == video_time:
            return
        if self.before_video_time > 0:
            self.processing_time = video_time - self.before_video_time
        self.before_video_time = video_time
        if len(landmarks) == 0:
            self.detect_flag = False
        else:
            self.detect_flag = True
            self.hands = [Hand(landmark, self.videoAspect, video_time) for landmark in landmarks]

    def is_detect(self) -> bool:
        return self.detect_flag

    def is_video_connect(self) -> bool:
        return self.connect_flag

    def draw(self) -> None:
        for hand in self.hands:
            hand.draw()

class App:
    def __init__(self) -> None:
        pyxel.init(WINDOW_W, WINDOW_H)
        self.mediapipe_manager = MediapipeManager()
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if not self.mediapipe_manager.is_video_connect():
            self.mediapipe_manager.connect()
            return
        self.mediapipe_manager.update()

    def draw(self) -> None:
        pyxel.cls(0)
        if self.mediapipe_manager.is_video_connect():
            videoWidth = js.videoWidth
            videoHeight = js.videoHeight
            pyxel.text(
                WINDOW_W // 4,
                WINDOW_H - 10,
                'CAMERA {}x{}'.format(videoWidth, videoHeight),
                7,
            )
            if self.mediapipe_manager.is_detect():
                pyxel.text(WINDOW_W // 2 + 10, WINDOW_H - 10, 'HAND: found', 7)
            else:
                pyxel.text(WINDOW_W // 2 + 10, WINDOW_H - 10, 'HAND: not found', 7)
        else:
            pyxel.text(
                WINDOW_W // 4, WINDOW_H - 10, 'Waiting for camera to connect', 7
            )
        self.mediapipe_manager.draw()

App()
