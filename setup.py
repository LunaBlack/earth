#!/usr/bin/env python2
# encoding: utf-8

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"namespace_packages": ["zope",
                                            "twisted",
                                            ],
                     "packages": ["os",
                                  "twisted.internet",
                                  "zope.interface",
                                  "scrapy",
                                  "lxml",
                                  "statscollect",
                                  "cffi",
                                  "pycparser",
                                  "cryptography",
                                  "distutils",
                                  "email",
                                  "pymysql",
                                  "myproject",
                                  ],
                     "excludes": ["tcl",
                                  "tkinter",
                                  "matplotlib",
                                  "wxPython",
                                  "collections.sys",
                                  "collections._weakref",
                                  ],
                     "includes": ["OpenSSL.crypto",
                                  "zope.interface",
                                  "pymysql",
                                  ],
                     "include_files": [(r"X:\earthquake\scrapy.cfg", "scrapy.cfg"),
                                       (r"X:\earthquake\setting.txt", "setting.txt"),
                                       # (r"C:\Python27\Lib\site-packages\scrapy\VERSION", "VERSION"),
                                       (r"C:\Python27\Lib\site-packages\scrapy\mime.types", "mime.types"),
                                       ],
                     "optimize": 2,
                     }

base = "Win32GUI"


def patch_scrapy_for_cxFreeze():
    with open(r"C:\Python27\Lib\site-packages\scrapy\__init__.py", "rt") as f:
        pass


setup(name = "LunaSpider",
      version = "1.0",
      description = "LunaSpider", # "spider program for IM College"
      options = {"build_exe": build_exe_options},
      executables = [Executable("setupspider.py", base=base)]
      )
