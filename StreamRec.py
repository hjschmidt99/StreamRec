import HandleConsole as con
import sys
import os
import json
import subprocess
import traceback
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import win32gui, win32con
import eel
import clipboard
import scheduler

eel.init('web')

# default app parameters
xparam = {
    "x": 50,
    "y": 50, 
    "w": 800,
    "h": 500,
    "port": 0,
    "txtDir": r"%USERPROFILE%\Videos",
    "txtPlayer": r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe",
    "txtOffset": "15",
    "txtCmdFile": "",
    "txtChannelFile": "",
    "chkSavePlaylist": False,
}

tFormatUi = "%d.%m.%Y %H:%M"

# load parameter file, always merge to xparam
fn = os.path.splitext(os.path.abspath(sys.argv[0]))[0]
fncfg = fn + ".json"
fncmd = fn + ".cmd"
fnchan = fn + ".m3u8"
if os.path.exists(fncfg):
    with open(fncfg, 'r') as f1:
        x = json.load(f1)
    for k in x.keys():
        xparam[k] = x[k]

if xparam["txtCmdFile"] == "":
    xparam["txtCmdFile"] = fncmd
if xparam["txtChannelFile"] == "":
    xparam["txtChannelFile"] = fnchan

cUrl = "url"
cArgs1 = "args1"
cArgs2 = "args2"

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
    global fncmd
    modes = []
    fncmd = xparam["txtCmdFile"]
    if os.path.exists(fncmd):
        with open(fncmd, 'r') as f1:
            t = f1.read()
        for x in t.split("\n"):
            if x.startswith(":mode_"):
                m = x.strip()[6:]
                modes.append(m)
    return modes

# get channels from file
def getChannels():
    global fnchan
    fnchan = xparam["txtChannelFile"]
    if fnchan.endswith(".pls"):
        return getChannelsPls(fnchan)
    if fnchan.endswith(".m3u8"):
        return getChannelsM3u(fnchan)

# get channels from pls file
# (opt. pls extensions Args1_x and Args2_x)
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
            a1 = f'Args1_{i}'
            a2 = f'Args2_{i}'
            if k in pls.keys() and v in pls.keys(): 
                data = { cUrl: pls[v] }
                if a1 in pls.keys(): data[cArgs1] = pls[a1]
                if a2 in pls.keys(): data[cArgs2] = pls[a2]
                channels[pls[k]] = data
    return list(channels.keys())

# get channels from m3u file
# (opt. m3u extensions #EXTARGS1 and #EXTARGS2)
def getChannelsM3u(fname):
    global channels
    channels = {}
    name = ""
    data = {}
    if os.path.exists(fname):
        with open(fname, 'r', encoding="utf-8") as f1:
            while True:
                x1 = f1.readline()
                if not x1: break
                x1 = x1.strip()
                if x1.startswith("#EXTINF:"):
                    a = x1.split(",", 1)
                    if len(a) == 2: 
                        if name != "":
                            channels[name] = data
                        name = a[1].strip()
                        data = {}
                elif x1.startswith("#EXTARGS1:"):
                    data[cArgs1] = x1.partition(":")[2]
                elif x1.startswith("#EXTARGS2:"):
                    data[cArgs2] = x1.partition(":")[2]
                elif x1.startswith("http"):
                    data[cUrl] = x1
            if name != "":
                channels[name] = data

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
def doCreate(chan, mode, start, end, title, useMaps, fullTimeshift):
    try:
        c = channels[chan]
        url = c[cUrl]
        args1 = c[cArgs1] if cArgs1 in c.keys() else "" 
        if fullTimeshift: args1 += " -live_start_index 1"
        args2 = "" if not useMaps else c[cArgs2] if cArgs2 in c.keys() else "" 
        tstart = datetime.strptime(start, tFormatUi)
        tend = datetime.strptime(end, tFormatUi)
        now = datetime.now()
        if tstart < now: tstart = now + timedelta(seconds=5)
        if tend < now: tend = now + timedelta(minutes=6)
        
        taskname = toFilename(f'Rec_{tstart.isoformat()}_{chan} - {title}')
        destfile = f'{xparam["txtDir"]}\\{taskname}.ts'
        folder = "\\Record"
        exe = "cmd.exe"
        args = f'/s /c ""{fncmd}" "{url}" "{destfile}" mode_{mode} "{args1}" "{args2}""'

        s = f'\nscheduled task:\n  folder: {folder}\n  taskname: {taskname}\n'
        s += f'  start: {datetime.strftime(tstart, tFormatUi)}\n'
        s += f'  end: {datetime.strftime(tend, tFormatUi)}\n'
        s += f'  exe: {exe}\n'
        s += f'  args: {args}'
        eel.prl(s)
        
        scheduler.createTask(folder, taskname, tstart, tend, exe, args)
    except:
        traceback.print_exc()

# paste event from clipboard, e.g. copied from TV-Browser
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
    if (s == "Play"): cmd = f'"{xparam["txtPlayer"]}" "{channels[p][cUrl]}"'
    if (s == "Tasks"): cmd = f'taskschd.msc'
    if (s == "PlayList"): log = getPlayist(p)
    if (s == "Console"): con.showConsole(con.conToggle)
    if (s == "Paste"): paste()
    if cmd:
        log = f'\ndoCmd ({s}, {p})\n{cmd}'
        subprocess.Popen(cmd, shell=True)
    if log: eel.prl(log)
    #return(log)

def getPlayist(chan):
    url = channels[chan][cUrl]
    p1 = ""
    if not xparam["chkSavePlaylist"]: 
        with urllib.request.urlopen(url) as response:
            rsp = response.read()
        p1 = rsp.decode("utf-8")
    else:
        p1 = processM3u(chan, url, xparam["txtDir"])
    s = f'\nChannel: {chan}\n{url}\n{p1}\n\n'
    print(s)
    return s

def processM3u(chan, url, dir):
    with urllib.request.urlopen(url) as response:
        rsp = response.read()
    p = rsp.decode("utf-8")
    p1 = p.splitlines()

    savenext1 = False
    savenext2 = False
    for ix1, x1 in enumerate(p1):
        if savenext1 or savenext2:
            url2 = x1
            # make relative urls absolute
            if not url2.startswith("http"):
                url2 = url.rsplit("/", 1)[0] + "/" + url2
                p1[ix1] = url2

            if savenext1:
                processM3u(chan, url2, dir)

        savenext1 = x1.startswith("#EXT-X-STREAM-INF") 
        savenext2 = x1.startswith("#EXTINF")

    fn1 = url.split("?")[0]
    fn1 = toFilename(chan) + "-" + os.path.basename(fn1)
    fn1 = os.path.join(dir, fn1)
    with open(fn1, 'w') as f1:
        f1.write("\n". join(p1))

    return p

#cmdline_args = []    
cmdline_args = ["–disable-translate", "–incognito", 
    f"--window-position={xparam['x']},{xparam['y']}", 
    f"--window-size={xparam['w']-20},{xparam['h']}"]
eel.start('main.html', 
    cmdline_args=cmdline_args, 
    port=xparam["port"], 
    position=(xparam["x"], xparam["y"]), 
    size=(xparam["w"], xparam["h"]),
    block=True)

#while (True): eel.sleep(1)
