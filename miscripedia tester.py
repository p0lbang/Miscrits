import pyautogui
import easyocr
import numpy
import easyocr.character
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

    read = reader.recognize(numpy.array(img))
    (_, text, _) = read[0]

    # old.save(f"{text}-b4.jpg")
    # img.save(f"{text}.jpg")
    img.save(f"{text}.jpg")

    return text

def mpediaTest():
    miscrit = LXVI_readImage([1375, 325, 238, 40])
    print(f"\n{miscrit}\n")

mpediaTest()