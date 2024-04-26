from typing import List, cast
import sys
import time
import mss
import mss.tools
from PIL import ImageGrab
import numpy
import pyautogui
import easyocr
from colorama import Fore
from pyscreeze import Point
from os import environ
import pathlib
import pyjson5
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame


CONFIG = {}
with open("mConfig.json5", "r") as file:
    CONFIG = pyjson5.loads(file.read())

reader = easyocr.Reader(["en"], gpu=True, verbose=True)
pygame.init()


def UIImage(imagename: str) -> str:
    return str(pathlib.PurePath("UI_images", imagename))


b = 0
caught = False
start = time.perf_counter()
rizz = pygame.mixer.Sound(pathlib.PurePath("audio", "rizz.mp3"))
on = pygame.mixer.Sound(pathlib.PurePath("audio", "on.mp3"))
off = pygame.mixer.Sound(pathlib.PurePath("audio", "off.mp3"))
pluck = pygame.mixer.Sound(pathlib.PurePath("audio", "pluck.mp3"))
bend = pygame.mixer.Sound(pathlib.PurePath("audio", "bend.mp3"))

APPNAMEPNG = "appname.png"
if sys.platform.startswith("linux"):
    APPNAMEPNG = "appname_linux.png"

searchSeq = CONFIG["search"]["searchSeq"][CONFIG["search"]["searchCode"]]
for s, search in enumerate(searchSeq):
    searchSeq[s] = str(pathlib.PurePath("imgSources", f"{search}.png"))

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


def playSound(audio: pygame.mixer.Sound) -> None:
    if CONFIG["audio"]:
        audio.play()


def checkActive():
    return LXVI_locateCenterOnScreen(UIImage(APPNAMEPNG), 0.8) is not None


def LXVI_moveTo(p: Point, duration: float = 0):
    global monitor
    try:
        pyautogui.moveTo(
            int(p.x) + monitor["left"], int(p.y) + monitor["top"], duration=duration
        )
    except Exception:
        pyautogui.moveTo(
            int(p[0]) + monitor["left"], int(p[1]) + monitor["top"], duration=duration
        )


def LXVI_dragTo(p: Point, duration: float = 0):
    global monitor
    try:
        pyautogui.dragTo(
            int(p.x) + monitor["left"], int(p.y) + monitor["top"], duration=duration
        )
    except Exception:
        pyautogui.dragTo(
            int(p[0]) + monitor["left"], int(p[1]) + monitor["top"], duration=duration
        )


def LXVI_locateCenterOnScreen(
    imagename: str,
    confidence: float = 0.999,
    region: tuple[int, int, int, int] | None = None,
) -> Point | None:
    try:
        screenshot = ImageGrab.grab(
            bbox=(
                monitor["left"],
                monitor["top"],
                monitor["left"] + monitor["width"],
                monitor["top"] + monitor["height"],
            ),
            all_screens=True,
        )

        locateBox = pyautogui.locate(
            needleImage=imagename,
            haystackImage=screenshot,
            confidence=confidence,
            region=region,
        )
        if locateBox is None:
            return None
        return pyautogui.center(cast(tuple[int, int, int, int], locateBox))
    except pyautogui.ImageNotFoundException:
        return None


def LXVI_readImage(
    region: tuple[int, int, int, int] = (0, 0, 0, 0), numerical: bool = False
):
    # PIL library, bbox = (left,top,right,bottom)
    # pyautogui library, region = (left,top,width,height)

    # converts region to bbox
    bbox_left = monitor["left"] + region[0]
    bbox_top = monitor["top"] + region[1]
    bbox_right = bbox_left + region[2]
    bbox_bottom = bbox_top + region[3]

    computedBbox = (bbox_left, bbox_top, bbox_right, bbox_bottom)

    img = ImageGrab.grab(bbox=computedBbox, all_screens=True)
    if numerical:
        read = reader.recognize(
            numpy.array(img), allowlist="0123456789", blocklist="-~( ).,"
        )
    else:
        read = reader.recognize(numpy.array(img), blocklist="-~( ).,")
    (_, text, _) = read[0]

    # img.save(f"errorer.jpg")
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
            UIImage("gold.png"), confidence=0.7, region=[0, 100, 1920, 980]
        )
        is not None
    ):
        click(UIImage("gold.png"), 0.7, 0, 0, [0, 100, 1920, 980])
    while (
        LXVI_locateCenterOnScreen(UIImage("potion1.png"), confidence=0.65) is not None
    ):
        click(UIImage("potion1.png"), 0.65, 0, 0)


rarDict = {
    "com": "Common",
    "rar": "Rare",
    "epi": "Epic",
    "exo": "Exotic",
    "lag": "Legendary",
}


