import ctypes
import time

def press_mouse_button_4():
    MOUSEEVENTF_XDOWN = 0x0080
    MOUSEEVENTF_XUP = 0x0100
    XBUTTON1 = 0x0001

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON1, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON1, 0)

time.sleep(2)
press_mouse_button_4()
print("Mouse button 4 pressed")
