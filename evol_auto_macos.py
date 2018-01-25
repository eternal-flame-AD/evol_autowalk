"""
EVOL_auto dependencies
1.Pillow
    pip install Pillow
2.ADB
    replace the original adb if doesn't work
"""
#from __future__ import print_function, division
import ctypes
import os
import sys
import time
#import math
import random
import subprocess
from PIL import Image
#from six.moves import input
from common import screenshot
global routcount,markx,marky,lastspec
routcount=0
def yes_or_no(prompt, true_value='y', false_value='n', default=True):
    """
    prompt connect adb
    """
    default_value = true_value if default else false_value
    prompt = '{} {}/{} [{}]: '.format(prompt, true_value,
        false_value, default_value)
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
def pixel_match(im,target_x,target_y,target_r,target_g,target_b,diff,debug=False):
    """
    try:
        im_pixel=im.load()
    except:
        return False
    pixel=im_pixel[target_x,target_y]
        old method
    """
    pixel=im.getpixel((target_x,target_y))
    if debug:
        print([target_x,target_y],pixel,[target_r,target_g,target_b])
    if abs(pixel[0]-target_r)+abs(pixel[1]-target_g)+abs(pixel[2]-target_b)<=diff:
        return True
    else:
        return False
def detect_selection(im):
    if detect_main_menu(im):
        return False
    for cy in range(192,1000):
        if pixel_match(im,220,cy,250,125,147,30) and pixel_match(im,680,cy,250,125,147,30) and pixel_match(im,890,cy,250,125,147,30):
            return True
    return False
def detect_loc(im): #228 117 191 220 115 140
    global markx,marky
    if not detect_main_menu(im):
        return False
    for x in range(400,1000):
        for y in range(480,1000):
            if pixel_match(im,x,y,220,115,140,30) and pixel_match(im,x,y+50,220,115,140,30) and (not pixel_match(im,x,y+200,220,115,140,30)):
                    markx=x
                    marky=y
                    return True
    return False
def detect_comp(im):
    global routcount
    return ((routcount>300) and detect_main_menu(im))
def detect_main_menu(im):
    matchdiamond=False
    matchplus=False
    for y in range(0,100):
        for x in range(760,950):
            if pixel_match(im,x,y,187,30,72,3):
                matchdiamond=True
        for x in range(970,1080):
            if pixel_match(im,x,y,189,156,130,3):
                matchplus=True
    return (matchdiamond and matchplus)
def drift():
    return random.uniform(10,30)
def tap(px,py):
    global lastspec,routcount,need_resize,height,width
    if not (px==956):
        lastspec=True
        routcount=0
    else:
        lastspec=False
        routcount+=1
    if need_resize:
        px*=width
        py*=height
#    si = subprocess.STARTUPINFO()
#    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
#si.wShowWindow = subprocess.SW_HIDE # default
    cmd = 'adb shell input tap {x} {y}'.format(
        x=px,
        y=py
    )
#    print(cmd)
#    print(routcount)
    subprocess.Popen(cmd,shell=True)
#·    os.system(cmd)
def do_sel():
    print("selecting...")
    tap(781,690-drift())
def sel_loc():
    print("arrived...")
    tap(markx+10+drift(),marky+drift())
def do_3sel(im):
    global routcount
    print("3sel!!!")
    while not detect_main_menu(im):
        im.close()
        im=do_screenshot()
        for i in range(10):
            tap(956,1870)
            time.sleep(0.1)
        time.sleep(1.5)
        tap(random.choice((200,540,880)),750+drift())
        time.sleep(3)
    routcount=0
def Determine_status(im):
    if detect_selection(im) and (not lastspec):
        do_sel()
    elif detect_loc(im) and (not lastspec):
        sel_loc()
    elif detect_comp(im) and (not lastspec):
#        ctypes.windll.user32.MessageBoxW(0, "Current process is complete!", "Complete!", 0)
        print("Current process is complete!")
        sys.exit()
    else:
        print("routine...")
        for i in range(10):
            tap(956,1870)
            time.sleep(0.1)
def do_screenshot():
    global need_resize,need_rotate,height,width
    print("Pull_screenshot...",end=" ")
    screenshot.pull_screenshot()
    try:
        im = Image.open('./autojump.png')
        success=True
    except:
        success=False
        try:
            screenshot.pull_screenshot()
            im = Image.open('./autojump.png')
            success=True
        except:
            print("screenshot_error")
    if success:
        if need_rotate:
            print("Rotating...",end=" ")
            im=im.transpose(Image.ROTATE_90)
            width=width+height
            height=width-height
            width=width-height
        if need_resize:
            print("Resizing...",end=" ")
            im=im.resize((1080,1920))
    return im
def main():
    global routcount,need_resize,need_rotate,height,width
    op = yes_or_no('remote adb?')
    if op:
        netpos=raw_input()
        cmd = 'adb connect {x}'.format(
            x=netpos,
        )
        os.system(cmd)
    sel=0
#    debug.dump_device_info()
    screenshot.check_screenshot()
    screenshot.pull_screenshot()
    im = Image.open('./autojump.png')
    width,height=im.size
    need_rotate=False
    need_resize=False
    if width>height:
            print("Need rotate!")
            need_rotate=True
            im=im.transpose(Image.ROTATE_90)
            width=width+height
            height=width-height
            width=width-height
    if (width!=1080) or (height!=1920):
            print("Need resize!")
            need_resize=True
    im.close()
    width=width/1080
    height=height/1920
    tap(956,1870)
    routcount=0
    while True:
        im=do_screenshot()
        print("Parsing...",end=" ")
        Determine_status(im)
        if (not detect_main_menu(im)) and ((routcount==151) or (routcount==150)):  
            do_3sel(im)
    #     time.sleep(random.uniform(0.1, 0.5))
        im.close()
main()
