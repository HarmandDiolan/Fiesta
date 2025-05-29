import cv2
import numpy as np
import mss
import pyautogui
import time
import ctypes
import datetime

# Load templates
template1 = cv2.imread("img2.png", cv2.IMREAD_COLOR)
template2 = cv2.imread("img3.PNG", cv2.IMREAD_COLOR)
reward_template = cv2.imread("reward.PNG", cv2.IMREAD_COLOR)
yellow_template = cv2.imread("yellow.PNG", cv2.IMREAD_COLOR)

if template1 is None or template2 is None or reward_template is None or yellow_template is None:
    raise FileNotFoundError("One or more templates not found")

# Store templates and their sizes
templates = []
for tpl in [template1, template2]:
    tH, tW = tpl.shape[:2]
    templates.append((tpl, tH, tW))

reward_h, reward_w = reward_template.shape[:2]
yellow_h, yellow_w = yellow_template.shape[:2]  # <<< yellow.PNG size

def take_screenshot_color():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        return img

def multi_scale_color_match(screen, template, tW, tH, scales=np.linspace(0.8, 1.2, 10), threshold=0.52):
    found = None
    for scale in scales:
        resized = cv2.resize(template, (int(tW * scale), int(tH * scale)))
        rH, rW = resized.shape[:2]
        if screen.shape[0] < rH or screen.shape[1] < rW:
            continue

        result = np.zeros((screen.shape[0] - rH + 1, screen.shape[1] - rW + 1))
        for i in range(3):
            result += cv2.matchTemplate(screen[:, :, i], resized[:, :, i], cv2.TM_CCOEFF_NORMED)
        result /= 3.0

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f"Scale {scale:.2f} max match value: {max_val:.3f}")
        if max_val >= threshold:
            found = (max_val, max_loc, rW, rH)
            break
    return found

def press_mouse_button_4():
    MOUSEEVENTF_XDOWN = 0x0080
    MOUSEEVENTF_XUP = 0x0100
    XBUTTON1 = 0x0001

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON1, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON1, 0)

def click_on_template(template, tW, tH, threshold=0.52):
    screen = take_screenshot_color()
    match = multi_scale_color_match(screen, template, tW, tH, threshold=threshold)
    if match:
        _, (x, y), w, h = match
        center_x = x + w // 2
        center_y = y + h // 2

        pyautogui.moveTo(center_x, center_y)
        ctypes.windll.user32.SetCursorPos(center_x, center_y)
        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP

        print(f"Clicked on template at ({center_x}, {center_y}) using mouse 1")
        return True
    return False

def click_on_reward():
    return click_on_template(reward_template, reward_w, reward_h, threshold=0.52)

# Main loop
while True:
    screenshot = take_screenshot_color()
    detected_any = False

    for idx, (template, tH, tW) in enumerate(templates):
        match = multi_scale_color_match(screenshot, template, tW, tH, threshold=0.52)
        if match:
            max_val, max_loc, w, h = match
            detected_any = True
            print(f"✅ Detected template {idx+1} with confidence {max_val:.2f} at {max_loc}")

            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 3)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.png"
            cv2.imwrite(filename, screenshot)
            print(f"💾 Screenshot saved as {filename}")

            # Simulate Mouse Button 4
            press_mouse_button_4()
            print("🖱️ Pressed mouse button 4")

            time.sleep(1)

            if click_on_reward():
                time.sleep(0.5)

                while True:
                    clicked = click_on_template(yellow_template, yellow_w, yellow_h, threshold=0.52)
                    if clicked:
                        print("🟡 Clicked on yellow.PNG")
                        time.sleep(0.5)
                    else:
                        print("❌ yellow.PNG not detected anymore, stopping clicks")
                        break

            break  # Only process one match per loop

    if not detected_any:
        print("❌ No templates detected")

    time.sleep(1)