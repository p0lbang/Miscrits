import threading
import mouse
import keyboard

mouse_events = []

mouse.hook(mouse_events.append)

keyboard.wait("a")
mouse.unhook(mouse_events.append)

m_thread = threading.Thread(target = lambda :mouse.play(mouse_events))
m_thread.start()