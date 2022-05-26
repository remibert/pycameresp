[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Text editor

![ShellEdit.gif](/images/ShellEdit.gif "Shell and text editor")


This editor works directly in the board. The text editor uses VT100 sequence escapes, on your computer, you must have a shell that supports these sequence escapes (The camflasher app allows this).

This allows you to make quick and easy changes directly on the board, without having to use synchronization tools, or do remote modification with telnet connection.
This editor allows script execution, and displays errors and execution time.

Editor shortcuts : 

| Shortcuts           | Keys |
| :-------------------| :---------------|
| **Exit**            | Escape  |
| **Move cursor**     | Arrows, Home, End, PageUp, PageDown, Ctrl-Home, Ctrl-End, Ctrl-Left, Ctrl-Right          |
| **Selection**       | Shift-Arrows, Shift-Home, Shift-End, Alt-Shift-Arrows, Ctrl-Shift-Left, Ctrl-Shift-Right |
| **Select all**      | Ctrl-A |
| not used            | Ctrl-B |
| **Copy**            | Ctrl-C on a selection |
| not used            | Ctrl-D |
| **Execute script**  | Ctrl-E or F5 |
| **Find**            | Ctrl-F |
| **Goto line**       | Ctrl-G |
| **Backspace**       | Ctrl-H |
| **Tabultation**     | Ctrl-I |
| **Line feed**       | Ctrl-J |
| not used            | Ctrl-K |
| **Delete line**     | Ctrl-L |
| **Carriage feed**   | Ctrl-M |
| **Find next**       | Ctrl-N or F3 |
| not used            | Ctrl-O |
| **Find previous**   | Ctrl-P or Shift-F3 |
| **Comment block**   | Ctrl-Q on a selection |
| **Replace**         | Ctrl-R |
| **Save**            | Ctrl-S |
| **Toggle mode**     | Ctrl-T toggle insertion to replacement |
| **Case change**     | Ctrl-U on a selection toggle majuscule, minuscule |
| **Paste**           | Ctrl-V on a selection |
| not used            | Ctrl-W |
| **Cut**             | Ctrl-X on a selection |
| not used            | Ctrl-Y |
| not used            | Ctrl-Z |
| **Indent**          | Tab on a selection |
| **Unindent**        | Shift-Tab on a selection |


This editor also works on linux and osx, and can also be used autonomously,
you need to add the useful.py script to its side of editor.py. 
All the keyboard shortcuts are at the start of the script editor.py.

**On the boards with low memory, it may work, but on very small files, otherwise it may produce an error due to insufficient memory.**

