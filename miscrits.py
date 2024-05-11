from typing import cast
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
import math
from pynput.keyboard import Key, KeyCode, Listener
import threading
import os
import datetime
import json
import miscritsData

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame  # noqa: E402


def readJSON(filename: str, sortouter: bool = True, sortinner: bool = True) -> dict:
    try:
        DICTIONARY = {}
        with open(filename, "r") as file:
            filetext = file.read()
            if filetext != "":
                tempjson = pyjson5.loads(filetext)
                DICTIONARY = tempjson

                if sortinner:
                    for key, value in tempjson.items():
                        try:
                            DICTIONARY[key] = dict(sorted(tempjson[key].items()))
                        except AttributeError:
                            pass

                if sortouter:
                    DICTIONARY = dict(sorted(DICTIONARY.items()))

        return DICTIONARY
    except IOError:  # FileNotFoundError in Python 3
        with open(filename, "w") as file:
            file.write(str(pyjson5.dumps({})))
            return {}


# AREASTATS = readJSON("areastats.json5")
CATCHRATE = readJSON("catchrate.json5")
CONFIG = readJSON("mConfig.json5", sortouter=False, sortinner=False)
PRESETS = readJSON("mPresets.json5", sortouter=True, sortinner=False)
CRITS = readJSON("mData.json5", sortouter=True, sortinner=False)

reader = easyocr.Reader(["en"], gpu=True, verbose=True)
MCDATA = miscritsData.MiscritsData()


def UIImage(imagename: str) -> str:
    return str(pathlib.PurePath("UI_images", imagename))


# use only for folder with files inside. never with other folders inside
def miscritProfiles() -> list[str]:
    return [
        f
        for f in os.listdir(pathlib.PurePath("profileImages"))
        if os.path.isfile(pathlib.PurePath("profileImages", f))
    ]


def getSound(filename):
    if not CONFIG["audio"]:
        return None
    return pygame.mixer.Sound(filename)


b = 0
sNo = 1
caught = False
toContinue = True
firstBattle = True
autoSwitch = CONFIG["team"]["autoSwitch"]
start = time.perf_counter()

if CONFIG["audio"]:
    pygame.init()

on = getSound(pathlib.PurePath("audio", "on.mp3"))
off = getSound(pathlib.PurePath("audio", "off.mp3"))
rizz = getSound(pathlib.PurePath("audio", "rizz.mp3"))
pluck = getSound(pathlib.PurePath("audio", "pluck.mp3"))
bend = getSound(pathlib.PurePath("audio", "bend.mp3"))
rock = getSound(pathlib.PurePath("audio", "rock.mp3"))

APPNAMEPNG = "appname.png"
if sys.platform.startswith("linux"):
    APPNAMEPNG = "appname_linux.png"

searchCode = CONFIG["search"]["searchCode"]
searchSeq = CONFIG["search"]["searchSeq"][searchCode]
for s, search in enumerate(searchSeq):
    searchSeq[s] = str(pathlib.PurePath("searchImages", f"{search}.png"))

walkRegion = searchCode[:2]
walkSeq = CONFIG["walk"]["walkSeq"][walkRegion]
walkInt = CONFIG["walk"]["walkSeq"][f"{walkRegion}0"]
walkDis = CONFIG["walk"]["walkDistance"]
for w, walk in enumerate(walkSeq):
    walkSeq[w] = Point(
        int(walkDis * math.cos(math.radians(walkSeq[w]))),
        int(-walkDis * math.sin(math.radians(walkSeq[w]))),
    )
walkRegion = str(pathlib.PurePath("walkImages", f"{walkRegion}.png"))

qualityDict = ["F-","F ","F+","D ","D+","C ","C+","B ","B+","A ","A+","S ","S+","XX"]

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

stop_event = threading.Event()
configupdate_event = threading.Event()


def playSound(audio: pygame.mixer.Sound) -> None:
    if CONFIG["audio"]:
        audio.play()


def checkActive():
    if CONFIG["minimizable"]:
        while LXVI_locateCenterOnScreen(UIImage(APPNAMEPNG), 0.8) is None:
            pass
    if LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.9) is not None:
        login()
        return True
    return LXVI_locateCenterOnScreen(UIImage(APPNAMEPNG), 0.8) is not None


