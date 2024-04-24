# ---------[    C O N F I G    ]---------#
sounds = True  # ..... ..................# just True or False
autoSearch = True  # ....................#
searchInterval = 4  # ...................# interval for clicking between searches [4 minimum for multiple]
autoTrain = True  # .....................# set to True to automatically level up miscrits
bonusTrain = False  # ...................# set to True if you want to spend platinum on your trainable miscrits
miscritCheck = False  # .................# set to True to get miscrit's name
huntType = "battle"  # ..................# "battle" or "escape" the miscrits that are not the target
autoCatch = True  # .....................# try to catch miscrit if catch rate is greater than
catchable = 85  # .......................# this catch percentage
catchStandardDict = {"Common": 27,  # ...# 27-45%
                     "Rare": 35,  # .....# 17-35%
                     "Epic": 25,  # .....# 10-25%
                     "Exotic": 10,  # ...# ?-10%
                     "Legendary": 10,  #.# ?-?
                     "Unidentified": 27  #
                     } # ................# initial catch percentage to capture for each rarity
WEAKNESS = "nature.png"  # ..............# choose element that is strong against main miscrit
targetAll = True  # .....................# set to True to make everyone a target for capture
targets = []  # .........................# miscrit names without space (pray for accuracy)
searchSeq = ["m1_stool", "m1_cage1", "m1_mirrors", "m1_cage2"]
                                         # copy sequences from 'locations.txt'
#----------------------------------------#

import sys
import time
import mss
import mss.tools
from PIL import ImageGrab
import numpy
import pyautogui
import easyocr
import easyocr.imgproc
import easyocr.character
from colorama import Fore
from pyscreeze import Point
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import pathlib

reader = easyocr.Reader(["en"], gpu=True, verbose=False)
pygame.init()

b = 0
caught = False
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
    searchSeq[s] = str(pathlib.PurePath("imgSources",f"{search}.png"))

with mss.mss() as sct:
    # Get information of monitor 2
    monitor_number = 1
    mon = sct.monitors[monitor_number]

    # The screen part to capture
    monitor = {
        "top": mon["top"],
        "left": mon["left"],
        "width": mon["width"],
        "height": mon["height"],
        "mon": monitor_number,
    }

assert monitor is not None

def playSound(sound: pygame.mixer.Sound) -> None:
    if sounds:
        sound.play()


def checkActive():
    if LXVI_locateCenterOnScreen(APPNAMEPNG, 0.8, 
                                #  [0, 0, 1920, 100]
                                 ) is not None:
        return True
    else:
        return False

def LXVI_moveTo(p: Point, duration:float = 0):
    global monitor
    try:
        pyautogui.moveTo(int(p.x)+monitor["left"],int(p.y)+monitor["top"], duration=duration)
    except Exception:
        pyautogui.moveTo(int(p[0])+monitor["left"],int(p[1])+monitor["top"], duration=duration)

def LXVI_locateCenterOnScreen(
    imagename: str,
    confidence: float = 0.999,
    region: tuple[int, int, int, int] | None = None,
) -> Point | None:
    try:
        screenshot = ImageGrab.grab(
            bbox=(monitor["left"],monitor["top"],monitor["left"]+monitor["width"],monitor["top"]+monitor["height"]),
            all_screens=True)

        locateBox = pyautogui.locate(needleImage=imagename,haystackImage=screenshot,confidence=confidence,region=region)
        return pyautogui.center(locateBox)
    except pyautogui.ImageNotFoundException:
        return None


def LXVI_readImage(
    region: tuple[int, int, int, int] | None = None, numerical: bool = False
):
    
    # PIL library, bbox = (left,top,right,bottom)
    # pyautogui library, region = (left,top,width,height)

    # converts region to bbox
    bbox_left = monitor["left"] + region[0]
    bbox_top =  monitor["top"] +  region[1]
    bbox_right = bbox_left + region[2]
    bbox_bottom = bbox_top + region[3]

    computedBbox = (
                bbox_left,
                bbox_top,
                bbox_right,
                bbox_bottom
            )

    img = ImageGrab.grab(
            bbox=computedBbox,
            all_screens=True
        )
    if numerical:
        read = reader.recognize(
            numpy.array(img), allowlist="0123456789", blocklist="-~( ).,"
        )
    else:
        read = reader.recognize(numpy.array(img), blocklist="-~( ).,")
    (_, text, _) = read[0]

    #img.save(f"errorer.jpg")
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

    LXVI_moveTo(toClick, duration=duration)
    pyautogui.leftClick()
    time.sleep(sleep)
    return True


