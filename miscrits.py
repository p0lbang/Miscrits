#----[    C O N F I G    ]----#
alerts = True  #..............# just True or False
autoSearch = True  #..........# 
autoTrain = True  #...........#
huntType = "battle"  #........# "battle" or "escape" the miscrits that are not the target
autoCatch = True  #...........# try to catch miscrit if catch rate is greater than 
catchable = 90  #.............# this catch percentage
WEAKNESS = "nature.png"  #....# choose element that is strong against main miscrit
target = "BlightedKiloray"  #.# miscrit name without space (pray for accuracy)
targetBypass = False #........# set to True to make everyone a target for capture

# SELECT WHICH ELEMENTS TO SEARCH IN ALTERNATION
EXPLORE = ["a2_puddle.png", "a2_palm.png", "a2_stone.png", "a2_tree.png"]
# EXPLORE = ["eldertree.png", "eldershrub.png", "eldersunflower.png", "elderleafpile.png"]
# EXPLORE = ["a4_bush.png", "a4_cattail2.png", "a4_tree.png" "a4_empty.png"]
# EXPLORE = ["a4_blightbush.png", "a4_blightbush2.png", "a4_flowers.png"]
# EXPLORE = ["m0_cattail3.png", "m0_cattail2.png", "m0_cattail1.png", "m0_stone.png"]
# EXPLORE = ["m2_sofa.png", "m2_statue.png", "m2_brush1.png", "m2_cage.png"]
# EXPLORE = ["m2_shelf.png", "m2_brush2.png", "m2_potions.png", "m2_woodcage.png"]
# EXPLORE = ["m2_statue2.png", "m2_chairL.png"]

import easyocr.imgproc
import pyautogui
import time
import sys
import easyocr
import numpy
import easyocr.character
if alerts: import pygame

reader = easyocr.Reader(["en"], gpu=True, verbose=False)
start = time.time()
b = 0
caught = False

if alerts:
    pygame.init()
    augh = pygame.mixer.Sound("augh.mp3")
    on = pygame.mixer.Sound("on.mp3")
    off = pygame.mixer.Sound("off.mp3")
    dance = pygame.mixer.Sound("dance.mp3")


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


