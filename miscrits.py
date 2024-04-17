import pyautogui, pyscreeze, time, keyboard, sys

b = 0
start = time.time()

# SELECT WHICH TWO ELEMENTS TO SEARCH IN ALTERNATION
fward = "eldertree.png"
bward = "eldershrub.png"

def searchMode(b,fward,bward):
    checkActive(b,fward,bward)
    try:
        while pyautogui.locateOnScreen("expmultiplier.png", confidence = 0.9) != None:
            try:
                toClick = pyautogui.locateCenterOnScreen(fward, confidence = 0.9)
                pyautogui.moveTo(toClick, duration = 0.2)
                pyautogui.leftClick()
                time.sleep(4)
                try:
                    pyautogui.locateOnScreen("expmultiplier.png", confidence = 0.8)
                    searchMode(b,fward,bward)
                except Exception:
                    # print("Entering battle mode. Waiting for battle to finish...")
                    battleMode(b,fward,bward)
            except Exception:
                try:
                    toClick = pyautogui.locateCenterOnScreen(bward, confidence = 0.9)
                    pyautogui.moveTo(toClick, duration = 0.2)
                    pyautogui.leftClick()
                    time.sleep(4)
                    try:
                        pyautogui.locateOnScreen("expmultiplier.png", confidence = 0.8)
                        searchMode(b,fward,bward)
                    except Exception:
                        # print("Entering battle mode. Waiting for battle to finish...")
                        battleMode(b,fward,bward)
                except Exception:
                    checkActive(b,fward,bward)
                    print("Elements not found, concluding process...")
                    conclude(b)
        else:
            conclude(b)
    except Exception:
        conclude(b)

def battleMode(b,fward,bward):
    checkActive(b,fward,bward)
    try:
        pyautogui.locateOnScreen("miscripedia.png", confidence = 0.8)
        time.sleep(0.1)
        try:   
            toClick = pyautogui.locateCenterOnScreen("run.png", confidence = 0.99)
            pyautogui.moveTo(toClick, duration = 0.2)
            try:
                pyautogui.locateOnScreen("nature.png")
                pyautogui.leftClick()
            except Exception:
                pyautogui.moveRel(115,80)
                pyautogui.leftClick()
                pyautogui.moveTo(toClick, duration = 0.2)
        except Exception:
            battleMode(b,fward,bward)
        battleMode(b,fward,bward)
    except Exception:
        b += 1
        # print("Battle done.")
        time.sleep(0.5)
        summary(b,fward,bward)

def summary(b,fward,bward):
    checkActive(b,fward,bward)
    try: 
        try:
            pyautogui.locateOnScreen("trainable.png", confidence = 0.6)
            trainable = True
        except Exception:
            trainable = False
        
        pyautogui.locateOnScreen("closebtn.png", confidence = 0.9)
        time.sleep(1)
        pyautogui.moveTo(pyautogui.locateOnScreen("closebtn.png", confidence = 0.85), duration = 0.1)
        pyautogui.leftClick()
        time.sleep(1)
        
        if trainable == True:
            try:
                toClick = pyautogui.locateCenterOnScreen("train.png", confidence = 0.75)
                pyautogui.moveTo(toClick, duration = 0.2)
                pyautogui.leftClick()
                time.sleep(1)
                train(b,fward,bward)
            except Exception:
                searchMode(b,fward,bward)
        else:
            searchMode(b,fward,bward)
    except Exception:
        time.sleep(1)
        summary(b,fward,bward)
        
def train(b,fward,bward):
    checkActive(b,fward,bward)
    try:
        toClick = pyautogui.locateCenterOnScreen("trainable.png", confidence = 0.6)
    except Exception:
        time.sleep(1)
        toClick = pyautogui.locateCenterOnScreen("x.png", confidence = 0.8)
        pyautogui.moveTo(toClick, duration = 0.2)
        pyautogui.leftClick()
        time.sleep(0.2)
        searchMode(b,fward,bward)
    else:
        try:
            pyautogui.moveTo(toClick, duration = 0.2)
            pyautogui.leftClick()
            time.sleep(0.2)
            toClick = pyautogui.locateCenterOnScreen("train2.png", confidence = 0.75)
            pyautogui.moveTo(toClick, duration = 0.2)
            pyautogui.leftClick()
            time.sleep(0.3)
            toClick = pyautogui.locateCenterOnScreen("continuebtn.png", confidence = 0.75)
            pyautogui.moveTo(toClick, duration = 0.2)
            pyautogui.leftClick()
            time.sleep(0.5)
            try:
                toClick = pyautogui.locateCenterOnScreen("continuebtn2.png", confidence = 0.75)
                pyautogui.moveTo(toClick, duration = 0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
                toClick = pyautogui.locateCenterOnScreen("continuebtn2.png", confidence = 0.5)
                pyautogui.moveTo(toClick, duration = 0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
                toClick = pyautogui.locateCenterOnScreen("skipbtn.png", confidence = 0.75)
                pyautogui.moveTo(toClick, duration = 0.2)
                pyautogui.leftClick()
                time.sleep(0.3)
            except Exception:
                train(b,fward,bward)
        except Exception:
            train(b,fward,bward)

def checkActive(b,fward,bward):
    try:
        pyautogui.locateOnScreen("appname.png", confidence = 0.75)
    except Exception:
        print("Game is minimized, concluding process...")
        time.sleep(0.5)
        conclude(b)

def conclude(b):
    print(f"Ended process after {b} Miscrits fought.")
    print(f"Runtime: {time.time()-start}")
    sys.exit("Ending process.")

time.sleep(1)
searchMode(b,fward,bward)
sys.exit("Ended.")