def cleanUp():
    while (
        LXVI_locateCenterOnScreen(
            "gold.png", confidence=0.7, region=[0, 100, 1920, 980]
        )
        is not None
    ):
        click("gold.png", 0.7, 0, 0, [0, 100, 1920, 980])
    while LXVI_locateCenterOnScreen("potion1.png", confidence=0.65) is not None:
        click("potion1.png", 0.65, 0, 0)


def getMiscritName():
    miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)
    if isinstance(miscrits_lore, Point):
        name = LXVI_readImage([int(miscrits_lore.x) + -130, int(miscrits_lore.y) + 35, 238, 35])
        return name
    else:
        return "[unidentified]"


rarDict ={"com": "Common", "rar": "Rare", "epi": "Epic", "exo": "Exotic", "lag": "Legendary"}
def getMiscritRarity():
    global rarDict
    miscrits_lore = LXVI_locateCenterOnScreen("miscrits_lore.png", 0.8)
    if isinstance(miscrits_lore, Point):
        rarity = LXVI_readImage([int(miscrits_lore.x) + -86, int(miscrits_lore.y) + 116, 60, 25])
        rarity = rarity[:3].lower()
        if rarity in rarDict:
            return rarDict[rarity]
        else:
            return "Unidentified"
    else:
        return "Unidentified"


def getCatchChance():
    catchButton = LXVI_locateCenterOnScreen("catchbtn.png", 0.75)
    if isinstance(catchButton, Point):
        chance = int(LXVI_readImage([int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22], True))
        return chance
    else:
        return None