def checkMaintenanceTime():
    now = datetime.datetime.now()
    if now.hour == 7 and now.minute >= 55:
        return True
    else:
        return False


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


def LXVI_screenshot(
    region: tuple[int, int, int, int] | None = None,
):
    # PIL library, bbox = (left,top,right,bottom)
    # pyautogui library, region = (left,top,width,height)

    # converts region to bbox
    computedBbox = None
    if region is not None:
        bbox_left = monitor["left"] + region[0]
        bbox_top = monitor["top"] + region[1]
        bbox_right = bbox_left + region[2]
        bbox_bottom = bbox_top + region[3]

        computedBbox = (bbox_left, bbox_top, bbox_right, bbox_bottom)
        
    img = ImageGrab.grab(bbox=computedBbox, all_screens=True)

    return img


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
    img = LXVI_screenshot(region=region)
    if numerical:
        read = reader.recognize(
            numpy.array(img), allowlist="0123456789", blocklist="-~( ).,"
        )
    else:
        read = reader.recognize(numpy.array(img), blocklist="-~( ).,1234567890")
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
    toClick = LXVI_locateCenterOnScreen(imagename, confidence=confidence, region=region)

    if toClick is None:
        return False

    LXVI_moveTo(toClick, duration=duration)
    pyautogui.leftClick()
    time.sleep(sleep)
    return True


