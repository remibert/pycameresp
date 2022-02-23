[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Text editor

![ShellEdit.gif](/images/ShellEdit.gif "Shell and text editor")


This editor works directly in the board. The text editor uses VT100 sequence escapes, on your computer, you must have a shell that supports these sequence escapes.
This allows you to make quick and easy changes directly on the board, without having to use synchronization tools. 
This editor allows script execution, and displays errors and execution time.

Editor shortcuts : 
- **Exit**         : Escape
- **Move cursor**  : Arrows, Home, End, PageUp, PageDown, Ctrl-Home, Ctrl-End, Ctrl-Left, Ctrl-Right
- **Selection**    : Shift-Arrows, Shift-Home, Shift-End, Alt-Shift-Arrows, Ctrl-Shift-Left, Ctrl-Shift-Right
- **Clipboard**    : Selection with Ctrl X(Cut), Ctrl-C(Copy), Ctrl-V(Paste)
- **Case change**  : Selection with Ctrl-U(Toggle majuscule, minuscule)
- **Indent**       : Selection with Tab(Indent) or Shift-Tab(Unindent)
- **Comment block**: Selection with Ctrl-Q
- **Save**         : Ctrl-S
- **Find**         : Ctrl-F
- **Replace**      : Ctrl-H
- **Toggle mode**  : Ctrl-T (Insertion/Replacement)
- **Delete line**  : Ctrl-L
- **Goto line**    : Ctrl-G
- **Execute**      : F5

This editor also works on linux and osx, and can also be used autonomously,
you need to add the useful.py script to its side of editor.py. 
All the keyboard shortcuts are at the start of the script editor.py.

**On the boards with low memory, it may work, but on very small files, otherwise it may produce an error due to insufficient memory.**

