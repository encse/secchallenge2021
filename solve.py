import importlib
import os
import logging

import sys
from pyfiglet import Figlet
from xtermcolor import colorize

# logging.basicConfig(level=logging.DEBUG)
title = 'Secchallenge 2021'
print(colorize(Figlet(font="binary", width=200).renderText(title), ansi=5))
print(colorize(Figlet(font="banner3-D", width=200).renderText(title), ansi=4))
print(colorize(Figlet(font="binary", width=200).renderText(title), ansi=5))

rootDir = sys.argv[1] if len(sys.argv) > 1 else '.'

for root, subFolders, files in os.walk(rootDir):
    if root.endswith('/solution') and 'solve.py' in files:

        absolute_path = os.path.realpath(root)
        python_module_name = root.replace('./', '').split('/')
        print('/'.join(python_module_name))
        python_module_name.append('solve')
        cwd = os.getcwd()
        sys.path.append(absolute_path)
        os.chdir(absolute_path)
        try:
            module = importlib.import_module('.'.join(python_module_name), 'secchallenge')
            if 'solve' in dir(module):
                flag = module.solve().strip()
                print(colorize(flag, ansi=2))

        except Exception as e:
            print(e)
        except KeyboardInterrupt as e:
            print('interrupt')

        sys.path.remove(absolute_path)
        os.chdir(cwd)
        print()