def cleanUp():
    while (
        LXVI_locateCenterOnScreen(UIImage("gold.png"), 0.7, [0, 100, 1920, 980])
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
    "leg": "Legendary",
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
        miscrit = miscrit[0].upper() + miscrit[1:]
        rarity = rarity[:3].lower()
        rarity = rarDict[rarity]
    else:
        miscrit = "[unidentified]"
        rarity = "Unidentified"


def getCurrentMiscrit(region: tuple[int, int, int, int] | None = None):
    global reader, img

    mPedia = LXVI_locateCenterOnScreen(UIImage("miscripedia.png"), 0.8)
    if mPedia is not None:
        img = LXVI_screenshot(region=(int(mPedia.x) - 289, int(mPedia.y) - 31, 40, 40))
        img.save(f"{UIImage("currentMiscrit.png")}")


def updateCurrentMiscrit():
    global onSkillPage
    onSkillPage = 1

    PRESETS = {}
    with open("mPresets.json5", "r") as file:
        PRESETS = pyjson5.loads(file.read())

    for profile in miscritProfiles():
        if (
            LXVI_locateCenterOnScreen(
                str(pathlib.PurePath("profileImages", profile)), 0.95
            )
            is not None
        ):
            profileName = profile[:-4]
            print(f"\033[AActivated Preset: {profileName}             \n")
            return profileName

    print("Miscrit profile not found, creating new profile.")
    print(
        "Run this code again after changing image name in profileImages and details in mPresets.json5"
    )
    mPedia = LXVI_locateCenterOnScreen(UIImage("miscripedia.png"), 0.8)
    if isinstance(mPedia, Point):
        img = LXVI_screenshot(region=(int(mPedia.x) - 289, int(mPedia.y) - 31, 40, 40))
        img.save("profileImages\\newProfile.png")
    PRESETS["newProfile"] = {}
    PRESETS["newProfile"]["skipWeakness"] = True
    PRESETS["newProfile"]["strength"] = "gold.png"
    PRESETS["newProfile"]["weakness"] = "gold.png"
    PRESETS["newProfile"]["isDual"] = False
    PRESETS["newProfile"]["strength2"] = "gold.png"
    PRESETS["newProfile"]["weakness2"] = "gold.png"
    PRESETS["newProfile"]["ignoreWeakness"] = False
    PRESETS["newProfile"]["hasNegate"] = False
    PRESETS["newProfile"]["hasHeal"] = False
    PRESETS["newProfile"]["healCD"] = 1
    PRESETS["newProfile"]["main"] = 1
    PRESETS["newProfile"]["strong"] = 1
    PRESETS["newProfile"]["weak"] = 3
    PRESETS["newProfile"]["heal"] = 1
    PRESETS["newProfile"]["bigpoke"] = 1
    PRESETS["newProfile"]["poke"] = 10

    with open("mPresets.json5", "w") as file:
        outputtxt = json.dumps(PRESETS, indent=2)
        file.write(outputtxt)

    print("Concluding process...")
    conclude()


def getCatchChance():
    catchButton = LXVI_locateCenterOnScreen(UIImage("catchbtn.png"), 0.75)
    if isinstance(catchButton, Point):
        chance = int(
            LXVI_readImage(
                [int(catchButton.x) - 17, int(catchButton.y) + 13, 18, 22], True
            )
        )
        if chance >= 110:
            return 10
        return min(chance, 100)
    else:
        return None


def getTeamLevel():
    myMiscrits = LXVI_locateCenterOnScreen(UIImage("myMiscrits.png"), 0.9)
    levels = []
    if isinstance(myMiscrits, Point):
        levelA = Point(x=myMiscrits.x - 8, y=myMiscrits.y + 73)
        for x in range(4):
            try:
                levels.append(
                    int(
                        LXVI_readImage(
                            [int(levelA.x), int(levelA.y) + x * 50, 15, 15], True
                        )
                    )
                )
            except Exception:
                levels.append(0)
        return levels
    else:
        return [0, 0, 0, 0]


def useSkill(toClick: Point, skillNo: int = 1):
    global onSkillPage, skillClick

    page = int((skillNo - 1) / 4) + 1
    skill = (skillNo - 1) % 4
    skillClick = Point(toClick.x + 160 * skill, toClick.y)
    skillsetL = Point(toClick.x - 130, toClick.y)
    skillsetR = Point(toClick.x + 610, toClick.y)

    while onSkillPage != page:
        if onSkillPage < page:
            LXVI_moveTo(skillsetR)
            pyautogui.leftClick()
            onSkillPage += 1
        elif onSkillPage > page:
            LXVI_moveTo(skillsetL)
            pyautogui.leftClick()
            onSkillPage -= 1

    if CONFIG["fight"]["autoFight"]:
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
    else:
        LXVI_moveTo(skillClick)


def walkMode():
    (chatX, chatY) = LXVI_locateCenterOnScreen(UIImage("levelTop.png"), 0.95)
    (settX, settY) = LXVI_locateCenterOnScreen(UIImage("menubtn.png"), 0.95)
    center = Point(int((chatX + settX) / 2), int((chatY + settY) / 2))
    LXVI_moveTo(center)
    time.sleep(3)
    while checkActive:
        walkGoal = str(pathlib.PurePath("walkImages", f"{searchCode}.png"))
        if LXVI_locateCenterOnScreen(walkGoal, 0.90) is not None:
            return

        if CONFIG["walk"]["autoWalk"]:
            for w, walk in enumerate(walkSeq):
                toWalk = Point(center.x + walk.x, center.y + walk.y)
                LXVI_moveTo(toWalk, 0.2)
                pyautogui.mouseDown()
                # print(f"{walk} | {walkInt[w]}")
                time.sleep(walkInt[w])

                if (toClick := LXVI_locateCenterOnScreen(walkGoal, 0.85)) is not None:
                    LXVI_moveTo(toClick)
                    pyautogui.mouseUp()
                    time.sleep(1)
                    return
            pyautogui.mouseUp()
            return


def searchMode():
    global wildDATA, wildID, wildStats, wildScore

    loopcount = 0
    while True:
        if not checkActive():
            conclude()

        cleanUp()

        if checkMaintenanceTime():
            click(UIImage("menubtn.png"), 0.9, 0.2)
            click(UIImage("logoutbtn.png"))
            time.sleep(310)

        if CONFIG["search"]["autoSearch"]:
            loopcount += 1

            for search in searchSeq:
                if (toClick := LXVI_locateCenterOnScreen(search, 0.85)) is None:
                    continue

                LXVI_moveTo(toClick, 0.1)
                if LXVI_locateCenterOnScreen(UIImage("searchCD.png"), 0.9) is not None:
                    while (
                        LXVI_locateCenterOnScreen(UIImage("searchCD.png"), 0.9)
                        is not None
                    ):
                        pass
                pyautogui.leftClick()

                wildScore = 0
                try:
                    wildStats, wildID = MCDATA.getStatsID(CONFIG["search"]["searchInterval"])
                except:
                    wildStats = [0,0,0,0,0,0]
                    wildID = 0
                # print(f"\n\n{wildDATA}\n")

                for stat in wildStats:
                    wildScore += int(wildStats[stat])
                if wildScore == 0:
                    wildScore = 13
                else:
                    wildScore -= 6

                time.sleep(max(CONFIG["search"]["searchInterval"] - MCDATA.timeElapsed, 0))
                loopcount = 0

                if (
                    LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8)
                    is not None
                ):
                    encounterMode()
                    summary()

            if loopcount > 5:
                conclude()

        else:
            wildScore = 0
            try:
                wildStats, wildID = MCDATA.getStatsID(CONFIG["search"]["searchInterval"])
            except:
                wildStats = [0,0,0,0,0,0]
                wildID = 0
            # print(f"\n\n{wildDATA}\n")

            for stat in wildStats:
                wildScore += int(wildStats[stat])
            if wildScore == 0:
                wildScore = 13
            else:
                wildScore -= 6

            time.sleep(max(CONFIG["search"]["searchInterval"] - MCDATA.timeElapsed, 0))
            loopcount = 0

            if (
                LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8)
                is not None
            ):
                encounterMode()
                summary()
            time.sleep(0.5)


