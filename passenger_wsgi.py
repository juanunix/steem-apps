import sys
import os
sys.path.append('./steem-tag-search')

INTERP = "/home/kasfre2/steem.kasperfred.com/venv/bin/python3"
#INTERP is present twice so that the new Python interpreter knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)


import app as application