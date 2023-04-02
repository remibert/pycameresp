# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class defining a minimalist shell and text editor , directly executable on the board. """
# pylint: disable=redefined-builtin

def sh():
	""" Start the shell """
	from shell.commands import commands
	commands()
