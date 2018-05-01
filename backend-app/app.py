#!/usr/bin/env python

'''
file: app.py
author: Giovanni Macciocu
date: Tue May  1 07:57:34 2018
'''

import os
import sys

# relative directory module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../backend/')
from geotwitterstream import GeoTwitterStreamService


if __name__ == "__main__":
    service = GeoTwitterStreamService()
    service.start()