def encounterMode():
    global miscrit, current, weakness, strength1, b, sNo, onSkillPage, rarity, battle_start, toClick, toRun, firstBattle  # noqa

    b += 1
    sNo = 1
    action = 0
    onSkillPage = 1
    battle_start = time.perf_counter()
    weakness = False
    strength1 = False
    miscrit = "[redacted]"
    rarity = "Unidentified"

    while LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8) is None:
        pass

    if (
        firstBattle
        or LXVI_locateCenterOnScreen(UIImage("currentMiscrit.png"), 0.80) is None
    ):
        firstBattle = False
        getCurrentMiscrit()
        current = updateCurrentMiscrit()

    # miscritsCheck info
    CRITS = readJSON("mData.json5", sortouter=True, sortinner=False)

    try:
        miscrit = CRITS[str(f"{int(wildID):03d}")]["name"]
        rarity = CRITS[str(f"{int(wildID):03d}")]["rarity"]
    except KeyError:
        click(UIImage("miscripedia.png"), 0.8, 0.555, 0)
        getMiscritData()
        click(UIImage("mpedia_exit.png"), 0.8, 0, 0)
        pyautogui.leftClick()
        
        CRITS[str(f"{int(wildID):03d}")] = {}
        CRITS[str(f"{int(wildID):03d}")]["name"] = miscrit
        CRITS[str(f"{int(wildID):03d}")]["rarity"] = rarity
        with open("mData.json5", "w") as file:
            outputtxt = json.dumps(CRITS, indent=2)
            file.write(outputtxt)


    print(f"{qualityDict[wildScore]} | {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} wants to fight.")

    if (
        LXVI_locateCenterOnScreen(UIImage(PRESETS[current]["strength"]), 0.8)
        is not None
    ):
        action = -1
        strength1 = True
    elif (
        LXVI_locateCenterOnScreen(UIImage(PRESETS[current]["weakness"]), 0.8)
        is not None
    ):
        action = 1
        weakness = True

    if PRESETS[current]["isDual"]:
        if (
            LXVI_locateCenterOnScreen(UIImage(PRESETS[current]["strength2"]), 0.8)
            is not None
        ):
            action = -1
            strength1 = False
        elif (
            LXVI_locateCenterOnScreen(UIImage(PRESETS[current]["weakness2"]), 0.8)
            is not None
        ):
            action = 1
            weakness = True

    if CONFIG["catch"]["autoCatch"]:
        if miscrit not in ["[redacted]", "[unidentified]"]:
            keyMiscrit = miscrit.strip().lower()
            if keyMiscrit not in CATCHRATE:
                CATCHRATE[keyMiscrit] = {}

            keyQuality = qualityDict[wildScore]

            if keyQuality not in CATCHRATE[keyMiscrit]:
                CATCHRATE[keyMiscrit][keyQuality] = 1
            else:
                CATCHRATE[keyMiscrit][keyQuality] += 1

        catchStandard = CONFIG["catch"]["catchStandardDict"][rarity]
        if (miscrit in CONFIG["catch"]["targets"] or (CONFIG["catch"]["targetAll"] and miscrit not in CONFIG["catch"]["blocked"] and wildScore >= catchStandard)):
            print(f"\033[A{Fore.WHITE}{qualityDict[wildScore]} | {Fore.WHITE}Target miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} found!{Fore.LIGHTBLACK_EX}")
            playSound(pluck)
            catchMode()
            return
        elif (CONFIG["catch"]["ignoreBlockedIfS+"] and wildScore >= 12) or (CONFIG["catch"]["catchF-"] and wildScore == 0):
            print(f"\033[A{Fore.WHITE}{qualityDict[wildScore]} | {Fore.WHITE}{qualityDict[wildScore]} miscrit {Fore.YELLOW}{miscrit}{Fore.WHITE} found!{Fore.LIGHTBLACK_EX}")
            playSound(rizz)
            catchMode()
            return        
        elif miscrit not in CONFIG["catch"]["blocked"]:
            print(f"\033[A{qualityDict[wildScore]} | {Fore.WHITE}This {Fore.YELLOW}{miscrit}{Fore.WHITE} is trash. -p0lbang{Fore.LIGHTBLACK_EX}")

    if not checkActive():
        print("Minimized while in encounter mode, concluding process...")
        conclude()

    if (
        (PRESETS[current]["skipWeakness"] or CONFIG["fight"]["skipWeakness"])
        and weakness
    ) or CONFIG["catch"]["skipAll"]:
        while (toClick := LXVI_locateCenterOnScreen(UIImage("run.png"), 0.99)) is None:
            pass
        LXVI_moveTo(toClick)
        pyautogui.leftClick()
        print(
            "\033[A",
            f"{qualityDict[wildScore]} | "
            f"Time: {Fore.CYAN}{(time.perf_counter()-battle_start):05.2f}s{Fore.LIGHTBLACK_EX} | ",
            f" Avoided {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}.",
            sep="",
        )

        while LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is None:
            pass

        return

    toRun = LXVI_locateCenterOnScreen(UIImage("run.png"), 0.75)
    toClick = Point(toRun.x + 115, toRun.y + 80)

    r = 0

    if CONFIG["fight"]["autoFight"]:
        while True:
            if LXVI_locateCenterOnScreen(UIImage("currentMiscrit.png"), 0.80) is None:
                getCurrentMiscrit()
                current = updateCurrentMiscrit()
            r += 1
            if (
                PRESETS[current]["hasHeal"]
                and r % int(PRESETS[current]["healCD"] + 1) == 2
            ):
                lastAction = action
                action = 2
            if action == 0:  # strongest attack
                useSkill(toClick, PRESETS[current]["main"])
            elif (
                action == -1
            ):  # alternative attack to use for elements that are weak against you
                if strength1:
                    useSkill(toClick, PRESETS[current]["strong"])
                else:
                    useSkill(toClick, PRESETS[current]["strong2"])
            elif action == 1:  # skill for weakness element
                if not PRESETS[current]["ignoreWeakness"]:
                    useSkill(toClick, PRESETS[current]["weak"])
                else:
                    useSkill(toClick, PRESETS[current]["main"])
                if PRESETS[current]["hasNegate"]:
                    action = 0
            elif action == 2:
                useSkill(toClick, PRESETS[current]["heal"])
                action = lastAction

            if not checkActive():
                print("Minimized while in encounter mode, concluding process...")
                conclude()

            if LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is not None:
                print(
                    "\033[A",
                    f"{qualityDict[wildScore]} | "
                    f"Time: {Fore.CYAN}{(time.perf_counter()-battle_start):05.2f}s{Fore.LIGHTBLACK_EX} | ",
                    f"Defeated {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}.",
                    sep="",
                )
                return
    else:
        global thread_keybfight, thread_waitfight

        useSkill(toClick, 1)

        thread_keybfight = Listener(on_release=keybFight)
        thread_keybfight.start()
        thread_waitfight = threading.Thread(target=waitFight)
        thread_waitfight.start()

        thread_waitfight.join()


