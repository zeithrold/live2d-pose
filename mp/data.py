import json

from enum import Enum

import mediapipe as mp
import numpy as np

FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult


class MPImageQueueType(Enum):
    IMAGE = 0
    CLOSED = 1


class MPResultQueueType(Enum):
    READY = 0
    RESULT = 1


class MPImageBody:
    timestamp_ms: int
    image: np.ndarray

    def __init__(self, timestamp_ms: int, image: np.ndarray):
        self.timestamp_ms = timestamp_ms
        self.image = image


class MPImageQueueBody:
    type: MPImageQueueType
    body: MPImageBody | None

    def __init__(self, type: MPImageQueueType, body: MPImageBody | None):
        self.type = type
        self.body = body

    @staticmethod
    def closed():
        return MPImageQueueBody(MPImageQueueType.CLOSED, None)

    @staticmethod
    def image(timestamp_ms: int, image: np.ndarray):
        return MPImageQueueBody(
            MPImageQueueType.IMAGE, MPImageBody(timestamp_ms, image)
        )

    @staticmethod
    def from_dict(data: dict):
        return MPImageQueueBody.image(
            int(data["timestamp_ms"]), np.array(data["image"], dtype=np.uint8)
        )


class MPResultBody:
    timestamp_ms: int
    result: FaceLandmarkerResult

    def __init__(self, timestamp_ms: int, result: FaceLandmarkerResult):
        self.timestamp_ms = timestamp_ms
        self.result = result

    def to_json(self):
        result = self.result
        face_landmarks = result.face_landmarks
        face_landmarks = [
            [landmark.__dict__ for landmark in face] for face in face_landmarks
        ]
        obj = {
            "timeStampMs": self.timestamp_ms,
            "multiFaceLandmarks": face_landmarks,
        }
        return json.dumps(obj)


class MPResultQueueBody:
    type: MPResultQueueType
    body: MPResultBody | None

    def __init__(self, type: MPResultQueueType, body: MPResultBody | None):
        self.type = type
        self.body = body

    @staticmethod
    def ready():
        return MPResultQueueBody(MPResultQueueType.READY, None)

    @staticmethod
    def result(timestamp_ms: int, result: FaceLandmarkerResult):
        return MPResultQueueBody(
            MPResultQueueType.RESULT, MPResultBody(timestamp_ms, result)
        )
