import pyautogui
import easyocr
import numpy
import easyocr.character

reader = easyocr.Reader(["en"], gpu=True, verbose=False)

def LXVI_readImage(region: tuple[int, int, int, int] | None = None):
    global reader, img

    img = pyautogui.screenshot(region=region)

    read = reader.recognize(numpy.array(img))
    (_, text, _) = read[0]
    img.save(f"{text}.jpg")
    return text

def mpediaTest():
    miscrit = LXVI_readImage([1375, 330, 238, 38])
    print(f"\n{miscrit}\n")

mpediaTest()