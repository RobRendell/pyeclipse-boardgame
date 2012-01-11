'''
Created on 11 janv. 2012

@author: jglouis
'''
import sys, os
from cx_Freeze import setup, Executable
 
#############################################################################
# preparation des options 
 
# chemins de recherche des modules
path = sys.path + ["engine", "gui", "material", "tool"]

print path
 
# options d'inclusion/exclusion des modules
includes = []
excludes = []
packages = []
includefiles = ['src/material','src/gui']
 

binpathincludes = []
if sys.platform == "linux2":
    binpathincludes += ["/usr/lib"]

options = {"path": path,
           "includes": includes,
           "excludes": excludes,
           "packages": packages,
           "include_files": includefiles,
           "bin_path_includes": binpathincludes
           }
 
#############################################################################
# preparation des cibles
base = None
if sys.platform == "win32":
    base = "Win32GUI"
 
cible_1 = Executable(
    script = "src/eclipse.py",
    #base = base,
    compress = False,
    icon = None,
    )
 
#############################################################################
# creation du setup
setup(
    name = "eclipse_dist",
    version = "1",
    description = "Traitement de concours photos sous Windows et Linux",
    author = "Tyrtamos",
    options = {"build_exe": options},
    executables = [cible_1]
    )