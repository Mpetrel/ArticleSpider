#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/2 16:55
# @Author  : Mpetrel
# @Site    : 
# @File    : main.py
# @Software: PyCharm

from scrapy.cmdline import execute
import sys
import os


print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])