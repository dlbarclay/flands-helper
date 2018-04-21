@echo off
pyinstaller --noconfirm --log-level=WARN ^
    --onefile --noconsole --icon "res/tickbox.ico" ^
    --add-data="res;res" ^
    flandshelper.py

