import easyocr.imgproc
import pyautogui
import time
import sys
import easyocr
import numpy
import easyocr.character
import pygame
from pyscreeze import Point

reader = easyocr.Reader(["en"], gpu=False, verbose=False)
pygame.init()

b = 0
start = time.time()
augh = pygame.mixer.Sound("augh.mp3")
on = pygame.mixer.Sound("on.mp3")
off = pygame.mixer.Sound("off.mp3")
dance = pygame.mixer.Sound("dance.mp3")
# SELECT WHICH ELEMENTS TO SEARCH IN ALTERNATION
# EXPLORE = ["a1_cattail_02.png","a1_cattail_01.png","a1_cattail_03.png",]
# EXPLORE = ["a2_stump.png","a2_smallrock.png","a2_bigrock.png",]
# EXPLORE = ["a3_smallrock.png","a3_deadtree.png","a3_bigrock.png",]
# EXPLORE = ["a2_puddle.png", "a2_palm.png", "a2_stone.png", "a2_tree.png"]
# EXPLORE = ["eldertree.png", "eldershrub.png", "eldersunflower.png", "elderleafpile.png"]
# EXPLORE = ["a4_bush.png", "a4_cattail2.png", "a4_tree.png" "a4_empty.png"]
# EXPLORE = ["a4_blightbush.png", "a4_blightbush2.png", "a4_flowers.png"]
# EXPLORE = ["m0_cattail3.png", "m0_cattail2.png", "m0_cattail1.png", "m0_stone.png"]
# EXPLORE = ["m2_sofa.png", "m2_statue.png", "m2_brush1.png", "m2_cage.png"]
EXPLORE = ["m2_statue2.png", "m2_table.png", "m2_chairL.png", "m2_chairR.png"]
# EXPLORE = ["m2_shelf.png", "m2_brush2.png", "m2_potions.png", "m2_woodcage.png"]
# EXPLORE = ["m2_statue2.png", "m2_table.png", "m2_chairL.png"]

APPNAMEPNG = "appname.png"

if sys.platform.startswith('linux'):
    APPNAMEPNG = "appname_linux.png"


#####[    C O N F I G    ]#####
autoSearch = True  # just True or False
autoTrain = True  #
WEAKNESS = "nature.png"  # choose element that is strong against main miscrit
target = "Nanaslug"  # miscrit name without space (pray for accuracy)
huntType = "battle"  # "battle" or "escape" the miscrits that are not the target
checkForTarget = True
SoundsEnabled = False

def playSound(sound: pygame.mixer.Sound) -> None:
    global SoundsEnabled
    if SoundsEnabled:
        sound.play()

def LXVI_locateCenterOnScreen(
    imagename: str,
    confidence: float = 0.999,
    region: tuple[int, int, int, int] | None = None,
) -> Point | None:
    try:
        # pyautogui.screenshot("1_locatecenter.jpg",region=region)
        return pyautogui.locateCenterOnScreen(
            imagename, confidence=confidence, region=region
        )
    except pyautogui.ImageNotFoundException:
        return None


def LXVI_readImage(region: tuple[int, int, int, int] | None = None):
    global reader

    img = pyautogui.screenshot(region=region)

    read = reader.recognize(numpy.array(img))
    (_, text, _) = read[0]
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
                    if huntType == "hunt":
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
    global WEAKNESS, miscrit, target, checkForTarget

    miscrit = "wild miscrit"
    action = 1
    loopcount = 0
    battle_start = time.time()

    # check until miscripedia is shown
    while LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
        pass
    
    if LXVI_locateCenterOnScreen(WEAKNESS, confidence=0.9) is not None:
        action = 0
    
    if checkForTarget:
        click("miscripedia.png", 0.9, 0.555, 0)
        miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", confidence=0.7)
        
        if isinstance(miscrits_lore, Point):
            miscrit = LXVI_readImage(region=(
                int(miscrits_lore.x) + -140, 
                int(miscrits_lore.y) + 35, 
                238, 38))

        print(f"{miscrit} wants to fight!")
        click("mpedia_exit.png", 0.8, 0, 0)
        click("mpedia_exit.png", 0.8, 0, 0)

        if miscrit == target:
            print(
                f"\033[ATarget miscrit {target} found! Ending process for catch."
            )
            playSound(augh)
            time.sleep(10)
            conclude()

    # check until run is shown. which means ready to attack
    while (toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)) is None:
        pass

    if not checkActive():
        print("Minimized while in battle mode, concluding process...")
        conclude()
    
    while True:
        if action > 0:
            pyautogui.moveTo(toClick)
            pyautogui.moveRel(-45 + 160 * 1, 80)
            pyautogui.leftClick()
            pyautogui.moveTo(toClick)
        else:
            click("skillsetR.png", 0.75)
            pyautogui.moveTo(toClick)
            pyautogui.moveRel(-45 + 160 * 1, 80)
            pyautogui.leftClick()
            click("skillsetL.png", 0.75)
            pyautogui.moveTo(toClick)
            action = 1
        
        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            print(
                    f"\033[A{miscrit} was defeated. Time: {round(time.time()-battle_start, 3)}s"
                )
            print(f"loopcount: {loopcount}")
            return
        
        if not checkActive():
            print(f"\033[AMinimized while battling {miscrit}, concluding process...")
            conclude()
        
        loopcount+= 1
        

def escapeMode():
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
        playSound(dance)
        playSound(augh)
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
                return

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            if r == 0:
                pyautogui.moveTo(toClick)
                print(f"\033[AEscaped from {miscrit}.")
                pyautogui.leftClick()
            else:
                if miscrit == target:
                    print(
                        f"\033[ATarget miscrit {target} found! Ending process for catch."
                    )
                    time.sleep(10)
                    playSound(augh)
                    conclude()

                click("skillsetR.png", 0.75, 0, 0)

                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 80)
                pyautogui.leftClick()
                r = 1

                click("skillsetL.png", 0.75, 0, 0)

                pyautogui.moveTo(toClick)


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
    global APPNAMEPNG
    
    if LXVI_locateCenterOnScreen(APPNAMEPNG, 0.8, [0, 0, 1920, 100]) is not None:
        return True
    else:
        return False


def conclude():
    print(f"\nEnded process after {b} Miscrits encountered.")
    print(f"Runtime: {time.time()-start}\n")
    playSound(off)
    time.sleep(1)
    sys.exit()


time.sleep(2)
playSound(on)
time.sleep(1)
print()
if checkActive():
    searchMode()
else:
    print("Game not found on screen. Nothing happened.\n")
playSound(off)
time.sleep(1)