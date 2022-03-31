import sys
import os
import json
import subprocess
import traceback
import urllib
import datetime
import win32gui, win32con
import win32com.client
import eel
import clipboard
import scheduler

# console visibility
conWin = win32gui.GetForegroundWindow()
conOn = win32con.SW_SHOW
conOff = win32con.SW_HIDE
conToggle = -1
def showConsole(mode):
    global conState
    mode = mode if mode != -1 else conOff if conState == conOn else conOn
    conState = mode
    if not "debugSession" in os.environ.keys():
        win32gui.ShowWindow(conWin, mode)
showConsole(conOff)

eel.init('web')

# default app parameters
xparam = {
    "x": 50,
    "y": 50, 
    "w": 400,
    "h": 400,
    "port": 0,
    "txtDir_mru": ["D:\\Download\\Media"],
}

# load parameter file, always merge to xparam
fn = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
fncfg = fn + ".json"
fncmd = fn + ".cmd"
fnpls = fn + ".pls"
if os.path.exists(fncfg):
    with open(fncfg, 'r') as f1:
        x = json.load(f1)
    for k in x.keys():
        xparam[k] = x[k]

@eel.expose
def saveParams(x):
    for k in x.keys():
        xparam[k] = x[k]
    with open(fncfg, 'w') as f1:
        json.dump(xparam, f1, indent=4)
    return xparam

@eel.expose
def loadParams():
    xparam["selMode_values"] = getModes()
    xparam["selChan_values"] = getChannels()
    dump(xparam)
    return xparam

# get modes from cmd file
def getModes():
    modes = []
    if os.path.exists(fncmd):
        with open(fncmd, 'r') as f1:
            t = f1.read()
        for x in t.split("\n"):
            if x.startswith(":mode_"):
                m = x.strip()[6:]
                modes.append(m)
    return modes

# get channess from pls file
def getChannels():
    global channels
    channels = {}
    if os.path.exists(fnpls):
        with open(fnpls, 'r') as f1:
            t = f1.read()
        pls = {}
        for x in t.split("\n"):
            a = x.split("=", 1)
            if len(a) == 2: pls[a[0]] = a[1]
        for i in range(1, int(len(pls.keys()) / 2)):
            k = f'Title{i}'
            v = f'File{i}'
            if k in pls.keys() and v in pls.keys(): 
                channels[pls[k]] = pls[v]
    return list(channels.keys())

def dump(o):
    print(json.dumps(o, indent=4))

# makew string a valid filename
def toFilename(s):
    s = s.replace("\r", "")
    s = s.replace("\n", " - ")
    s = s.replace("\t", " ")
    s = s.replace("?", " ")
    s = s.replace(":", "-")
    s = s.replace("\"", "-")
    s = s.replace("/", "-")
    s = s.replace(".", "-")
    s = s.replace(",", "-")
    s = s.replace(";", "-")
    s = s.replace("  ", " ")
    return s.strip()

# create task
@eel.expose
def doCreate(chan, mode, start, end, title):
    try:
        tFormatUi = "%d.%m.%Y %H:%M:%S"
        url = channels[chan]
        tstart = datetime.datetime.strptime(start, tFormatUi)
        tend = datetime.datetime.strptime(end, tFormatUi)
        taskname = toFilename(f'Rec_{tstart.isoformat}_{chan} - {title}')
        destfile = f'{xparam["txtDir"]}\\{taskname}.ts'
        folder = "\\Record"
        xtool = "cmd.exe"
        xargs = f'/s /c ""{fncmd}" {url} "{destfile}" mode_{mode}"'
        scheduler.createTask(folder, taskname, tstart, tend, xtool, xargs)
    except:
        traceback.print_exc()

@eel.expose
def doCmd(s, p = None):
    print(f'doCmd {s}, {p}')
    if (s == "CmdFile"): subprocess.Popen(f'notepad.exe "{fncmd}"', shell=True)
    if (s == "PlsFile"): subprocess.Popen(f'notepad.exe "{fnpls}"', shell=True)
    if (s == "Console"): showConsole(conToggle)
    
eel.start('main.html', 
    cmdline_args=["--window-position=8000,0"], 
    port=xparam["port"], 
    position=(xparam["x"], xparam["y"]), 
    size=(xparam["w"], xparam["h"]),
    block=True)

