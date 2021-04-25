import importlib
import os
import logging

from pyfiglet import Figlet
from xtermcolor import colorize

# logging.basicConfig(level=logging.DEBUG)

print(Figlet(font="thin", width=200).renderText('secchallenge 2021'))

for root, subFolders, files in os.walk('.'):
    if root.endswith('/solution') and 'solve.py' in files:
        module_name = '/'.join(root.split('/')[2:4])
        python_module_name = root.split('/')[1:]
        python_module_name.append('solve')

        print(module_name)
        cwd = os.getcwd()
        os.chdir(root)
        try:

            module = importlib.import_module('.'.join(python_module_name))
            if 'solve' in dir(module):
                flag = module.solve()
                print(colorize(flag, ansi=2))
        except Exception as e:
            print(e)
        except KeyboardInterrupt as e:
            print('interrupt')

        os.chdir(cwd)
        print()

