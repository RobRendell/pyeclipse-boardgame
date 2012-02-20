'''
Created on 11 janv. 2012

@author: jglouis
'''
#The game was succesfully build under win7 and Ubuntu. for Ubuntu, it may be required to update
#the cx freeze version to the newest one (tested with the 4.1.3)

from cx_Freeze import setup, Executable
import sys, os

path = sys.path + ['engine', 'gui', 'material', 'tool', 'data', 'image', 'font']
includes =  []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
includefiles = ['data', 'image', 'font']
path = []

exe = Executable(
    script = 'eclipse.py',
    initScript = None,
    base = 'Win32GUI' if sys.platform == 'win32' else None,
    #base = None,
    icon = os.path.abspath('image/eclipse.ico')
    )

setup(
    
    version = '0.1',
    description = 'Eclipse Cx_Freeze Build',
    author = 'jglouis',
    name = 'cx_Freeze Sample File',
    
    options = {'build_exe': {'path':path,
                             'includes': includes,
                             'excludes': excludes,
                             'packages': packages,
                             'include_files':includefiles
                             }
               },
                           
    executables = [exe]
    )
