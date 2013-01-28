import sys
from cx_Freeze import setup, Executable

setup(name="qchess", executables=[Executable("qchess.py")])
