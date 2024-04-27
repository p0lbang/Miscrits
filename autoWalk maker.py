import pathlib
import pyautogui
import pyjson5
import time
from pynput import keyboard

CONFIG = {}
with open("mConfig.json5", "r") as file:
    CONFIG = pyjson5.loads(file.read())

imgNo = 1

def getClickArea():
    global imgNo
    (x,y) = pyautogui.position()
    img = pyautogui.screenshot(region=[x-100,y-100,200,200])
    img.save(pathlib.PurePath("walkMaker", f"af{imgNo:02d}.png"))
    
def on_release(key):
    global imgNo
    # print('{0} released'.format(key))
    print(f"\033[A{imgNo}                       ")
    if key == keyboard.Key.esc:
        # Stop listener
        return False
    elif key == keyboard.Key.enter:
        getClickArea()
        imgNo+=1
        time.sleep(2)
    elif key == keyboard.Key.right:
        imgNo+=1
    elif key == keyboard.Key.left:
        imgNo-=1
    elif key == keyboard.Key.space:
        try:
            (x,y) = pyautogui.locateCenterOnScreen(str(pathlib.PurePath("walkMaker", f"af{(imgNo-1):02d}.png")))
            pyautogui.leftClick(x,y)
        except:
            print(f"\033[A{imgNo-1} not found yet.")

# Collect events until released
print()
with keyboard.Listener(on_release=on_release) as listener:
    listener.join()
