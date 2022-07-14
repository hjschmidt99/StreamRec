pyinstaller.exe --onefile ^
    --add-data="web;web" ^
    streamrec.py
copy /y StreamRec.cmd dist\streamrec.cmd
copy /y StreamRec.pls dist\streamrec.pls
pause