# =============================================================================
#   BTOR Symbolic Execution Engine and Backends                        
#
#   BSD 3-Clause License. Copyright (c) 2024, Adwait Godbole 
# =============================================================================


"""
    Misc utils
"""

def parsewrapper(filepath):
    btor2str: list[str] = []
    with open(filepath, "r") as f:
        btor2str = f.readlines()
    return btor2str