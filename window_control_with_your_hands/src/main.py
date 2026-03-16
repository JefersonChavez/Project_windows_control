import cv2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from window_controller import WindowController


def draw_text_with_background(img, text, position, font_scale=1.0, thickness=2, bg_color=(0, 255, 0), text_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_w, text_h = text_size

    x, y = position
    cv2.rectangle(img, (x, y - text_h - 10), (x + text_w + 10, y + 5), bg_color, -1)
    cv2.putText(img, text, (x + 5, y), font, font_scale, text_color, thickness)


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandDetector(max_hands=1, detection_confidence=0.8, tracking_confidence=0.8)
    gesture_recognizer = GestureRecognizer(finger_threshold=0.025)
    window_controller = WindowController()

    gesture_actions = {
        'FIST': ('Minimizar ventana', lambda: window_controller.minimize_window()),
        'VICTORY': ('Mover a otro monitor', lambda: window_controller.move_window_to_monitor()),
        'PALM': ('Restaurar ventana', lambda: window_controller.restore_window()),
    }

    print("=" * 50)
    print("CONTROL DE VENTANAS POR GESTOS")
    print("=" * 50)
    print("Gestos disponibles:")
    print("  [FIST] PUÑO CERRADO  -> Minimizar ventana")
    print("  [VICTORY] V (2 dedos)  -> Mover a otro monitor")
    print("  [PALM] PALMA ABIERTA -> Restaurar ventana")
    print("  q               -> Salir")
    print("=" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame")
            break

        frame = cv2.flip(frame, 1)

        frame = detector.find_hands(frame)

        hand_landmarks = detector.get_hand_landmarks(frame, 0)

        if hand_landmarks:
            frame = detector.draw_landmarks(frame, hand_landmarks)

            positions = detector.get_finger_positions(hand_landmarks)

            gesture = gesture_recognizer.recognize_gesture(positions)

            if gesture and gesture in gesture_actions:
                action_name, action_func = gesture_actions[gesture]

                if gesture_recognizer.update_gesture(gesture):
                    try:
                        action_func()
                        print(f"Ejecutado: {action_name}")
                    except Exception as e:
                        print(f"Error al ejecutar acción: {e}")

                if gesture == 'FIST':
                    color = (0, 0, 255)
                elif gesture == 'VICTORY':
                    color = (255, 0, 0)
                elif gesture == 'PALM':
                    color = (0, 255, 255)
                else:
                    color = (0, 255, 0)

                draw_text_with_background(frame, f"{gesture}: {action_name}", (10, 40), font_scale=0.8, bg_color=color)
            else:
                draw_text_with_background(frame, "Mano detectada", (10, 40), font_scale=0.8, bg_color=(0, 255, 0))
        else:
            draw_text_with_background(frame, "Esperando mano...", (10, 40), font_scale=0.8, bg_color=(100, 100, 100))

        cv2.putText(frame, "Presiona 'q' para salir", (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Control de Ventanas por Gestos", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Programa terminado")


if __name__ == "__main__":
    main()