def waitFight():
    while True:
        if not checkActive():
            print("Minimized while in fight mode, concluding process...")
            thread_keybfight.stop()
            conclude()

        if LXVI_locateCenterOnScreen(UIImage("closebtn.png"), 0.85) is not None:
            thread_keybfight.stop()
            print(
                "\033[A",
                f"{qualityDict[wildScore]} | "
                f"Time: {Fore.CYAN}{(time.perf_counter()-battle_start):05.2f}s{Fore.LIGHTBLACK_EX} | ",
                f"Defeated {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}.",
                sep="",
            )
            return


def keybFight(key: Key | KeyCode):
    global sNo, toClick, skillClick, toRun
    if isinstance(key, KeyCode):
        if key.char == "z":
            LXVI_moveTo(skillClick)
            pyautogui.leftClick()
            pyautogui.moveRel(0, 40)
        elif key.char == "x":
            toRun = LXVI_locateCenterOnScreen(UIImage("run.png"), 0.75)
            LXVI_moveTo(toRun)

    if isinstance(key, Key):
        if key == Key.left and sNo > 1:
            sNo -= 1
            useSkill(toClick, sNo)
        elif key == Key.right and sNo < 12:
            sNo += 1
            useSkill(toClick, sNo)
        elif key == Key.up and sNo > 4:
            sNo -= 4
            useSkill(toClick, sNo)
        elif key == Key.down and sNo < 9:
            sNo += 4
            useSkill(toClick, sNo)


