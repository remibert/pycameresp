# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class defining a minimalist shell and text editor , directly executable on the board. """
from .shell import shell
shell()
import sys
if "shell.shell" in sys.modules:
	del sys.modules["shell.shell"]