def LXVI_readImage(region: tuple[int, int, int, int] | None = None, numerical: bool = False):
    global reader

    img = pyautogui.screenshot(region=region)
    
    if numerical:
        read = reader.recognize(numpy.array(img), allowlist='0123456789')
    else:
        read = reader.recognize(numpy.array(img))
    (_, text, _) = read[0]
    img.save(f"testing.jpg")
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

    while True:
        if not checkActive():
            print("Game not found during search mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
            time.sleep(1)
            if huntType == "battle":
                battleMode()
            else:
                escapeMode()
            summary()
        elif LXVI_locateCenterOnScreen("closebtn.png", 0.8) is not None:
            click("closebtn.png", 0.8, 1, 0)

        if (
            LXVI_locateCenterOnScreen(
                "gold.png", confidence=0.8, region=[0, 100, 1920, 980]
            )
            is not None
        ) or (LXVI_locateCenterOnScreen("potion1.png", confidence=0.65) is not None):
            cleanUp()

        if autoSearch:
            SearchSuccess = False
            for search in EXPLORE:
                if (
                    toClick := LXVI_locateCenterOnScreen(search, confidence=0.8)
                ) is None:
                    time.sleep(1)
                    continue

                SearchSuccess = True
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(4)

                if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
                    time.sleep(1)
                    if huntType == "escape":
                        escapeMode()
                    else:
                        battleMode()
                    summary()

            if not SearchSuccess:
                print("Elements not found, concluding process...")
                conclude()
        else:
            time.sleep(0.5)
            continue


def cleanUp():
    while (
        LXVI_locateCenterOnScreen(
            "gold.png", confidence=0.8, region=[0, 100, 1920, 980]
        )
        is not None
    ):
        click("gold.png", 0.8, 0, 0, [0, 100, 1920, 980])
    while LXVI_locateCenterOnScreen("potion1.png", confidence=0.65) is not None:
        click("potion1.png", 0.65, 0, 0)


def battleMode():
    global miscrit, caught
    r = 0

    if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            return

    click("miscripedia.png", 0.8, 0.555, 0)
    miscrit = LXVI_readImage([1375, 330, 238, 38])
    print(f"{miscrit} wants to fight!")
    click("mpedia_exit.png", 0.8, 0, 0)
    click("mpedia_exit.png", 0.8, 0, 0)

    battle_start = time.time()

    while True:
        if not checkActive():
            print(f"\033[AMinimized while battling {miscrit}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                if caught:
                    print(f"\033[A{miscrit} has been caught. Time: {round(time.time()-battle_start, 3)}s")
                    caught = False
                else:
                    print(f"\033[A{miscrit} was defeated. Time: {round(time.time()-battle_start, 3)}s")    
                return

        if not LXVI_locateCenterOnScreen(WEAKNESS, confidence=0.9):
            r = 1

        if miscrit == target or targetBypass:
            r = 0
            if alerts: dance.play()

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            if r != 0:
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick)
            else:
                if miscrit == target or targetBypass:
                    if alerts: augh.play()
                    if autoCatch:
                        catchMode()
                    else:
                        print(
                            f"\033[ATarget miscrit {miscrit} found! Ending process for manual catch."
                        )
                        time.sleep(10)
                        if alerts: augh.play()
                        conclude()
                else:
                    click("skillsetR.png", 0.75, 0, 0)
                    pyautogui.moveTo(toClick)
                    pyautogui.moveRel(-45 + 160 * 1, 80)
                    pyautogui.leftClick()
                    r = 1
                    click("skillsetL.png", 0.75, 0, 0)



def escapeMode():
    global miscrit, caught
    r = 0

    if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            return

    click("miscripedia.png", 0.9, 0.555, 0)
    miscrit = LXVI_readImage([1370, 330, 238, 38])
    if miscrit == target or targetBypass:
        r = 1
        print(f"{miscrit} found!!!")
        if alerts: 
            dance.play()
            augh.play()
    else:
        print(f"{miscrit} showed up.")
    click("mpedia_exit.png", 0.8, 0, 0)
    click("mpedia_exit.png", 0.8, 0, 0)

    while True:
        if not checkActive():
            print(f"\033[AMinimized while hunting for {target}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                if caught:
                    print(f"\033[AHunted and caught {miscrit}.")
                    caught = False
                return

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            if r == 0:
                pyautogui.moveTo(toClick)
                print(f"\033[ASuccessfully escaped from {miscrit}.")
                pyautogui.leftClick()
            else:
                if miscrit == target or targetBypass:
                    if alerts: augh.play()
                    if autoCatch:
                        catchMode()
                    else:
                        print(
                            f"\033[ATarget miscrit {miscrit} found! Ending process for manual catch."
                        )
                        time.sleep(10)
                        conclude()


def catchMode():
    global miscrit, caught
    c = 0
    caught = False

    while not caught:
        if not checkActive():
            print(f"\033[AMinimized while trying to catch {target}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                return
            
        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            chance = LXVI_readImage([1328, 158, 18, 22], True)
            time.sleep(0.1)
            if int(chance) >= catchable:
                c = 3
            if c == 0:
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                c = 1
            elif c == 1:
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 80)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                c = 2
            elif c == 2:
                click("skillsetR.png", 0.75, 0, 0)
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 80)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                click("skillsetL.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
            elif c == 3:
                click("catchbtn.png", 0.75, 6, 0)
                if LXVI_locateCenterOnScreen("catchSuccess.png", 0.9) is not None:
                    caught = True
                else:
                    c = 4
            elif c == 4:
                pyautogui.moveTo(toClick)
                print(f"\033[AFailed to catch {miscrit}. Time to kill I guess.")
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick)
    click("catchSkip.png", 0.9, 2, 0)


def summary():
    global b, autoTrain
    trainable = False

    if not checkActive():
        print("Minimized after Miscrit encounter, concluding process...")
        conclude()
    try:
        time.sleep(1.5)
        if LXVI_locateCenterOnScreen("trainable1.png", 0.675) is not None:
            trainable = autoTrain

        b += 1
        click("closebtn.png", 0.8, 1, 0)

        if autoCatch:
            time.sleep(1.5)
            click("skipbtn.png", 0.75, 1.5, 0.1)

        if trainable is True:
            click("train.png", 0.75, 0.5, 0)
            train()
            return

    except Exception:
        return


def train():
    while LXVI_locateCenterOnScreen("trainable.png", 0.6) is not None:
        if not checkActive():
            print("Minimized while training Miscrits, concluding process...")
            conclude()

        click("trainable.png", 0.6, 0.2, 0.1)
        click("train2.png", 0.8, 0.5, 0.1)
        click("continuebtn.png", 0.9, 1, 0.1)

        click("continuebtn2.png", 0.75, 2, 0.1)
        click("continuebtn3.png", 0.75, 2, 0.1)
        click("skipbtn.png", 0.75, 2.5, 0.1)
        continue

    else:
        click("x.png", 0.8, 0.2, 0)
        return


def checkActive():
    if LXVI_locateCenterOnScreen("appname.png", 0.8, [0, 0, 1920, 100]) is not None:
        return True
    else:
        return False


def conclude():
    print(f"\nEnded process after {b} Miscrits encountered.")
    print(f"Runtime: {time.time()-start}\n")
    if alerts: off.play()
    time.sleep(1)
    sys.exit()


if alerts: on.play()
time.sleep(1)
print()
if checkActive():
    searchMode()
else:
    print("Game not found on screen. Nothing happened.\n")
if alerts: off.play()
time.sleep(1)
sys.exit()