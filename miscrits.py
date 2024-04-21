import PIL.ImageFilter
import easyocr.imgproc
import pyautogui
import time
import sys
import easyocr
import numpy
import PIL
import easyocr.character
import pygame

reader = easyocr.Reader(["en"], gpu=True, verbose=False)
pygame.init()

b = 0
start = time.time()
augh = pygame.mixer.Sound("augh.mp3")
on = pygame.mixer.Sound("on.mp3")
off = pygame.mixer.Sound("off.mp3")
dance = pygame.mixer.Sound("dance.mp3")

# SELECT WHICH ELEMENTS TO SEARCH IN ALTERNATION
# EXPLORE = ["a2_puddle.png", "a2_palm.png", "a2_stone.png", "a2_tree.png"]
# EXPLORE = ["eldertree.png", "eldershrub.png", "eldersunflower.png", "elderleafpile.png"]
EXPLORE = ["a4_blightbush.png", "a4_flowers.png"]
# EXPLORE = ["m0_cattail3.png", "m0_cattail2.png", "m0_cattail1.png", "m0_stone.png"]
# EXPLORE = ["m2_sofa.png", "m2_statue.png", "m2_brush1.png", "m2_cage.png"]
# EXPLORE = ["m2_statue2.png", "m2_table.png", "m2_chairL.png", "m2_chairR.png"]
# EXPLORE = ["m2_shelf.png", "m2_brush2.png", "m2_potions.png", "m2_woodcage.png"]
WEAKNESS = "nature.png"


def LXVI_locateCenterOnScreen(
    imagename: str,
    confidence: float = 0.999,
    region: tuple[int, int, int, int] | None = None,
) -> pyautogui.Point | None:
    try:
        return pyautogui.locateCenterOnScreen(
            imagename, confidence=confidence, region=region
        )
    except pyautogui.ImageNotFoundException:
        return None


def LXVI_readImage(region: tuple[int, int, int, int] | None = None):
    global reader

    img = pyautogui.screenshot(region=region)
    # old = img.copy()
    # img = img.convert('L')
    # img = img.filter(PIL.ImageFilter.DETAIL)
    # img = img.filter(PIL.ImageFilter.SMOOTH)
    # img = img.filter(PIL.ImageFilter.EDGE_ENHANCE)
    # img = img.filter(PIL.ImageFilter.DETAIL)

    read = reader.recognize(numpy.array(img))
    (_, text, _) = read[0]
    # old.save(f"{text}-b4.jpg")
    # img.save(f"{text}.jpg")
    return text


def click(
    imagename: str,
    confidence: float = 0.9,
    sleep: float = 0.2,
    duration: float = 0.2,
    region: tuple[int, int, int, int] | None = None,
) -> bool:
    toClick = LXVI_locateCenterOnScreen(imagename, confidence=confidence)

    if toClick is None:
        return False

    pyautogui.moveTo(toClick, duration=duration)
    pyautogui.leftClick()
    time.sleep(sleep)
    return True


def searchMode():
    global EXPLORE

    if not checkActive():
        print("Game not found during search mode, concluding process...")
        conclude()

    if LXVI_locateCenterOnScreen("expmultiplier.png", 0.8) is None:
        if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
            time.sleep(1)
            battleMode()
            summary()

    while LXVI_locateCenterOnScreen("expmultiplier.png", 0.85) is not None:
        SearchSuccess = False

        if (
            LXVI_locateCenterOnScreen(
                "gold.png", confidence=0.8, region=[0, 100, 1920, 980]
            )
            is not None
        ):
            cleanUp()

        for search in EXPLORE:
            if (toClick := LXVI_locateCenterOnScreen(search, confidence=0.8)) is None:
                time.sleep(1)
                continue

            SearchSuccess = True
            pyautogui.moveTo(toClick, duration=0.2)
            pyautogui.leftClick()
            time.sleep(4)

            if LXVI_locateCenterOnScreen("expmultiplier.png", 0.8) is None:
                if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
                    time.sleep(1)
                    battleMode()
                    summary()

        if not SearchSuccess:
            print("Elements not found, concluding process...")
            conclude()

    else:
        print("Minimized during search mode. Concluding process...")
        conclude()


def cleanUp():
    while (
        LXVI_locateCenterOnScreen(
            "gold.png", confidence=0.8, region=[0, 100, 1920, 980]
        )
        is not None
    ):
        click("gold.png", 0.8, region=[0, 100, 1920, 980])
        continue
    return


def battleMode():
    global WEAKNESS 
    global miscrit

    target = "Delfilio"

    if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            return
    
    click("miscripedia.png", 0.9, 0.555, 0)
    miscrit = LXVI_readImage([1367, 325, 245, 40])
    print(f"Wild {miscrit} wants to fight!")
    if miscrit == target:
        dance.play()
        augh.play()
    click("mpedia_exit.png", 0.8, 0.05, 0)
    click("mpedia_exit.png", 0.8, 0.05, 0)

    r = 0
    while True:
        if not checkActive():
            print("Minimized while in battle mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                return

        time.sleep(0.1)

        if not LXVI_locateCenterOnScreen(WEAKNESS, confidence=0.9):
            r = 1

        if miscrit == target:
            r = 0

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            if r != 0:
                # click("skillsetR.png", 0.75)

                pyautogui.moveTo(toClick, duration=0.1)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick, duration=0.1)

                # click("skillsetL.png", 0.75)
            else:
                click("skillsetR.png", 0.75)

                pyautogui.moveTo(toClick, duration=0.1)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                r = 1

                click("skillsetL.png", 0.75)

                pyautogui.moveTo(toClick, duration=0.1)


def summary():
    global b
    trainable = False

    if not checkActive():
        print("Minimized after battle, concluding process...")
        conclude()
    try:
        time.sleep(1.5)
        if LXVI_locateCenterOnScreen("trainable1.png", 0.675) is not None:
            trainable = True

        b += 1
        print(f"{b} Miscrits fought. Defeated: {miscrit}")
        click("closebtn.png", 0.85, 1)

        if trainable is True:
            click("train.png", 0.75, 0.5)
            train()
            return

    except Exception:
        return


def train():
    while LXVI_locateCenterOnScreen("trainable.png", 0.6) is not None:
        if not checkActive():
            print("Minimized while training Miscrits, concluding process...")
            conclude()

        click("trainable.png", 0.6, 0.2, 0.2)
        click("train2.png", 0.8, 0.5, 0.2)
        click("continuebtn.png", 0.9, 1, 0.2)

        click("continuebtn2.png", 0.75, 2, 0.2)
        click("continuebtn3.png", 0.75, 2, 0.2)
        click("skipbtn.png", 0.75, 2.5, 0.2)
        continue

    else:
        click("x.png", 0.8)
        return


def checkActive():
    if LXVI_locateCenterOnScreen("appname.png", 0.8, [0, 0, 1920, 100]) is not None:
        return True
    else:
        return False


def conclude():
    print(f"Ended process after {b} Miscrit battles.")
    print(f"Runtime: {time.time()-start}")
    print()
    time.sleep(1)
    off.play()
    sys.exit()


# time.sleep(2)
print()
if checkActive():
    on.play()
    searchMode()
else:
    print("Game not found on screen. Nothing happened.\n")
sys.exit()