def getMiscritData():
    global rarDict, miscrit, rarity
    miscrits_lore = LXVI_locateCenterOnScreen(UIImage("miscrits_lore.png"), 0.8)
    if isinstance(miscrits_lore, Point):
        miscrit = LXVI_readImage(
            [int(miscrits_lore.x) + -130, int(miscrits_lore.y) + 32, 238, 40]
        )
        rarity = LXVI_readImage(
            [int(miscrits_lore.x) + -86, int(miscrits_lore.y) + 116, 60, 25]
        )
        rarity = rarity[:3].lower()
        rarity = rarDict[rarity]
    else:
        miscrit = "[unidentified]"
        rarity = "Unidentified"


def getCatchChance():
    catchButton = LXVI_locateCenterOnScreen(UIImage("catchbtn.png"), 0.75)
    if isinstance(catchButton, Point):
        chance = int(
            LXVI_readImage(
                [int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22], True
            )
        )
        return chance
    else:
        return None


def getTeamLevel():
    myMiscrits = LXVI_locateCenterOnScreen(UIImage("myMiscrits.png"), 0.9)
    levels = []
    if isinstance(myMiscrits, Point):
        levelA = Point(x=myMiscrits.x - 8, y=myMiscrits.y + 73)
        for x in range(3):
            try:
                levels.append(
                    int(
                        LXVI_readImage(
                            [int(levelA.x), int(levelA.y) + 50 + x * 50, 15, 15], True
                        )
                    )
                )
            except Exception:
                levels.append(0)
        return levels
    else:
        return [0, 0, 0]


def useSkill(toClick: Point, skillNo: int = 1):
    global onSkillPage

    page = int(skillNo / 4) + 1
    skill = (skillNo - 1) % 4
    skillClick = Point(toClick.x + 160 * skill, toClick.y)

    while onSkillPage != page:
        if onSkillPage < page:
            click(UIImage("skillsetR.png"), 0.75, 0, 0)
            onSkillPage += 1
        elif onSkillPage > page:
            click(UIImage("skillsetL.png"), 0.75, 0, 0)
            onSkillPage -= 1

    while (
        LXVI_locateCenterOnScreen(
            UIImage("run.png"), 0.99, [toClick.x - 132, toClick.y - 106, 36, 55]
        )
        is None
    ):
        if (
            LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is not None
            or not checkActive()
        ):
            return
        pass

    LXVI_moveTo(skillClick)
    pyautogui.leftClick()
    pyautogui.moveRel(0, 40)


def searchMode():
    while True:
        if not checkActive():
            print("Game not found during search mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8) is not None:
            encounterMode()
            summary()
        elif LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.8) is not None:
            click(UIImage("closebtn.png"), 0.8, 1, 0)

        cleanUp()

        if CONFIG["search"]["autoSearch"]:
            SearchSuccess = False
            for search in searchSeq:
                if (
                    toClick := LXVI_locateCenterOnScreen(search, confidence=0.8)
                ) is None:
                    continue

                SearchSuccess = True
                LXVI_moveTo(toClick, duration=0.1)
                pyautogui.leftClick()
                time.sleep(CONFIG["search"]["searchInterval"])

                if (
                    LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8)
                    is not None
                ):
                    encounterMode()
                    summary()

            if not SearchSuccess:
                print("Elements not found, concluding process...")
                conclude()
        else:
            time.sleep(0.5)


