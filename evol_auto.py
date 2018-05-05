"""
EVOL_auto dependencies
1.Pillow
    pip install Pillow
2.ADB
    replace the original adb if doesn't work
"""
import ctypes
import os
import sys
import time
import random
import subprocess
from PIL import Image
from common import screenshot
global talkcount, markx, marky, lastspec
talkcount = 0


def yes_or_no(prompt, true_value='y', false_value='n', default=True):
    """
    prompt connect adb
    """
    default_value = true_value if default else false_value
    prompt = '{} {}/{} [{}]: '.format(prompt, true_value, false_value,
                                      default_value)
    i = input(prompt)
    if not i:
        return default
    while True:
        if i == true_value:
            return True
        elif i == false_value:
            return False
        prompt = 'Please input {} or {}: '.format(true_value, false_value)
        i = input(prompt)


def pixel_match(im,
                target_x,
                target_y,
                target_r,
                target_g,
                target_b,
                diff,
                debug=False):
    pixel = im.getpixel((target_x, target_y))
    if debug:
        print([target_x, target_y], pixel, [target_r, target_g, target_b])
    if abs(pixel[0] - target_r) + abs(pixel[1] - target_g) + abs(
            pixel[2] - target_b) <= diff:
        return True
    else:
        return False


# we face a selection
def detect_selection(im):
    if detect_main_menu(im):
        return False
    for cy in range(192, 1000):
        if pixel_match(im, 220, cy, 250, 125, 147, 30) and pixel_match(
                im, 680, cy, 250, 125, 147, 30) and pixel_match(
                    im, 890, cy, 250, 125, 147, 30):
            return True
    return False


# if we have arrived and thereis a locator
def detect_loc(im):
    global markx, marky
    if not detect_main_menu(im):
        return False
    for x in range(400, 1000):
        for y in range(480, 1000):
            if pixel_match(im, x, y, 220, 115, 140, 30) and pixel_match(
                    im, x, y + 50, 220, 115, 140, 30) and (not pixel_match(
                        im, x, y + 200, 220, 115, 140, 30)):
                markx = x
                marky = y
                return True
    return False


# whether we have finished all tasks
def detect_comp(im):
    global routcount
    return ((routcount > 20) and detect_main_menu(im))


# go through the endless talk
def do_talk():
    for _ in range(0, 10):
        tap(321 + drift(), 1443 + drift())


# returns whether we are in a talk
def in_talk(im):
    global talkcount
    talkcount += 1
    return (not detect_main_menu(im)) and (pixel_match(im, 912, 1819, 247, 128,
                                                       151, 80))


# we are in the main screen
def detect_main_menu(im):
    matchdiamond = False
    matchplus = False
    for y in range(0, 100):
        for x in range(760, 950):
            if pixel_match(im, x, y, 187, 30, 72, 3):
                matchdiamond = True
        for x in range(970, 1080):
            if pixel_match(im, x, y, 189, 156, 130, 3):
                matchplus = True
    return (matchdiamond and matchplus)


# add some drift to prevent being detected
def drift():
    return random.uniform(10, 30)


# adb tap wrapper
def tap(px, py):
    global lastspec, need_resize, height, width
    if not (px == 956):
        lastspec = True
    else:
        lastspec = False
    if need_resize:
        px *= width
        py *= height
    cmd = 'adb shell input tap {x} {y}'.format(x=px, y=py)
    if "win" in sys.platform:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(cmd, startupinfo=si)
    else:
        subprocess.Popen(cmd, shell=True)
    time.sleep(0.1)


# select one option
def do_sel():
    print("selecting...")
    tap(781, 690 - drift())
    time.sleep(2)


# enter the place we arrived
def sel_loc():
    print("arrived...")
    tap(markx + 10 + drift(), marky + drift())
    time.sleep(2)


# randomly select one choice when we face a 1 in 3 quesion
def do_3sel(im):
    global talkcount
    print("3sel!!!")
    while not detect_main_menu(im):
        im.close()
        im = do_screenshot()
        for _ in range(10):
            tap(956, 1870)
            time.sleep(0.1)
        time.sleep(1.5)
        tap(random.choice((200, 540, 880)), 750 + drift())
        time.sleep(3)
    talkcount = 0


'''determine the current status
sorry it cant detect 1 in 3 selections so
that one is not included here'''


def Determine_status(im):
    global talkcount, routcount
    if detect_selection(im) and (not lastspec):
        do_sel()
    elif detect_loc(im) and (not lastspec):
        sel_loc()
    elif detect_comp(im) and (not lastspec):
        print("Current process is complete!")
        sys.exit()
    elif in_talk(im):
        routcount = 0
        print("Talk...")
        do_talk()
    else:
        talkcount = 0
        routcount += 1
        print("routine...")
        for _ in range(10):
            tap(956, 1870)
            time.sleep(0.1)


# screenshot getter
def do_screenshot():
    global need_resize, need_rotate, height, width
    print("Pull_screenshot...", end=" ")
    try:
        im = screenshot.pull_screenshot()
        success = True
    except:
        success = False
        try:
            im = screenshot.pull_screenshot()
            success = True
        except:
            print("screenshot_error")
    if success:
        if need_rotate:
            print("Rotating...", end=" ")
            im = im.transpose(Image.ROTATE_90)
            width = width + height
            height = width - height
            width = width - height
        if need_resize:
            print("Resizing...", end=" ")
            im = im.resize((1080, 1920))
    return im


def main():
    global talkcount, routcount, need_resize, need_rotate, height, width
    op = yes_or_no('remote adb?', default=False)
    if op:
        netpos = input()
        cmd = 'adb connect {x}'.format(x=netpos, )
        os.system(cmd)
    screenshot.check_screenshot()
    im = screenshot.pull_screenshot()
    width, height = im.size
    need_rotate = False
    need_resize = False
    if width > height:
        print("Need rotate!")
        need_rotate = True
        im = im.transpose(Image.ROTATE_90)
        width = width + height
        height = width - height
        width = width - height
    if (width != 1080) or (height != 1920):
        print("Need resize!")
        need_resize = True
    im.close()
    width = width / 1080
    height = height / 1920
    tap(956, 1870)
    talkcount = 0
    routcount = 0
    while True:
        im = do_screenshot()
        print("Parsing...", end=" ")
        Determine_status(im)
        if (not detect_main_menu(im)) and ((talkcount >= 15)):
            do_3sel(im)
        im.close()


main()
