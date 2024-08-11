
import unittest

import btoropt

from btor2ex.boolectorsolver import BoolectorSolver
import btor2ex.prfsm as prfsm
from btor2ex.btor2ex import BTOR2Ex
import btor2ex.utils as utils


class PrFSMTest(unittest.TestCase):
    """Check whether Verification FSM is generated correctly"""
    
    def test_btor1(self):
        prgm = btoropt.parse(utils.parsewrapper("tests/btor/reg_en.btor"))

        prfsm1 = prfsm.PrFSM()
        cprgm = prfsm1.run(prgm)
        self.assertEqual(cprgm[0].lid, 23)
        self.assertEqual(cprgm[-1].lid, 28)

class BTORMCTest(unittest.TestCase):
    """Check whether Boolector-based model-checker is working properly"""
    
    def test_btormc_unsafe(self):
        prgm = btoropt.parse(utils.parsewrapper("tests/btor/reg_en.bad.btor"))

        engine = BTOR2Ex(BoolectorSolver("test"), prgm)
        self.assertFalse(engine.bmc(3))

    def test_btormc_safe(self):
        prgm = btoropt.parse(utils.parsewrapper("tests/btor/reg_en.safe.btor"))

        engine = BTOR2Ex(BoolectorSolver("test"), prgm)
        self.assertTrue(engine.bmc(3))