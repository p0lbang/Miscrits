import pyautogui
import easyocr
import numpy
import time
import easyocr.character
from pyscreeze import Point
# import PIL
# import PIL.ImageFilter

reader = easyocr.Reader(["en"], gpu=True, verbose=False)


def LXVI_readImage(region: tuple[int, int, int, int] | None = None):
    global reader, img

    img = pyautogui.screenshot(region=region)

    # old = img.copy()
    img = img.convert("L")
    # img = img.filter(PIL.ImageFilter.DETAIL)
    # img = img.filter(PIL.ImageFilter.SMOOTH)
    # img = img.filter(PIL.ImageFilter.EDGE_ENHANCE)
    # img = img.filter(PIL.ImageFilter.DETAIL)

    read = reader.recognize(
        numpy.array(img),
        blocklist="-~() 1234567890",
        # allowlist="0123456789",
    )

    (_, text, _) = read[0]

    # old.save(f"{text}-b4.jpg")
    # img.save(f"{text}.jpg")
    img.save(f"testing.jpg")

    return text


def LXVI_getImage(region: tuple[int, int, int, int] | None = None):
    global reader, img

    img = pyautogui.screenshot(region=region)
    img.save(f"testing.png")


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


def click(
    imagename: str,
    confidence: float = 0.9,
    sleep: float = 0.2,
    duration: float = 0.1,
    region: tuple[int, int, int, int] | None = None,
) -> bool:
    toClick = LXVI_locateCenterOnScreen(imagename, confidence=confidence)

    if toClick is None:
        return False

    pyautogui.moveTo(toClick, duration=duration)
    pyautogui.leftClick()
    time.sleep(sleep)
    return True


def getMiscritName():
    miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)
    if isinstance(miscrits_lore, Point):
        miscrit = LXVI_readImage(
            region=(int(miscrits_lore.x) + -130, int(miscrits_lore.y) + 32, 238, 40)
        )
    print(f"\n{miscrit}\n")


def getMiscritRarity():
    rarDict = {
        "com": "Common",
        "rar": "Rare",
        "epi": "Epic",
        "exo": "Exotic",
        "lag": "Legendary",
    }
    miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)
    if isinstance(miscrits_lore, Point):
        rarity = LXVI_readImage(
            [int(miscrits_lore.x) + -86, int(miscrits_lore.y) + 116, 60, 25]
        )
        rarity = rarity[:3].lower()
    print(rarDict[rarity])


def getTeamLevelA():
    myMiscrits = LXVI_locateCenterOnScreen("myMiscrits.png", 0.9)
    if isinstance(myMiscrits, Point):
        levelA = Point(x=myMiscrits.x - 8, y=myMiscrits.y + 73)
        levelB = int(LXVI_readImage([int(levelA.x), int(levelA.y) + 50, 15, 15]))
        levelC = int(LXVI_readImage([int(levelA.x), int(levelA.y) + 100, 15, 15]))
        levelD = int(LXVI_readImage([int(levelA.x), int(levelA.y) + 150, 15, 15]))
    print(f"{levelB} {levelC} {levelD}")
    return [int(levelB), int(levelC), int(levelD)]


# -665, 315 | 170, 82
# -695, 283
def getTeamLevelB():
    exit = LXVI_locateCenterOnScreen("x.png", 0.9)
    pointD = Point(x=int(exit.x) - 90, y=int(exit.y) + 200)
    offset = Point(-665, 315)
    point0 = Point(exit.x + offset.x, exit.y + offset.y)
    pointZ = Point(point0.x - 30, point0.y - 30)
    offset = Point(172, 84)

    page = 0
    number = 1
    lastMiscrit = False
    while not lastMiscrit:
        for row in range(3):
            for column in range(4):
                pointN = Point(pointZ.x + column * offset.x, pointZ.y + row * offset.y)
                pointM = Point(point0.x + column * offset.x, point0.y + row * offset.y)
                if (
                    LXVI_locateCenterOnScreen(
                        "teamslotEmpty.png", 0.8, [pointN.x, pointN.y, 150, 65]
                    )
                    is None
                ):
                    level = int(LXVI_readImage([int(pointM.x), int(pointM.y), 16, 14]))
                    print(f"{number:02d}: {level:02d}", end="  |  ")
                    number += 1
                else:
                    lastMiscrit = True
                    break
            print()
            if lastMiscrit:
                break
        print()
        page += 1
        click("teamR.png", 0.8, 0, 0)
    return


def getCatchChance():
    catchButton = LXVI_locateCenterOnScreen("catchbtn.png", 0.75)
    if isinstance(catchButton, Point):
        chance = LXVI_readImage(
            region=(int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22)
        )
    print(chance)


def getMyMiscritProfile():
    mPedia = LXVI_locateCenterOnScreen("UI_Images\\miscripedia.png", 0.8)
    if isinstance(mPedia, Point):
        profile = LXVI_getImage(
            region=(int(mPedia.x) - 289, int(mPedia.y) - 31, 40, 40)
        )


getMiscritName()
