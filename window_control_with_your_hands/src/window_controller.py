import win32gui
import win32con
import win32api
import sys


class WindowController:
    def __init__(self):
        self.monitors = self.get_monitors()
        self.current_monitor_index = 0

    def get_monitors(self):
        return self.get_screen_monitors()

    def get_screen_monitors(self):
        import ctypes
        from ctypes import wintypes
        
        monitors = []
        
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = ctypes.cast(lprcMonitor, ctypes.POINTER(wintypes.RECT)).contents
            monitors.append({
                'left': r.left,
                'top': r.top,
                'right': r.right,
                'bottom': r.bottom,
                'width': r.right - r.left,
                'height': r.bottom - r.top
            })
            return 1
        
        MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.RECT), ctypes.c_void_p)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
        return monitors

    def get_active_window(self):
        return win32gui.GetForegroundWindow()

    def minimize_window(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        return False

    def maximize_window(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        return False

    def restore_window(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        return False

    def move_window_to_monitor(self, hwnd=None, target_monitor_index=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if not hwnd:
            return False

        screen_monitors = self.get_screen_monitors()

        if not screen_monitors:
            return False

        current_rect = win32gui.GetWindowRect(hwnd)

        current_monitor_idx = 0
        for i, mon in enumerate(screen_monitors):
            if current_rect[0] >= mon['left'] and current_rect[0] < mon['right']:
                current_monitor_idx = i
                break

        if target_monitor_index is None:
            target_monitor_index = (current_monitor_idx + 1) % len(screen_monitors)

        if target_monitor_index >= len(screen_monitors):
            target_monitor_index = 0

        target_monitor = screen_monitors[target_monitor_index]

        window_width = current_rect[2] - current_rect[0]
        window_height = current_rect[3] - current_rect[1]

        new_x = target_monitor['left'] + (target_monitor['width'] - window_width) // 2
        new_y = target_monitor['top'] + (target_monitor['height'] - window_height) // 2

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            new_x,
            new_y,
            window_width,
            window_height,
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )

        return True

    def snap_window_left(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if not hwnd:
            return False

        screen_monitors = self.get_screen_monitors()
        if not screen_monitors:
            return False

        for mon in screen_monitors:
            if win32gui.GetWindowRect(hwnd)[0] >= mon['left']:
                target = mon
                break
        else:
            target = screen_monitors[0]

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            target['left'],
            target['top'],
            target['width'] // 2,
            target['height'],
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )
        return True

    def snap_window_right(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_active_window()

        if not hwnd:
            return False

        screen_monitors = self.get_screen_monitors()
        if not screen_monitors:
            return False

        for mon in screen_monitors:
            if win32gui.GetWindowRect(hwnd)[0] >= mon['left']:
                target = mon
                break
        else:
            target = screen_monitors[0]

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            target['left'] + target['width'] // 2,
            target['top'],
            target['width'] // 2,
            target['height'],
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )
        return True
