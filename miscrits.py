# -------[    C O N F I G    ]-------#
sounds = True  # ....................# just True or False
autoSearch = True  # ................#
searchInterval = 4  # ...............# interval for clicking between searches 
autoTrain = True  # .................#
miscritCheck = True  # ..............# set to True to get miscrit's name
huntType = "battle"  # ..............# "battle" or "escape" the miscrits that are not the target
autoCatch = True  # .................# try to catch miscrit if catch rate is greater than
catchable = 85  # ...................# this catch percentage
catchStandard = 28  # ...............# initial catch percentage to capture [msx is 42]
WEAKNESS = "nature.png"  # ..........# choose element that is strong against main miscrit
targetAll = True  # ................# set to True to make everyone a target for capture
targets = ["BlightedFiender"]  # ....# miscrit names without space (pray for accuracy)
searchSeq = ["a3_blight", "a3_sun3", "a3_magic", "a3_fuchsia"]

import sys
import time
import numpy
import pyautogui
import easyocr
import easyocr.imgproc
import easyocr.character
import pygame
from colorama import Fore
from pyscreeze import Point

reader = easyocr.Reader(["en"], gpu=True, verbose=False)
pygame.init()

b = 0
start = time.time()
rizz = pygame.mixer.Sound("rizz.mp3")
on = pygame.mixer.Sound("on.mp3")
off = pygame.mixer.Sound("off.mp3")
pluck = pygame.mixer.Sound("pluck.mp3")
bend = pygame.mixer.Sound("bend.mp3")

APPNAMEPNG = "appname.png"
if sys.platform.startswith("linux"):
    APPNAMEPNG = "appname_linux.png"

for s, search in enumerate(searchSeq):
    searchSeq[s] =".\\imgSources\\" + search + ".png"

def checkActive():
    if LXVI_locateCenterOnScreen(APPNAMEPNG, 0.8, [0, 0, 1920, 100]) is not None:
        return True
    else:
        return False


def playSound(sound: pygame.mixer.Sound) -> None:
    if sounds:
        sound.play()


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


def LXVI_readImage(
    region: tuple[int, int, int, int] | None = None, numerical: bool = False
):
    img = pyautogui.screenshot(region=region)

    if numerical:
        read = reader.recognize(
            numpy.array(img), allowlist="0123456789", blocklist="-~()"
        )
    else:
        read = reader.recognize(numpy.array(img), blocklist="-~()")
    (_, text, _) = read[0]

    # img.save(f"testing.jpg")
    return text


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


def searchMode():
    while True:
        if not checkActive():
            print("Game not found during search mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
            time.sleep(1)
            encounterMode()
            summary()
        elif LXVI_locateCenterOnScreen("closebtn.png", 0.8) is not None:
            click("closebtn.png", 0.8, 1, 0)

        cleanUp()

        if autoSearch:
            SearchSuccess = False
            for search in searchSeq:
                if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
                    encounterMode()
                    summary()
                
                if (
                    toClick := LXVI_locateCenterOnScreen(search, confidence=0.8)
                ) is None:
                    time.sleep(1)
                    continue

                SearchSuccess = True
                pyautogui.moveTo(toClick, duration=0.1)
                pyautogui.leftClick()
                time.sleep(searchInterval)


            if not SearchSuccess:
                print("Elements not found, concluding process...")
                conclude()
        else:
            time.sleep(0.5)
            continue


def encounterMode():
    global miscrit

    miscrit = "WILD MISCRIT"
    action = 1
    battle_start = time.time()

    while LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is None:
        pass

    if LXVI_locateCenterOnScreen(WEAKNESS, 0.9) is not None:
        action = 0

    if miscritCheck:
        click("miscripedia.png", 0.8, 0.555, 0)
        miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)

        if isinstance(miscrits_lore, Point):
            miscrit = LXVI_readImage(
                region=(int(miscrits_lore.x) + -130, int(miscrits_lore.y) + 33, 238, 40)
            )

        print(f"{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} wants to fight.")
        click("mpedia_exit.png", 0.8, 0, 0)
        click("mpedia_exit.png", 0.8, 0, 0)

        toCatch = False
        catchButton = LXVI_locateCenterOnScreen("catchbtn.png", 0.75)

        if miscrit in targets or targetAll:
            print(
                f"\033[A{Fore.WHITE}Target miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} found!{Fore.LIGHTBLACK_EX}"
            )
            playSound(rizz)

            if autoCatch:
                time.sleep(1)
                if isinstance(catchButton, Point):
                    toCatch = int(LXVI_readImage([int(catchButton.x) - 17,int(catchButton.y) + 13, 18, 22], True)) <= catchStandard
                if toCatch or miscrit in targets:
                    playSound(pluck)
                    catchMode()
                    return
                else:
                    print(
                        f"\033[A{Fore.WHITE}This {Fore.YELLOW}{miscrit}{Fore.WHITE} is trash. -p0lbang{Fore.LIGHTBLACK_EX}"
                    )
            else:
                print("Ending process for manual catch.")
                conclude()
    else:
        print(f"{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} wants to fight.")

    while (toClick := LXVI_locateCenterOnScreen("run.png", 0.99)) is None:
        pass

    if not checkActive():
        print(f"Minimized while in encounter mode, concluding process...")
        conclude()

    if huntType != "battle":
        pyautogui.moveTo(toClick)
        print(
            f"\033[ASuccessfully escaped from {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}."
        )
        pyautogui.leftClick()
    else:
        toClick = (toClick.x + 115, toClick.y + 80)


    while True:
        if action > 0:
            pyautogui.moveTo(toClick)
            pyautogui.leftClick()
        else:
            click("skillsetR.png", 0.75, 0, 0)
            pyautogui.moveTo(toClick)
            pyautogui.leftClick()
            action = 1
            click("skillsetL.png", 0.75, 0, 0)

        if not checkActive():
            print(f"Minimized while in encounter mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            print(
                f"\033[A{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} was defeated.",
                end=" ",
            )
            print(
                f"Time: {Fore.CYAN}{round(time.time()-battle_start, 3)}s{Fore.LIGHTBLACK_EX}"
            )
            return