def catchMode():
    global miscrit, caught, current
    action = 1

    while (toClick := LXVI_locateCenterOnScreen(UIImage("run.png"), 0.99)) is None:
        pass
    
    chance = getCatchChance()
    if chance >= 46:
        chance = str(chance)
        chance = int(chance[:1])
    elif chance == 45 and rarity != "Common":
        chance = 4
    elif chance == 35 and rarity != "Rare":
        chance = 3
    elif chance == 25 and rarity != "Epic":
        chance = 2
    elif chance == 15 and rarity != "Exotic":
        chance = 1

    if weakness:
        action = 0
    
    if rarity == "Legendary":
        playSound(rock)
        time.sleep(10)

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
                    f"\033[A{Fore.RED}{qualityDict[wildScore]}{Fore.LIGHTBLACK_EX} | {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX} died at {Fore.RED}{chance}%{Fore.LIGHTBLACK_EX} catch rate."
                )

                return

        if LXVI_locateCenterOnScreen(UIImage("currentMiscrit.png"), 0.80) is None:
            getCurrentMiscrit()
            current = updateCurrentMiscrit()

        if (
            toClick := LXVI_locateCenterOnScreen(UIImage("run.png"), confidence=0.99)
        ) is not None:
            toClick = Point(toClick.x + 115, toClick.y + 80)
            chance = getCatchChance()

            if (
                rarity == "Legendary"
                and int(chance) >= CONFIG["catch"]["catchablePercentageL"]
            ) or (
                rarity != "Legendary"
                and int(chance) >= CONFIG["catch"]["catchablePercentage"]
            ):
                if action != 3:
                    action = 2

            if action == 0:
                useSkill(toClick, PRESETS[current]["weak"])
                action = 1
            elif action == 1:
                if int(chance) < CONFIG["catch"]["bigpokeThreshold"]:
                    useSkill(toClick, PRESETS[current]["bigpoke"])
                else:
                    useSkill(toClick, PRESETS[current]["poke"])
            elif action == 2:
                click(UIImage("catchbtn.png"), 0.75, 6, 0)
                if (
                    LXVI_locateCenterOnScreen(UIImage("catchSuccess.png"), 0.9)
                    is not None
                ):
                    playSound(bend)
                    caught = True
                else:
                    action = 3
            elif action == 3:
                print(
                    f"\033[A{Fore.RED}{qualityDict[wildScore]}{Fore.LIGHTBLACK_EX} | Failed to catch {Fore.WHITE}{miscrit}{Fore.LIGHTBLACK_EX}.     "
                )
                useSkill(toClick, PRESETS[current]["main"])

    print(
        f"\033[A{Fore.GREEN}{qualityDict[wildScore]}{Fore.WHITE} | {Fore.YELLOW}{miscrit}{Fore.WHITE} has been caught at {Fore.GREEN}{chance}%. {Fore.LIGHTBLACK_EX}"
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

    if autoSwitch:
        levelABCD = [level >= CONFIG["team"]["switchLevel"] for level in getTeamLevel()]
        if not CONFIG["team"]["switchMain"]:
            levelABCD[0] = False

    click(UIImage("x.png"), 0.8, 0.2, 0)

    if autoSwitch and (True in levelABCD):
        switchTeam(levelABCD)


def switchTeam(levelABCD):
    global autoSwitch

    while LXVI_locateCenterOnScreen(UIImage("teambtn.png"), 0.9) is None:
        pass
    click(UIImage("teambtn.png"), 0.9, 0.5, 0)

    outCount = 0
    exit = LXVI_locateCenterOnScreen(UIImage("x.png"), 0.9)
    pointD = Point(int(exit.x) - 90, int(exit.y) + 200)
    offset = Point(-180, 0)
    for index, level in enumerate(reversed(levelABCD)):
        if level:
            outCount += 1
            pointX = Point(pointD.x + index * offset.x, pointD.y + index * offset.y)
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
    if outCount != 0:
        autoSwitch = False


def login():
    wait = time.perf_counter()
    if (toClick := LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.8)) is not None:
        print("\nAccount logged out, logging back in...")
        LXVI_moveTo(toClick)
        time.sleep(3)
        pyautogui.leftClick()
        time.sleep(5)
    if (toClick := LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.8)) is not None:
        print("Attempting to log in again...")
        LXVI_moveTo(toClick)
        time.sleep(3)
        pyautogui.leftClick()
    while LXVI_locateCenterOnScreen(UIImage("miscripedia.png"), 0.75) is None:
        if time.perf_counter() - wait >= 30:
            print("Having trouble signing back in. Concluding process...")
            conclude()
        pass
    print("Account logged back in. Resuming...   ")
    time.sleep(5)
    dailySpin()
    time.sleep(5)


