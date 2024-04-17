import pyautogui
import time
import sys

b = 0
start = time.time()

# SELECT WHICH ELEMENTS TO SEARCH IN ALTERNATION
EXPLORE = ["eldertree.png", "eldershrub.png"]
WEAKNESS = "nature.png"


def JEDD_locateCenterOnScreen(
    imagename: str, confidence: float
) -> pyautogui.Point | None:
    try:
        return pyautogui.locateCenterOnScreen(imagename, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None


def click(
    imagename: str, confidence: float = 0.9, sleep: float = 0.2, duration: float = 0.2
) -> bool:
    toClick = JEDD_locateCenterOnScreen(imagename, confidence=confidence)

    if toClick is None:
        return False

    pyautogui.moveTo(toClick, duration=duration)
    pyautogui.leftClick()
    time.sleep(sleep)
    return True


def searchMode():
    global EXPLORE
    checkActive()
    while JEDD_locateCenterOnScreen("expmultiplier.png", confidence=0.9) is not None:
        SearchSuccess = False
        for search in EXPLORE:
            if (
                toClick := JEDD_locateCenterOnScreen(search, confidence=0.9)
            ) is not None:
                SearchSuccess = True
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(4)

                if (
                    JEDD_locateCenterOnScreen("expmultiplier.png", confidence=0.8)
                    is None
                ):
                    battleMode()
                else:
                    continue

        if not SearchSuccess:
            checkActive()
            print("Elements not found, concluding process...")
            conclude()


def battleMode():
    global WEAKNESS, b
    checkActive()
    try:
        pyautogui.locateOnScreen("miscripedia.png", confidence=0.8)
        time.sleep(0.1)
        try:
            toClick = pyautogui.locateCenterOnScreen("run.png", confidence=0.99)
            pyautogui.moveTo(toClick, duration=0.2)
            try:
                pyautogui.locateOnScreen(WEAKNESS)
                pyautogui.leftClick()
            except Exception:
                pyautogui.moveRel(115, 80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick, duration=0.2)
        except Exception:
            battleMode()
        # print("battlemode again")
        battleMode()
    except Exception:
        b += 1
        # print("Battle done.")
        time.sleep(0.5)
        summary()


def summary():
    checkActive()
    try:
        try:
            pyautogui.locateOnScreen("trainable.png", confidence=0.6)
            trainable = True
        except Exception:
            trainable = False

        pyautogui.locateOnScreen("closebtn.png", confidence=0.9)
        time.sleep(1)
        pyautogui.moveTo(
            pyautogui.locateOnScreen("closebtn.png", confidence=0.85), duration=0.1
        )
        pyautogui.leftClick()
        time.sleep(1)

        if trainable is True:
            try:
                toClick = pyautogui.locateCenterOnScreen("train.png", confidence=0.75)
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(1)
                train()
            except Exception:
                searchMode()
        else:
            searchMode()
    except Exception:
        time.sleep(1)
        summary()


def train():
    checkActive()
    try:
        toClick = pyautogui.locateCenterOnScreen("trainable.png", confidence=0.6)
    except Exception:
        time.sleep(1)
        click("x.png", 0.8)
        searchMode()
    else:
        try:
            pyautogui.moveTo(toClick, duration=0.2)
            pyautogui.leftClick()
            time.sleep(0.2)
            toClick = pyautogui.locateCenterOnScreen("train2.png", confidence=0.75)
            pyautogui.moveTo(toClick, duration=0.2)
            pyautogui.leftClick()
            time.sleep(0.3)
            toClick = pyautogui.locateCenterOnScreen("continuebtn.png", confidence=0.75)
            pyautogui.moveTo(toClick, duration=0.2)
            pyautogui.leftClick()
            time.sleep(0.5)
            try:
                toClick = pyautogui.locateCenterOnScreen(
                    "continuebtn2.png", confidence=0.75
                )
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
                toClick = pyautogui.locateCenterOnScreen(
                    "continuebtn2.png", confidence=0.5
                )
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
                toClick = pyautogui.locateCenterOnScreen("skipbtn.png", confidence=0.75)
                pyautogui.moveTo(toClick, duration=0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
            except Exception:
                train()
        except Exception:
            train()


def checkActive():
    try:
        pyautogui.locateOnScreen("appname.png", confidence=0.75)
    except Exception:
        print("Game is minimized, concluding process...")
        time.sleep(0.5)
        conclude()


def conclude():
    print(f"Ended process after {b} Miscrits fought.")
    print(f"Runtime: {time.time()-start}")
    sys.exit("Ending process.")


time.sleep(1)
searchMode()
sys.exit("Ended.")
