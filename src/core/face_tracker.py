"""
Face tracking module using MediaPipe Face Mesh.
Extracts 468/478 3D facial landmarks and resolves key feature points for eyes, nose, and lips.
"""

from typing import Any

import cv2
import mediapipe as mp
import numpy as np

from src.utils.logger import setup_logger

logger = setup_logger("FaceTracker")


class FaceTracker:
    """
    Processes video frames with MediaPipe Face Mesh and returns extracted landmarks.
    """

    # Canonical landmark index definitions
    NOSE_TIP_INDEX = 4
    NOSE_BRIDGE_INDEX = 1

    # Left eye landmarks: 6 key points (outer, upper outer, upper inner, inner, lower inner, lower outer)
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

    # Right eye landmarks: 6 key points (outer, upper outer, upper inner, inner, lower inner, lower outer)
    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

    # Lips landmarks for Mouth Aspect Ratio (MAR)
    # Left corner, upper outer, upper inner, right corner, lower inner, lower outer
    MOUTH_INDICES = [61, 0, 13, 291, 14, 17]

    # Contours for full eye rendering
    LEFT_EYE_CONTOUR = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    RIGHT_EYE_CONTOUR = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    LIPS_CONTOUR = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

    def __init__(
        self,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.last_detection_success = False
        logger.info("FaceTracker initialized with MediaPipe Face Mesh.")

    def process_frame(self, frame: np.ndarray) -> dict[str, Any] | None:
        """
        Processes a BGR image frame and extracts key facial landmarks.

        :param frame: BGR image from camera.
        :return: Dictionary with normalized & pixel landmark coordinates, or None if no face detected.
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            self.last_detection_success = False
            return None

        self.last_detection_success = True
        landmarks = results.multi_face_landmarks[0].landmark

        def get_pt(idx: int) -> tuple[float, float, float]:
            lm = landmarks[idx]
            return (lm.x, lm.y, lm.z)

        def get_px(idx: int) -> tuple[int, int]:
            lm = landmarks[idx]
            return (int(lm.x * w), int(lm.y * h))

        # Extract normalized coordinates
        nose_tip = get_pt(self.NOSE_TIP_INDEX)
        nose_bridge = get_pt(self.NOSE_BRIDGE_INDEX)
        left_eye = [get_pt(i) for i in self.LEFT_EYE_INDICES]
        right_eye = [get_pt(i) for i in self.RIGHT_EYE_INDICES]
        mouth = [get_pt(i) for i in self.MOUTH_INDICES]

        # Extract pixel coordinates for rendering
        nose_px = get_px(self.NOSE_TIP_INDEX)
        left_eye_px = [get_px(i) for i in self.LEFT_EYE_CONTOUR]
        right_eye_px = [get_px(i) for i in self.RIGHT_EYE_CONTOUR]
        mouth_px = [get_px(i) for i in self.LIPS_CONTOUR]

        return {
            "nose": (nose_tip[0], nose_tip[1]),
            "nose_3d": nose_tip,
            "nose_bridge": nose_bridge,
            "left_eye": [(p[0], p[1]) for p in left_eye],
            "right_eye": [(p[0], p[1]) for p in right_eye],
            "mouth": [(p[0], p[1]) for p in mouth],
            "raw_landmarks": landmarks,
            "pixels": {
                "nose": nose_px,
                "left_eye": left_eye_px,
                "right_eye": right_eye_px,
                "mouth": mouth_px,
            },
            "frame_size": (w, h),
        }

    def close(self) -> None:
        """
        Closes MediaPipe FaceMesh resources.
        """
        if self.face_mesh:
            self.face_mesh.close()
            logger.info("FaceTracker closed.")
