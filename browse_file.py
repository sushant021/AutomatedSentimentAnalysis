# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 13:38:30 2019

@author: nsush
"""

import tkinter 
from tkinter import messagebox 
from tkinter import filedialog

#initiate tinker and hide window 
main_win = tkinter.Tk() 
main_win.withdraw()

main_win.overrideredirect(True)
main_win.geometry('0x0+0+0')

main_win.deiconify()
main_win.lift()
main_win.focus_force()

#open file selector 
main_win.sourceFile = filedialog.askopenfilename(parent=main_win, initialdir= "/",
title='Please select a directory')

#close window after selection 
main_win.destroy()

#print path 
print(main_win.sourceFile )