import mediapipe as mp
import cv2
import os


class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.max_hands = max_hands
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, 'hand_landmarker.task')
        
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        base_options = BaseOptions(model_asset_path=model_path)
        options = HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
            running_mode=VisionRunningMode.VIDEO
        )
        self.detector = HandLandmarker.create_from_options(options)
        self.mp_draw = mp.tasks.vision.drawing_utils
        self.mp_hands_connections = mp.tasks.vision.HandLandmarksConnections
        self.timestamp = 0

    def find_hands(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        self.results = self.detector.detect_for_video(mp_image, self.timestamp)
        self.timestamp += 33
        return frame

    def get_hand_landmarks(self, frame, hand_index=0):
        if self.results and self.results.hand_landmarks:
            if hand_index < len(self.results.hand_landmarks):
                return self.results.hand_landmarks[hand_index]
        return None

    def draw_landmarks(self, frame, hand_landmarks):
        if hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands_connections.HAND_CONNECTIONS
            )
        return frame

    def get_finger_positions(self, hand_landmarks):
        if not hand_landmarks:
            return {}

        lm = hand_landmarks

        return {
            'thumb_tip': (lm[4].x, lm[4].y),
            'index_tip': (lm[8].x, lm[8].y),
            'middle_tip': (lm[12].x, lm[12].y),
            'ring_tip': (lm[16].x, lm[16].y),
            'pinky_tip': (lm[20].x, lm[20].y),
            'thumb_base': (lm[2].x, lm[2].y),
            'index_base': (lm[5].x, lm[5].y),
            'middle_base': (lm[9].x, lm[9].y),
            'ring_base': (lm[13].x, lm[13].y),
            'pinky_base': (lm[17].x, lm[17].y),
            'wrist': (lm[0].x, lm[0].y)
        }
