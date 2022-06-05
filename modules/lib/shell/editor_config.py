# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Editor configuration, contains shortcuts, tab size, scrolling and others """
TABSIZE = 4          # Tabulation size
HORIZONTAL_MOVE=8    # Scrolling minimal deplacement

ESCAPE           = "\x1b"

# For the same action several shortcuts can be used

# Move shortcuts
UP               = ["\x1b[A"]
DOWN             = ["\x1b[B"]
RIGHT            = ["\x1b[C"]
LEFT             = ["\x1b[D"]
HOME             = ["\x1b[1;3D", "\x1b[H", "\x1b\x1b[D", "\x1b[1~", "\x1bb"]
END              = ["\x1b[1;3C", "\x1b[F", "\x1b\x1b[C", "\x1b[4~", "\x1bf"]
PAGE_UP          = ["\x1b[1;3A", "\x1b[A", "\x1b\x1b[A", "\x1b[5~"]
PAGE_DOWN        = ["\x1b[1;3B", "\x1b[B", "\x1b\x1b[B", "\x1b[6~"]
TOP              = ["\x1b[1;5H"]
BOTTOM           = ["\x1b[1;5F"]
NEXT_WORD        = ["\x1b[1;5C"]
PREVIOUS_WORD    = ["\x1b[1;5D"]

# Selection shortcuts
SELECT_UP        = ["\x1b[1;2A"]
SELECT_DOWN      = ["\x1b[1;2B"]
SELECT_RIGHT     = ["\x1b[1;2C"]
SELECT_LEFT      = ["\x1b[1;2D"]
SELECT_PAGE_UP   = ["\x1b[1;10A","\x1b[1;4A","\x1b[5;2~"]
SELECT_PAGE_DOWN = ["\x1b[1;10B","\x1b[1;4B","\x1b[6;2~"]
SELECT_HOME      = ["\x1b[1;2H","\x1b[1;10D"]
SELECT_END       = ["\x1b[1;2F","\x1b[1;10C"]
SELECT_TOP       = ["\x1b[1;6H"]
SELECT_BOTTOM    = ["\x1b[1;6F"]
SELECT_NEXT_WORD = ["\x1b[1;6C","\x1b[1;4C"]
SELECT_PREV_WORD = ["\x1b[1;6D","\x1b[1;4D"]


SELECT_ALL       = ["\x01"]                              # Select All
# Ctrl-B unused
COPY             = ["\x03","\x1bc"]                      # Copy
# Ctrl-D unused
EXECUTE          = ["\x05", "\x1b[15~"]                  # Execute script
FIND             = ["\x06", "\x1BOQ"]                    # Find
GOTO             = ["\x07"]                              # Goto line
BACKSPACE        = ["\x08","\x7F"]                       # Backspace
INDENT           = ["\x09"]                              # Indent
# Line feed reserved
# Ctrl-K unused
DELETE_LINE      = ["\x0C"]                              # Delete line
NEW_LINE         = ["\x0D", "\0x0A"]                     # New line pressed
FIND_NEXT        = ["\x0E", "\x1bOR"]                    # Find next
# Ctrl-O unused
FIND_PREVIOUS    = ["\x10", "\x1b[1;2R"]                 # Find previous
COMMENT          = ["\x11"]                              # Comment block
REPLACE          = ["\x12"]                              # Replace
SAVE             = ["\x13", "\x1bs"]                     # Save
TOGGLE_MODE      = ["\x14"]                              # Toggle replace/insert mode
CHANGE_CASE      = ["\x15"]                              # Change case
PASTE            = ["\x16","\x1bv"]                      # Paste
# Ctrl-W unused
CUT              = ["\x18","\x1bx"]                      # Cut
# Ctrl-Y unused
# Ctrl-Z unused

EXIT             = [ESCAPE]                              # Exit

DELETE           = ["\x1b[3~"]                           # Delete pressed
UNINDENT         = ["\x1b[Z"]                            # Unindent

SELECTION_START = b"\x1B[7m"
SELECTION_END   = b"\x1B[m"