def dailySpin():
    if LXVI_locateCenterOnScreen(UIImage("spinbtn.png"), 0.8):
        click(UIImage("spinbtn.png"), 0.8)
        while LXVI_locateCenterOnScreen(UIImage("spindonebtn.png"), 0.8) is None:
            pass
        time.sleep(1)
        click(UIImage("spindonebtn.png"), 0.8, 1)


def conclude():
    if LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.8):
        login()
        return

    with open("catchrate.json5", "w") as file:
        outputtxt = json.dumps(CATCHRATE, indent=2)
        file.write(outputtxt)

    print(
        f"\nEnded process after {Fore.CYAN}{b}{Fore.LIGHTBLACK_EX} Miscrits encountered."
    )
    print(f"Runtime: {Fore.CYAN}{time.perf_counter()-start}{Fore.LIGHTBLACK_EX}")
    playSound(off)
    print(Fore.RESET)
    time.sleep(0.5)
    sys.exit()


def runMiscrits():
    print(Fore.LIGHTBLACK_EX)
    playSound(on)
    print("Initiating code... process started.\n")
    time.sleep(1)
    while checkActive():
        if not checkActive():
            print("Game not found during search mode, concluding process...")
            conclude()
        if LXVI_locateCenterOnScreen(UIImage("battlebtns.png"), 0.8) is not None:
            encounterMode()
            summary()
        elif LXVI_locateCenterOnScreen(UIImage("loginbtn.png"), 0.8) is not None:
            login()
        else:
            click(UIImage("closebtn.png"), 0.9, 1, 0)
            click(UIImage("savebtn.png"), 0.95, 1, 0)
            click(UIImage("x.png"), 0.95, 1, 0)
        if CONFIG["walk"]["autoWalk"] and (
            LXVI_locateCenterOnScreen(walkRegion, 0.75) is not None
        ):
            walkGoal = str(pathlib.PurePath("walkImages", f"{searchCode}.png"))
            if LXVI_locateCenterOnScreen(walkGoal, 0.9) is None:
                walkMode()
        searchMode()
    print("Game not found on screen.")
    playSound(rizz)
    time.sleep(1)


def show(key: Key | KeyCode):
    global toContinue
    if isinstance(key, KeyCode):
        if key.char == "q":
            toContinue = False
            print("Stopping miscrits...")
            pyautogui.moveTo((0, 0))


thread_keyb = Listener(on_press=show)
thread_keyb.start()
try:
    runMiscrits()
except pyautogui.FailSafeException:
    thread_keyb.stop()
    conclude()