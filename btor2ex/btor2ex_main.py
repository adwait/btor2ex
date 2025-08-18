"""
    btor2ex_main.py

    Main entry point for BTOR2Ex.

    This file is part of BTOR2Ex. Please see the LICENSE file for details.
"""

import argparse
import sys
import logging

import btoropt

from btor2ex import BTOR2Ex
from btor2ex import parsewrapper
from btor2ex.bitwuzlasolver import BitwuzlaSolver
from btor2ex.boolectorsolver import BoolectorSolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inner_main(args):
    
    # Get input file and BMC bound from command line
    argparser = argparse.ArgumentParser(description="BTOR2EX: BTOR2 symbolic execution engine")
    
    argparser.add_argument("input", type=str, help="Input BTOR2 file")
    argparser.add_argument("-b", "--bound", type=int, help="BMC bound", default=2)
    argparser.add_argument("-s", "--solver", type=str, choices=["boolector","bitwuzla"], default="boolector", help="Backend solver")
    
    args = argparser.parse_args()
    
    # Parse the input file
    prgm = btoropt.parse(parsewrapper(args.input))
    # Select backend solver
    if args.solver == "bitwuzla":
        solver = BitwuzlaSolver("bitwuzla")
    elif args.solver == "boolector":
        solver = BoolectorSolver("boolector")
    else:
        raise ValueError(f"Unknown solver: {args.solver}")

    engine = BTOR2Ex(solver, prgm)
    result = engine.bmc(args.bound)
    
    if result:
        print("SAFE")
    else:
        print("UNSAFE: please see log for trace")

if __name__ == "__main__":
    inner_main(sys.argv[1:])

def main():
    inner_main(sys.argv[1:])
