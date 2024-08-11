


import argparse
import sys
import logging

import btoropt

import btor2ex.btor2ex as btor2ex
import btor2ex.utils as utils
import btor2ex.boolectorsolver as boolectorsolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(args):
    
    # Get input file and BMC bound from command line
    argparser = argparse.ArgumentParser(description="BTOR2EX: BTOR2 symbolic execution engine")
    
    argparser.add_argument("input", type=str, help="Input BTOR2 file")
    argparser.add_argument("-b", "--bound", type=int, help="BMC bound", default=3)
    
    args = argparser.parse_args()
    
    # Parse the input file
    prgm = btoropt.parse(utils.parsewrapper(args.input))

    engine = btor2ex.BTOR2Ex(boolectorsolver.BoolectorSolver("test"), prgm)
    result = engine.bmc(args.bound)
    
    if result:
        print("SAFE")
    else:
        print("UNSAFE: please see log for trace")

if __name__ == "__main__":
    main(sys.argv[1:])