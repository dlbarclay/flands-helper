#!/usr/bin/env bash
pyinstaller --noconfirm --log-level=WARN \
    --onefile --noconsole --icon "res/tickbox.ico" \
    --add-data="res:res" \
    --add-data="res:res" \
    flandshelper.py

