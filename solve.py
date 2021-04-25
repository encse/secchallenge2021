import importlib
import os
import logging

import sys
from pyfiglet import Figlet
from xtermcolor import colorize

# logging.basicConfig(level=logging.DEBUG)
title = 'Secchallenge 2021'
print(colorize(Figlet(font="banner3-D", width=200).renderText(title), ansi=4))
print(colorize(Figlet(font="binary", width=200).renderText(title), ansi=5))

rootDir = sys.argv[1] if len(sys.argv) > 1 else '.'

for root, subFolders, files in os.walk(rootDir):
    if root.endswith('/solution') and 'solve.py' in files:

        python_module_name = root.replace('./', '').split('/')
        print('/'.join(python_module_name))
        python_module_name.append('solve')
        cwd = os.getcwd()
        os.chdir(root)
        try:

            module = importlib.import_module('.'.join(python_module_name), 'secchallenge')
            if 'solve' in dir(module):
                flag = module.solve().strip()
                print(colorize(flag, ansi=2))
        except Exception as e:
            print(e)
        except KeyboardInterrupt as e:
            print('interrupt')

        os.chdir(cwd)
        print()