def searchMode():
    while True:
        if not checkActive():
            print("Game not found during search mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is not None:
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
                
                if (toClick := LXVI_locateCenterOnScreen(search, confidence=0.8)) is None:
                    time.sleep(1)
                    continue

                SearchSuccess = True
                LXVI_moveTo(toClick, duration=0.1)
                pyautogui.leftClick()
                time.sleep(searchInterval)

            if not SearchSuccess:
                print("Elements not found, concluding process...")
                conclude()
        else:
            time.sleep(0.5)
            continue


def encounterMode():
    global miscrit, b
    
    b += 1
    miscrit = "[redacted]"
    rarity = "Unidentified"
    action = 1
    battle_start = time.time()

    while LXVI_locateCenterOnScreen("battlebtns.png", 0.8) is None:
        pass

    if LXVI_locateCenterOnScreen(WEAKNESS, 0.8) is not None:
        action = 0

    if miscritCheck:
        click("miscripedia.png", 0.8, 0.555, 0)
        miscrit = getMiscritName()
        rarity = getMiscritRarity()
        print(f"{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} wants to fight.")
        click("mpedia_exit.png", 0.8, 0, 0)
        pyautogui.leftClick()
        # click("mpedia_exit.png", 0.8, 0, 0)

        if targetAll or miscrit in targets:
            print(f"\033[A{Fore.WHITE}Target miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} found!{Fore.LIGHTBLACK_EX}")
            playSound(rizz)

            if autoCatch:
                catchStandard = catchStandardDict[rarity]
                while (toClick := LXVI_locateCenterOnScreen("run.png", 0.99)) is None:
                    pass
                if (getCatchChance() <= catchStandard) or (miscrit in targets):
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
        
        if autoCatch:
            catchStandard = catchStandardDict[rarity]
            while LXVI_locateCenterOnScreen("run.png", 0.99) is None:
                pass
            if (getCatchChance() <= catchStandard) or (miscrit in targets):
                playSound(pluck)
                catchMode()
                return

    while (toClick := LXVI_locateCenterOnScreen("run.png", 0.99)) is None:
        pass

    if not checkActive():
        print("Minimized while in encounter mode, concluding process...")
        conclude()

    if huntType != "battle":
        LXVI_moveTo(toClick)
        print(f"\033[ASuccessfully escaped from {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}.")
        pyautogui.leftClick()
    else:
        toClick = (toClick.x + 115, toClick.y + 80)

    while True:
        if action > 0:
            LXVI_moveTo(toClick)
            pyautogui.leftClick()
        else:
            click("skillsetR.png", 0.75, 0, 0)
            LXVI_moveTo(toClick)
            pyautogui.leftClick()
            action = 1
            click("skillsetL.png", 0.75, 0, 0)

        if not checkActive():
            print("Minimized while in encounter mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
            print(f"\033[A{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} was defeated.", end=" ",)
            print(f"Time: {Fore.CYAN}{round(time.time()-battle_start, 3)}s{Fore.LIGHTBLACK_EX}")
            return


def catchMode():
    global miscrit, caught
    action = 0

    initialChance = getCatchChance()
    chance = initialChance
    print(f"     {Fore.YELLOW}{miscrit}{Fore.LIGHTBLACK_EX}'s initial catch rate: {Fore.CYAN}{initialChance}%{Fore.LIGHTBLACK_EX}")
    while not caught:
        if not checkActive():
            print(f"Minimized while trying to catch {Fore.YELLOW}{miscrit}{Fore.LIGHTBLACK_EX}, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen("miscripedia.png", confidence=0.8) is None:
            if LXVI_locateCenterOnScreen("closebtn.png", 0.85) is not None:
                print(f"\033[A     {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} died at {chance}% with initial catch rate: {Fore.RED}{initialChance}%.{Fore.LIGHTBLACK_EX}")
                return

        if (toClick := LXVI_locateCenterOnScreen("run.png", confidence=0.99)) is not None:
            toClick = (toClick.x - 45, toClick.y + 80)
            chance = getCatchChance()

            if int(chance) >= catchable:
                if action != 4:
                    action = 3
            if action == 0:
                click("skillsetR.png", 0.75, 0, 0)
                LXVI_moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 1, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                action = 1
            elif action == 1:
                click("skillsetR.png", 0.75, 0, 0)
                LXVI_moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                action = 2
            elif action == 2:
                click("skillsetR.png", 0.75, 0, 0)
                click("skillsetR.png", 0.75, 0, 0)
                LXVI_moveTo(toClick)
                pyautogui.moveRel(-45 + 160 * 2, 0)
                pyautogui.leftClick()
                click("skillsetL.png", 0.75, 0, 0)
                click("skillsetL.png", 0.75, 0, 0)
                LXVI_moveTo(toClick)
            elif action == 3:
                click("catchbtn.png", 0.75, 6, 0)
                if LXVI_locateCenterOnScreen("catchSuccess.png", 0.9) is not None:
                    playSound(bend)
                    caught = True
                else:
                    action = 4
            elif action == 4:
                LXVI_moveTo(toClick)
                print(f"{Fore.LIGHTBLACK_EX}     Failed to catch {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} with {Fore.RED}{chance}%{Fore.LIGHTBLACK_EX}.")
                pyautogui.moveRel(-45 + 160 * 1, 0)
                pyautogui.leftClick()
                LXVI_moveTo(toClick)

    print(f"\033[A     {Fore.YELLOW}{miscrit}{Fore.WHITE} has been caught. {Fore.LIGHTBLACK_EX}Initial chance: {Fore.GREEN}{initialChance}%{Fore.LIGHTBLACK_EX}")
    click("catchSkip.png", 0.9, 2, 0)
    click("closebtn.png", 0.85, 2, 0)


def summary():
    global caught
    trainable = False

    if not checkActive():
        print("Minimized after Miscrit encounter, concluding process...")
        conclude()
    
    # time.sleep(1)

    if LXVI_locateCenterOnScreen("trainable1.png", 0.75) is not None:
        trainable = True

    click("closebtn.png", 0.8, 0.5, 0)

    if caught:
        time.sleep(1.5)
        click("skipbtn.png", 0.75, 1, 0)
        caught = False

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
        if bonusTrain:
            click("bonustrain.png", 0.9, 0.4, 0.1)
        click("continuebtn.png", 0.9, 1, 0.1)

        click("continuebtn2.png", 0.75, 2, 0.1)
        click("continuebtn3.png", 0.75, 2, 0.1)
        click("skipbtn.png", 0.75, 1, 0.1)

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
