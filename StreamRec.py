import sys
import os
import json
import subprocess
import traceback
import urllib.request
from datetime import datetime, timedelta
import win32gui, win32con
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
    "w": 800,
    "h": 500,
    "port": 0,
    "txtDir": r"D:\Download\\Media",
    "txtPlayer": r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe",
    "txtOffset": "15",
}

tFormatUi = "%d.%m.%Y %H:%M"

# load parameter file, always merge to xparam
fn = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
fncfg = fn + ".json"
fncmd = fn + ".cmd"
fnpls = fn + ".pls"
fnm3u = fn + ".m3u8"
fnchan = fnpls
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
    xparam["selChan_values"] = getChannels(fnchan)
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

# get channess from file
def getChannels(fname):
    if fname.endswith(".pls"):
        return getChannelsPls(fname)
    if fname.endswith(".m3u8"):
        return getChannelsM3u(fname)

# get channess from pls file
def getChannelsPls(fname):
    global channels
    channels = {}
    if os.path.exists(fname):
        with open(fname, 'r', encoding="utf-8") as f1:
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

# get channess from m3u file
def getChannelsM3u(fname):
    global channels
    channels = {}
    if os.path.exists(fname):
        with open(fname, 'r', encoding="utf-8") as f1:
            while True:
                x1 = f1.readline()
                if not x1: break
                if x1.startswith("#EXTINF:"):
                    a = x1.split(",", 1)
                    x2 = f1.readline()
                    if not x2: break
                    if len(a) == 2: 
                        channels[a[1].strip()] = x2.strip()
    return list(channels.keys())

def dump(o):
    print(json.dumps(o, indent=4))

# make string a valid filename
def toFilename(s):
    s = s.replace("\r", "")
    s = s.replace("\n", " - ")
    s = s.replace("\t", " ")
    s = s.replace("?", " ")
    s = s.replace("*", " ")
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
        url = channels[chan]
        tstart = datetime.strptime(start, tFormatUi)
        tend = datetime.strptime(end, tFormatUi)
        now = datetime.now()
        if tstart < now: tstart = now + timedelta(seconds=5)
        if tend < now: tend = now + timedelta(minutes=6)
        
        taskname = toFilename(f'Rec_{tstart.isoformat()}_{chan} - {title}')
        destfile = f'{xparam["txtDir"]}\\{taskname}.ts'
        folder = "\\Record"
        exe = "cmd.exe"
        args = f'/s /c ""{fncmd}" {url} "{destfile}" mode_{mode}"'

        s = f'\nscheduled task:\n  folder: {folder}\n  taskname: {taskname}\n'
        s += f'  start: {datetime.strftime(tstart, tFormatUi)}\n'
        s += f'  end: {datetime.strftime(tend, tFormatUi)}\n'
        s += f'  exe: {exe}\n'
        s += f'  args: {args}'
        eel.prl(s)
        
        scheduler.createTask(folder, taskname, tstart, tend, exe, args)
    except:
        traceback.print_exc()

def paste():
    try:
        s = clipboard.paste()
        print(s)
        # 12.04.2019 21:45–23:20 - ARD-alpha - Fawlty Towers
        s = s.replace("–", "-").strip()
        a = s.split(" - ", 2)
        if len(a) != 3: return
        chan = a[1]
        title = a[2]
        dt = a[0].split(" ")
        ta = dt[1].split("-")
        t1 = f'{dt[0]} {ta[0]}'
        t2 = f'{dt[0]} {ta[1]}'
        tstart = datetime.strptime(t1, tFormatUi)
        tend = datetime.strptime(t2, tFormatUi)
        if ta[0] > ta[1] : tend += timedelta(days=1)
        offset = timedelta(minutes=int(xparam["txtOffset"]))
        tstart = datetime.strftime(tstart - offset, tFormatUi)
        tend = datetime.strftime(tend + offset, tFormatUi)
        eel.prl(f'\npaste from clipboard:\n{s}')
        eel.pasteResult(tstart, tend, chan, title)
    except:
        traceback.print_exc()

@eel.expose
def doCmd(s, p):
    print(f'doCmd {s}, {p}')
    cmd = None
    log = ""
    if (s == "CmdFile"): cmd = f'notepad.exe "{fncmd}"'
    if (s == "ChanFile"): cmd = f'notepad.exe "{fnchan}"'
    if (s == "Play"): cmd = f'"{xparam["txtPlayer"]}" "{channels[p]}"'
    if (s == "Tasks"): cmd = f'taskschd.msc'
    if (s == "PlayList"): log = getPlayist(p)
    if (s == "Console"): showConsole(conToggle)
    if (s == "Paste"): paste()
    if cmd:
        log = f'\ndoCmd ({s}, {p})\n{cmd}'
        subprocess.Popen(cmd, shell=True)
    if log: eel.prl(log)
    #return(log)

def getPlayist(chan):
    url = channels[chan]
    with urllib.request.urlopen(url) as response:
        rsp = response.read()
    s = f'\nChannel: {chan}\n{url}\n{rsp.decode("utf-8")}\n\n'
    print(s)
    return s


eel.start('main.html', 
    cmdline_args=["--window-position=8000,0"], 
    port=xparam["port"], 
    position=(xparam["x"], xparam["y"]), 
    size=(xparam["w"], xparam["h"]),
    block=True)

#while (True): eel.sleep(1)
