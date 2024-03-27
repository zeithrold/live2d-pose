import json

from enum import Enum

import mediapipe as mp
import numpy as np

FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult


class MPImageBody:
    timestamp_ms: int | None
    image: np.ndarray | None
    closed: bool

    def __init__(
        self, timestamp_ms: int | None, image: np.ndarray | None, closed: bool
    ):
        self.timestamp_ms = timestamp_ms
        self.image = image
        self.closed = closed

    @staticmethod
    def closed_body():
        return MPImageBody(None, None, True)

    @staticmethod
    def from_json(data: dict):
        return MPImageBody(
            data.get("timestamp_ms"),
            np.array(data.get("image")),
            False,
        )


class MPResultType(Enum):
    READY = 0
    RESULT = 1


class MPResultBody:
    timestamp_ms: int
    result: FaceLandmarkerResult
    type: MPResultType

    def __init__(
        self, timestamp_ms: int, result: FaceLandmarkerResult, type: MPResultType
    ):
        self.timestamp_ms = timestamp_ms
        self.type = type
        self.result = result

    @staticmethod
    def ready_body():
        return MPResultBody(0, None, MPResultType.READY)

    @staticmethod
    def from_mp(timestamp_ms: int, result: FaceLandmarkerResult):
        result = json.dumps(result)
        return MPResultBody(timestamp_ms, result, MPResultType.RESULT)
    