def catchMode():
    global miscrit
    action = 0
    caught = False

    catchButton = LXVI_locateCenterOnScreen("catchbtn.png", 0.75)
    while not caught:
        if not checkActive():
            print(
                f"\033[AMinimized while trying to catch {Fore.YELLOW}{miscrit}{Fore.LIGHTBLACK_EX}, concluding process..."
            )
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                print(
                    f"\033[A{Fore.WHITE}Target miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} died. Failed to catch.{Fore.LIGHTBLACK_EX}"
                )
                return

        if (
            toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)
        ) is not None:
            toClick = (toClick.x - 45, toClick.y + 80)

            if isinstance(catchButton, Point):
                chance = LXVI_readImage([int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22], True)

            if int(chance) >= catchable:
                if action != 4:
                    action = 3
            if action == 0:
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                action = 1
            elif action == 1:
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                action = 2
            elif action == 2:
                click("skillsetR.png", 0.75, 0, 0)
                click("skillsetR.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                click("skillsetL.png", 0.75, 0, 0)
                pyautogui.moveTo(toClick)
            elif action == 3:
                click("catchbtn.png", 0.75, 6, 0)
                if LXVI_locateCenterOnScreen("catchSuccess.png", 0.9) is not None:
                    playSound(bend)
                    caught = True
                else:
                    action = 4
            elif action == 4:
                pyautogui.moveTo(toClick)
                print(
                    f"\033[A{Fore.WHITE}Time to kill {Fore.YELLOW}{miscrit}{Fore.WHITE}, I guess.{Fore.LIGHTBLACK_EX}"
                )
                pyautogui.moveRel(-45 + 160 * 1, 0)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick)

    print(
        f"\033[A{Fore.YELLOW}{miscrit}{Fore.WHITE} has been caught.     {Fore.LIGHTBLACK_EX}"
    )
    click("catchSkip.png", 0.9, 2, 0)
    click("closebtn.png", 0.85, 2, 0)


def summary():
    global b
    trainable = False

    if not checkActive():
        print("Minimized after Miscrit encounter, concluding process...")
        conclude()
    
    # time.sleep(1)

    if LXVI_locateCenterOnScreen("trainable1.png", 0.675) is not None:
        trainable = True

    b += 1
    click("closebtn.png", 0.8, 1, 0)

    if autoCatch:
        time.sleep(1.5)
        click("skipbtn.png", 0.75, 1, 0)

    if trainable:
        click("train.png", 0.75, 0.5, 0)
        train()


def train():
    while LXVI_locateCenterOnScreen("trainable.png", 0.6) is not None:
        if not checkActive():
            print("Minimized while training Miscrits, concluding process...")
            conclude()
        if not autoTrain:
            print("You have trainable Miscrits, concluding process...")
            conclude()
        click("trainable.png", 0.6, 0.2, 0.1)
        click("train2.png", 0.8, 0.5, 0.1)
        click("continuebtn.png", 0.9, 1, 0.1)

        click("continuebtn2.png", 0.75, 2, 0.1)
        click("continuebtn3.png", 0.75, 2, 0.1)
        click("skipbtn.png", 0.75, 2.5, 0.1)

    click("x.png", 0.8, 0.2, 0)


def conclude():
    print(
        f"\nEnded process after {Fore.CYAN}{b}{Fore.LIGHTBLACK_EX} Miscrits encountered."
    )
    print(f"Runtime: {Fore.CYAN}{time.time()-start}{Fore.LIGHTBLACK_EX}")
    playSound(off)
    print(Fore.RESET)
    time.sleep(1)
    sys.exit()


print(Fore.LIGHTBLACK_EX)
playSound(on)
time.sleep(1)
if not checkActive():
    print("Game not found on screen. Nothing happened.")
    conclude()
searchMode()
playSound(off)
time.sleep(1)
