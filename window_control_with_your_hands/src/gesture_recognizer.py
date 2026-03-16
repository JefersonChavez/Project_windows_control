import math


class GestureRecognizer:
    def __init__(self, finger_threshold=0.02):
        self.finger_threshold = finger_threshold
        self.last_gesture = None
        self.gesture_cooldown = 30
        self.gesture_timer = 0

    def is_finger_extended(self, tip_pos, base_pos):
        return tip_pos[1] < base_pos[1] - self.finger_threshold

    def is_finger_closed(self, tip_pos, base_pos):
        return tip_pos[1] > base_pos[1] + self.finger_threshold

    def get_extended_fingers(self, positions):
        if not positions:
            return []

        extended = []

        index_extended = self.is_finger_extended(positions['index_tip'], positions['index_base'])
        middle_extended = self.is_finger_extended(positions['middle_tip'], positions['middle_base'])
        ring_extended = self.is_finger_extended(positions['ring_tip'], positions['ring_base'])
        pinky_extended = self.is_finger_extended(positions['pinky_tip'], positions['pinky_base'])

        wrist_x = positions['wrist'][0]
        thumb_tip_x = positions['thumb_tip'][0]
        thumb_base_x = positions['thumb_base'][0]
        thumb_extended = abs(thumb_tip_x - wrist_x) > abs(thumb_base_x - wrist_x) + self.finger_threshold

        if index_extended:
            extended.append('index')
        if middle_extended:
            extended.append('middle')
        if ring_extended:
            extended.append('ring')
        if pinky_extended:
            extended.append('pinky')
        if thumb_extended:
            extended.append('thumb')

        return extended

    def recognize_gesture(self, positions):
        if not positions:
            return None

        extended_fingers = self.get_extended_fingers(positions)

        num_extended = len(extended_fingers)

        if num_extended == 0:
            return 'FIST'
        elif num_extended == 5:
            return 'PALM'
        elif num_extended == 2 and 'index' in extended_fingers and 'middle' in extended_fingers:
            if 'ring' not in extended_fingers and 'pinky' not in extended_fingers:
                return 'VICTORY'
        elif num_extended == 1 and 'index' in extended_fingers:
            return 'POINTING'
        elif num_extended == 3 and 'index' in extended_fingers and 'middle' in extended_fingers and 'ring' in extended_fingers:
            return 'THREE_FINGERS'
        elif num_extended == 4:
            fingers_only = [f for f in extended_fingers if f != 'thumb']
            if len(fingers_only) == 4:
                return 'FOUR_FINGERS'

        return None

    def should_trigger_gesture(self, gesture):
        if gesture != self.last_gesture:
            self.gesture_timer = 0
            return True

        self.gesture_timer += 1
        if self.gesture_timer > self.gesture_cooldown:
            self.gesture_timer = 0
            return True

        return False

    def update_gesture(self, gesture):
        if gesture:
            if self.should_trigger_gesture(gesture):
                self.last_gesture = gesture
                return True
        return False
