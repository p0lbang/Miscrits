import time
import pyautogui
from pyscreeze import Point

def LXVI_locateCenterOnScreen(
    imagename: str,
    confidence: float = 0.999,
    region: tuple[int, int, int, int] | None = None,
) -> Point | None:
    try:
        return pyautogui.locateCenterOnScreen(
            imagename, confidence=confidence, region=region
        )
    except pyautogui.ImageNotFoundException:
        return None
    
def LXVI_dragTo(
    image1: str,
    image2: str,
    confidence: float = 0.75,
    duration: float = 0.2,
    sleep: float = 0.5
):
    pyautogui.moveTo(LXVI_locateCenterOnScreen(image1, confidence))
    pyautogui.dragTo(LXVI_locateCenterOnScreen(image2, confidence), button='left', duration=duration)
    time.sleep(sleep)

def switchMiscrit():
    LXVI_dragTo("dot1.png", "dot2.png", duration=5)

switchMiscrit()