# import PIL.ImageFilter
import easyocr.imgproc
import pyautogui
import time
import sys
import easyocr
import numpy
# import PIL
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
# EXPLORE = ["a4_bush.png", "a4_cattail2.png", "a4_empty.png"]
EXPLORE = ["a4_blightbush.png", "a4_blightbush2.png", "a4_flowers.png"]
# EXPLORE = ["m0_cattail3.png", "m0_cattail2.png", "m0_cattail1.png", "m0_stone.png"]
# EXPLORE = ["m2_sofa.png", "m2_statue.png", "m2_brush1.png", "m2_cage.png"]
# EXPLORE = ["m2_statue2.png", "m2_table.png", "m2_chairL.png", "m2_chairR.png"]
# EXPLORE = ["m2_shelf.png", "m2_brush2.png", "m2_potions.png", "m2_woodcage.png"]

#####[    C O N F I G    ]#####
autoSearch = True             # just True or False
encounterType = "battle"      # "battle" or "hunt"
WEAKNESS = "nature.png"       # choose element that is strong against main miscrit
target = "DarkShellbee"       # miscrit name without space (pray for accuracy)


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
    # img = img.convert("L")
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
    global EXPLORE, autoSearch

    if not checkActive():
        print("Game not found during search mode, concluding process...")
        conclude()

    if LXVI_locateCenterOnScreen("expmultiplier.png", 0.8) is None:
        if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
            time.sleep(1)
            if encounterType == "hunt": huntMode()
            else: battleMode()
            summary()
        elif LXVI_locateCenterOnScreen("closebtn.png", 0.8) is not None:
            click("closebtn.png", 0.8, 1)

    while LXVI_locateCenterOnScreen("expmultiplier.png", 0.85) is not None:
        if (LXVI_locateCenterOnScreen("gold.png", confidence=0.8, region=[0, 100, 1920, 980]) is not None
            ) or (LXVI_locateCenterOnScreen("potion1.png", confidence=0.65) is not None):
            cleanUp()

        if autoSearch:
            SearchSuccess = False
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
                        if encounterType == "hunt": huntMode()
                        else: battleMode()
                        summary()

            if not SearchSuccess:
                print("Elements not found, concluding process...")
                conclude()
        else:
            time.sleep(0.5)
            continue

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
    while LXVI_locateCenterOnScreen("potion1.png", confidence=0.65) is not None:
        click("potion1.png", 0.65)
        continue
    return


def battleMode():
    global WEAKNESS, miscrit, target
    r = 0

    if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            return

    click("miscripedia.png", 0.9, 0.555, 0)
    miscrit = LXVI_readImage([1375, 330, 238, 38])
    print(f"Wild {miscrit} wants to fight!")
    click("mpedia_exit.png", 0.8, 0, 0)
    click("mpedia_exit.png", 0.8, 0, 0)

    battle_start = time.time()

    while True:
        if not checkActive():
            print(f"Minimized while battling {miscrit}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                print(f"    Wild {miscrit} was defeated.")
                print(f"    Time elapsed: {time.time()-battle_start}")
                return

        if not LXVI_locateCenterOnScreen(WEAKNESS, confidence=0.9):
            r = 1

        if miscrit==target:
            r = 0
            dance.play()

        if (toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)) is not None:
            if r != 0:
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick)
            else:
                if miscrit == target:
                    print(f"Target miscrit {target} found! Ending process for catch.")
                    time.sleep(10)
                    augh.play()
                    conclude()
                click("skillsetR.png", 0.75)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                r = 1
                click("skillsetL.png", 0.75)
                pyautogui.moveTo(toClick)


def huntMode():
    global miscrit, target
    r = 0

    if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            return

    click("miscripedia.png", 0.9, 0.555, 0)
    miscrit = LXVI_readImage([1370, 330, 238, 38])
    if miscrit == target:
        r = 1
        print(f"{target} found!!!")
        dance.play()
        augh.play()
    print(f"Wild {miscrit} showed up.")
    click("mpedia_exit.png", 0.8, 0, 0)
    click("mpedia_exit.png", 0.8, 0, 0)

    while True:
        if not checkActive():
            print(f"Minimized while hunting for {target}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                return

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            if r == 0:
                pyautogui.moveTo(toClick)
                print(f"    Escaped from {miscrit}.")
                pyautogui.leftClick()
            else:
                dance.play()
                time.sleep(20)
                augh.play()

                click("skillsetR.png", 0.75)

                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                r = 1

                click("skillsetL.png", 0.75)

                pyautogui.moveTo(toClick)


def summary():
    global b
    trainable = False

    if not checkActive():
        print("Minimized after Miscrit encounter, concluding process...")
        conclude()
    try:
        time.sleep(1.5)
        if LXVI_locateCenterOnScreen("trainable1.png", 0.675) is not None:
            trainable = True

        b += 1
        click("closebtn.png", 0.8, 1, 0)

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
    print(f"Ended process after {b} Miscrits encountered.")
    print(f"Runtime: {time.time()-start}\n")
    off.play()
    time.sleep(1)
    sys.exit()


# time.sleep(2)
on.play()
time.sleep(1)
print()
if checkActive():
    searchMode()
else:
    print("Game not found on screen. Nothing happened.\n")
off.play()
time.sleep(1)
sys.exit()
