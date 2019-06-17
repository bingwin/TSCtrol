import sys
import os
from  PyQt5.Qt import *

print(QDir.currentPath())


def creeatFloder(floderName):

    if not os.path.exists(floderName):
        os.makedirs(floderName)
    else:
        print(floderName + " already existed")


creeatFloder("/Users/tieniu/resources")