#!/usr/bin/env python3

import os

DEBUG_PRINT_ON=False

def setDebugPrint(on):
    global DEBUG_PRINT_ON
    DEBUG_PRINT_ON = bool(on)

def dprint(*args, **nargs):
    global DEBUG_PRINT_ON
    if (DEBUG_PRINT_ON):
        print(*args, **nargs)

