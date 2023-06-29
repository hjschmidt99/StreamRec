# for quick hiding on startup import this file first
import os
import win32gui, win32con

# console visibility
conWin = win32gui.GetForegroundWindow()
conOn = win32con.SW_SHOW
conOff = win32con.SW_HIDE
conToggle = -1
def showConsole(mode):
    global conState
    mode = mode if mode != -1 else conOff if conState == conOn else conOn
    conState = mode
    # avoid console hiding in debugger by setting "debugSession" in launch.json "env"
    if not "debugSession" in os.environ.keys():
        win32gui.ShowWindow(conWin, mode)
showConsole(conOff)
