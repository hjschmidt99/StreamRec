pyinstaller.exe --onefile ^
    --add-data="web;web" ^
    streamrec.py
copy /y StreamRec.cmd dist\streamrec.cmd
copy /y StreamRec.m3u8 dist\streamrec.m3u8
pause