def encounterMode():
    global miscrit, b, onSkillPage, rarity

    b += 1
    miscrit = "[redacted]"
    rarity = "Unidentified"
    action = 0
    onSkillPage = 1
    battle_start = time.perf_counter()

    while LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8) is None:
        pass

    if (
        LXVI_locateCenterOnScreen(UIImage(CONFIG["mainMiscrit"]["strength"]), 0.95)
        is not None
    ):
        action = -1
    elif (
        LXVI_locateCenterOnScreen(UIImage(CONFIG["mainMiscrit"]["weakness"]), 0.95)
        is not None
    ):
        action = 1

    # miscritsCheck info
    click(UIImage("miscripedia.png"), 0.8, 0.555, 0)
    getMiscritData()
    print(f"{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} wants to fight.")
    click(UIImage("mpedia_exit.png"), 0.8, 0, 0)
    pyautogui.leftClick()

    if CONFIG["wild"]["targetAll"] or miscrit in CONFIG["wild"]["targets"]:
        print(
            f"\033[A{Fore.WHITE}Target miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} found!{Fore.LIGHTBLACK_EX}"
        )

        if CONFIG["wild"]["autoCatch"]:
            catchStandard = CONFIG["wild"]["catchStandardDict"][rarity]
            while LXVI_locateCenterOnScreen(UIImage("run.png"), 0.99) is None:
                pass
            if (getCatchChance() <= catchStandard) or (
                miscrit in CONFIG["wild"]["targets"]
            ):
                playSound(pluck)
                catchMode()
                return
            else:
                print(
                    f"\033[A{Fore.WHITE}This {Fore.YELLOW}{miscrit}{Fore.WHITE} is trash. -p0lbang{Fore.LIGHTBLACK_EX}"
                )

    if not checkActive():
        print("Minimized while in encounter mode, concluding process...")
        conclude()

    if CONFIG["wild"]["fightHunt"]:
        toClick = LXVI_locateCenterOnScreen(UIImage("run.png"), 0.75)
        toClick = Point(toClick.x + 115, toClick.y + 80)
    else:
        while (toClick := LXVI_locateCenterOnScreen(UIImage("run.png"), 0.99)) is None:
            pass
        LXVI_moveTo(toClick)
        pyautogui.leftClick()
        print(
            f"\033[ASuccessfully escaped from {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}."
        )

    while True:
        if action == 0:  # strongest attack
            useSkill(toClick, CONFIG["mainMiscrit"]["main"])
        elif (
            action < 0
        ):  # alternative attack to use for elements that are weak against you
            useSkill(toClick, CONFIG["mainMiscrit"]["strong"])
        else:  # negate element skill
            useSkill(toClick, CONFIG["mainMiscrit"]["negate"])
            action = 0

        if not checkActive():
            print("Minimized while in encounter mode, concluding process...")
            conclude()

        if LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is not None:
            print(
                f"\033[A{Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} was defeated.",
                end=" ",
            )
            print(
                f"Time: {Fore.CYAN}{round(time.perf_counter()-battle_start, 3)}s{Fore.LIGHTBLACK_EX}"
            )
            return


def catchMode():
    global miscrit, caught
    action = 1

    initialChance = getCatchChance()
    chance = initialChance
    print(
        f"     {Fore.YELLOW}{miscrit}{Fore.LIGHTBLACK_EX}'s initial catch rate: {Fore.CYAN}{initialChance}%{Fore.LIGHTBLACK_EX}"
    )

    if (
        LXVI_locateCenterOnScreen(UIImage(CONFIG["mainMiscrit"]["weakness"]), 0.95)
        is not None
    ):
        action = 0

    while not caught:
        if not checkActive():
            print(
                f"Minimized while trying to catch {Fore.YELLOW}{miscrit}{Fore.LIGHTBLACK_EX}, concluding process..."
            )
            conclude()

        if (
            LXVI_locateCenterOnScreen(UIImage("miscripedia.png"), confidence=0.8)
            is None
        ):
            if LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is not None:
                print(
                    f"\033[A     {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} died at {Fore.RED}{chance}%{Fore.LIGHTBLACK_EX} catch rate.    "
                )
                return

        if (
            toClick := LXVI_locateCenterOnScreen(UIImage("run.png"), confidence=0.99)
        ) is not None:
            toClick = Point(toClick.x + 115, toClick.y + 80)
            chance = getCatchChance()

            if int(chance) >= CONFIG["wild"]["catchablePercentage"]:
                if action != 4:
                    action = 3

            if action == 0:
                useSkill(toClick, CONFIG["mainMiscrit"]["negate"])
                action = 1
            elif action == 1:
                useSkill(toClick, CONFIG["mainMiscrit"]["bigpoke"])
                action = 2
            elif action == 2:
                useSkill(toClick, CONFIG["mainMiscrit"]["poke"])
            elif action == 3:
                click(UIImage("catchbtn.png"), 0.75, 6, 0)
                if (
                    LXVI_locateCenterOnScreen(UIImage("catchSuccess.png"), 0.9)
                    is not None
                ):
                    playSound(bend)
                    caught = True
                else:
                    action = 4
            elif action == 4:
                print(
                    f"{Fore.LIGHTBLACK_EX}     Failed to catch {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} with {Fore.RED}{chance}%{Fore.LIGHTBLACK_EX}."
                )
                useSkill(toClick, CONFIG["mainMiscrit"]["main"])

    print(
        f"\033[A     {Fore.YELLOW}{miscrit}{Fore.WHITE} has been caught. {Fore.LIGHTBLACK_EX}Initial chance: {Fore.GREEN}{initialChance}%{Fore.LIGHTBLACK_EX}"
    )
    click(UIImage("catchSkip.png"), 0.9, 2, 0)
    click(UIImage("closebtn.png"), 0.85, 2, 0)


def summary():
    global caught
    trainable = False

    if not checkActive():
        print("Minimized after Miscrit encounter, concluding process...")
        conclude()

    if LXVI_locateCenterOnScreen(UIImage("trainable1.png"), 0.75) is not None:
        trainable = True

    click(UIImage("closebtn.png"), 0.8, 0.5, 0)

    if caught:
        time.sleep(1.5)
        click(UIImage("skipbtn.png"), 0.75, 1, 0)
        caught = False

    if trainable:
        click(UIImage("train.png"), 0.75, 0.5, 0)
        train()


