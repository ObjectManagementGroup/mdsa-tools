#!/usr/bin/env python3
import sys

# This is also in removeomgmarkup.pl but stumbles on the macro defs.  This does it correctly.
def replaceUsesNotDef(text, cmdname, value):
    # Leaving off the first \ means it picks up \newcommand and \renewcommand
    cmdDef = "newcommand{" + cmdname + "}"
    end = 0
    if cmdDef in text:
        start = text.index(cmdDef)
        end = start + len(cmdDef)
    text = text[:end] + text[end:].replace(cmdname, value)
    return text
    
text = sys.stdin.read()

# User file macros
text = replaceUsesNotDef(text, "\\userfiles", "../")
text = replaceUsesNotDef(text, "\\genfiles", "GeneratedContent/")
text = replaceUsesNotDef(text, "\\imgfiles", "Images/")

# Unicode chars that cause fits downstream (why?)
text = text.replace("’", "'")
text = text.replace("”", '"')
text = text.replace("“", '"')

# SENSR specific fixes
text = text.replace("{Example1.xml}", "{../Example1.xml}")
text = text.replace("{Example2.xml}", "{../Example2.xml}")
text = text.replace("{Example3.xml}", "{../Example3.xml}")

# These may not be needed any longer
text = text.replace("\x20\x19", "'")
text = text.replace("\xE2\x80\x99", "'")

print(text)
# print("Successful run", file=sys.stderr)
