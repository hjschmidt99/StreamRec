# for quick hiding on startup import this file first
import os
import sys
import win32gui, win32con, win32console
from io import StringIO

# workaround to avoid errors on --noconsole
if sys.stdout is None:
    sys.stdout = StringIO()
if sys.stderr is None:
    sys.stderr = StringIO()

conWin = None
if not getattr(sys, 'frozen', False):
    conWin = win32console.GetConsoleWindow()
    
# console visibility
conOn = win32con.SW_SHOW
conOff = win32con.SW_HIDE
conToggle = -1
def showConsole(mode):
    global conState
    mode = mode if mode != -1 else conOff if conState == conOn else conOn
    conState = mode
    # avoid console hiding in debugger by setting "debugSession" in launch.json "env"
    if not "debugSession" in os.environ.keys() and conWin:
        win32gui.ShowWindow(conWin, mode)
showConsole(conOff)
