"""
    utils.py

    Misc utils

    This file is part of BTOR2Ex. Please see the LICENSE file for details.
"""

def parsewrapper(filepath):
    btor2str: list[str] = []
    with open(filepath, "r") as f:
        btor2str = f.readlines()
    return btor2str