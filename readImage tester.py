import pyautogui
import easyocr
import numpy
import easyocr.character
from pyscreeze import Point
# import PIL
# import PIL.ImageFilter

reader = easyocr.Reader(["en"], gpu=True, verbose=False)


def LXVI_readImage(region: tuple[int, int, int, int] | None = None):
    global reader, img

    img = pyautogui.screenshot(region=region)

    # old = img.copy()
    # img = img.convert("L")
    # img = img.filter(PIL.ImageFilter.DETAIL)
    # img = img.filter(PIL.ImageFilter.SMOOTH)
    # img = img.filter(PIL.ImageFilter.EDGE_ENHANCE)
    # img = img.filter(PIL.ImageFilter.DETAIL)

    read = reader.recognize(
        numpy.array(img),
        blocklist="-~()",
        # , allowlist='0123456789'
    )

    (_, text, _) = read[0]

    # old.save(f"{text}-b4.jpg")
    # img.save(f"{text}.jpg")
    img.save(f"testing.jpg")

    return text


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


def mpediaTest():
    miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)
    if isinstance(miscrits_lore, Point):
        miscrit = LXVI_readImage(
            region=(int(miscrits_lore.x) + -130, int(miscrits_lore.y) + 32, 238, 40)
        )
    print(f"\n{miscrit}\n")


def catchrateTest():
    catchButton = LXVI_locateCenterOnScreen("catchbtn.png", 0.75)
    if isinstance(catchButton, Point):
        chance = LXVI_readImage(
            region=(int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22)
        )
    print(chance)


catchrateTest()