def train():
    while LXVI_locateCenterOnScreen(UIImage("trainable.png"), 0.6) is not None:
        if not checkActive():
            print("Minimized while training Miscrits, concluding process...")
            conclude()
        if not CONFIG["team"]["autoTrain"]:
            print("You have trainable Miscrits, concluding process...")
            conclude()
        click(UIImage("trainable.png"), 0.6, 0.2, 0.1)
        click(UIImage("train2.png"), 0.8, 0.5, 0.1)
        if CONFIG["team"]["bonusTrain"]:
            click(UIImage("bonustrain.png"), 0.9, 0.4, 0.1)
        click(UIImage("continuebtn.png"), 0.9, 1, 0.1)

        click(UIImage("continuebtn.png"), 0.75, 2, 0.1)
        click(UIImage("continuebtn.png"), 0.75, 2, 0.1)
        click(UIImage("skipbtn.png"), 0.75, 1, 0.1)

    if CONFIG["team"]["autoSwitch"]:
        levelBCD = [level >= CONFIG["team"]["switchLevel"] for level in getTeamLevel()]

    click(UIImage("x.png"), 0.8, 0.2, 0)

    if CONFIG["team"]["autoSwitch"] and (True in levelBCD):
        switchTeam(levelBCD)


def switchTeam(levelBCD):
    while LXVI_locateCenterOnScreen(UIImage("teambtn.png"), 0.9) is None:
        pass
    click(UIImage("teambtn.png"), 0.9, 0.5, 0)

    outCount = 0
    exit = LXVI_locateCenterOnScreen(UIImage("x.png"), 0.9)
    pointD = Point(int(exit.x) - 90, int(exit.y) + 200)
    offset = Point(-180, 0)
    for l, level in enumerate(reversed(levelBCD)):
        if level:
            outCount += 1
            pointX = Point(pointD.x + l * offset.x, pointD.y + l * offset.y)
            LXVI_moveTo(pointX)
            pyautogui.dragRel((0, 150))
            time.sleep(0.1)

    point0 = Point(exit.x - 665, exit.y + 315)
    pointZ = Point(point0.x - 30, point0.y - 30)
    offset = Point(172, 84)

    lastMiscrit = False
    while not lastMiscrit:
        for row in range(3):
            if lastMiscrit:
                break

            for column in range(4):
                pointN = Point(pointZ.x + column * offset.x, pointZ.y + row * offset.y)
                pointM = Point(point0.x + column * offset.x, point0.y + row * offset.y)

                if (
                    LXVI_locateCenterOnScreen(
                        UIImage("teamslotEmpty.png"), 0.8, [pointN.x, pointN.y, 150, 65]
                    )
                    is not None
                ):
                    lastMiscrit = True
                    break

                level = int(
                    LXVI_readImage([int(pointM.x), int(pointM.y), 16, 14], True)
                )
                if level < CONFIG["team"]["switchLevel"]:
                    LXVI_moveTo(pointM)
                    LXVI_dragTo(pointD, 0.2)
                    outCount -= 1
                    if outCount == 0:
                        lastMiscrit = True
                        break

        click(UIImage("teamR.png"), 0.8, 0, 0)
    click(UIImage("savebtn.png"), 0.8, 0, 0)


def reLogin():
    print("UNDER DEVELOPMENT")
    # the code gets here if the time is before 8:00 AM
    # it will wait until logged out by the server and log back in
    if toClick := LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.8) is not None:
        if autoLogin:
            LXVI_moveTo(toClick)
            pyautogui.leftClick()
        else:
            print("Account logged out. Ending session.")
            sys.exit()


def dailySpin():
    print("UNDER DEVELOPMENT")
    # the code gets here after logging back in for the first time after daily reset
    # it will press spin and accept the reward


def walkOrSumtin():
    print("UNDER DEVELOPMENT")
    # if this is on, it should have an array of images to follow until it sees the
    # current search sequence elements then proceed to autoSearching


def conclude():
    print(
        f"\nEnded process after {Fore.CYAN}{b}{Fore.LIGHTBLACK_EX} Miscrits encountered."
    )
    print(f"Runtime: {Fore.CYAN}{time.perf_counter()-start}{Fore.LIGHTBLACK_EX}")
    playSound(rizz)
    playSound(off)
    print(Fore.RESET)
    time.sleep(1)
    sys.exit()


print(Fore.LIGHTBLACK_EX)
playSound(on)
time.sleep(1)
while checkActive():
    searchMode()
print("Game not found on screen. Nothing happened.")
