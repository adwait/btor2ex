
import unittest

import btoropt

import boolectorsolver
import prfsm
import btor2ex
import utils


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

        engine = btor2ex.BTOR2Ex(boolectorsolver.BoolectorSolver("test"), prgm)
        self.assertFalse(engine.bmc(3))

    def test_btormc_safe(self):
        prgm = btoropt.parse(utils.parsewrapper("tests/btor/reg_en.safe.btor"))

        engine = btor2ex.BTOR2Ex(boolectorsolver.BoolectorSolver("test"), prgm)
        self.assertTrue(engine.bmc(3))