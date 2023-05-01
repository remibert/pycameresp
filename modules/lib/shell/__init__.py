# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Class defining a minimalist shell and text editor , directly executable on the board. """
# pylint: disable=redefined-builtin

def sh():
	""" Start the shell """
	import shell.commands
	shell.commands.commands()
