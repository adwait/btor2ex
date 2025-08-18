"""
    bitwuzlasolver.py

    Bitwuzla backend solver.

    This file is part of BTOR2Ex. Please see the LICENSE file for details.
"""

import os
from .btorsolver import BTORSolver, BTORSort
import bitwuzla


class BitwuzlaSolver(BTORSolver):
    def __init__(self, id: str = "bitwuzla"):
        super().__init__(id)
        # create solver and term manager
        self.tm = bitwuzla.TermManager()
        self.options = bitwuzla.Options()
        self.options.set(bitwuzla.Option.PRODUCE_MODELS, True)
        self.bz = bitwuzla.Bitwuzla(self.tm, self.options)
        self.sort_cache: dict[int, bitwuzla.Sort] = {}
        # track assumptions separately
        self.assumptions: list[bitwuzla.Term] = []

    def mk_sort(self, width: int) -> BTORSort:
        """Make bitvector sort."""
        if width not in self.sort_cache:
            bv_sort = self.tm.mk_bv_sort(width)
            self.sort_cache[width] = bv_sort
        return BTORSort(width)

    def mk_var(self, name: str, sort: BTORSort):
        """Make a variable."""
        bz_sort = self.sort_cache[sort.width]
        return self.tm.mk_const(bz_sort, name)

    def mk_const(self, val: int, sort: BTORSort):
        """Make a bitvector constant."""
        bz_sort = self.sort_cache[sort.width]
        return self.tm.mk_bv_value(bz_sort, val)
    
    def mk_assume(self, expr):
        """Record an assumption to pass to check_sat."""
        self.assumptions.append(expr)

    def mk_assert(self, expr):
        """Assert a formula."""
        self.bz.assert_formula(expr)

    def check_sat(self) -> bool:
        """Check satisfiability under recorded assumptions."""
        res = self.bz.check_sat(*self.assumptions)
        # clear assumptions after check
        self.assumptions.clear()
        return res == bitwuzla.Result.SAT

    def get_model(self):
        """Return an empty model dump (not implemented)."""
        return ""

    def get_assignment(self, expr):
        """Get integer assignment of a term."""
        val_term = self.bz.get_value(expr)
        # boolean term
        if hasattr(val_term, "is_true") and val_term.is_true():
            return 1
        if hasattr(val_term, "is_false") and val_term.is_false():
            return 0
        # bitvector term: get raw string and convert
        raw = val_term.value()
        return int(raw, 2)

    def push(self):
        """Push assertion level."""
        self.bz.push()

    def pop(self):
        """Pop assertion level."""
        self.bz.pop()

    #
    # Operators
    #
    def not_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.NOT, [a])

    def inc_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_INC, [a])

    def dec_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_DEC, [a])

    def neg_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_NEG, [a])

    def redand_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_REDAND, [a])

    def redor_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_REDOR, [a])

    def redxor_(self, a):
        return self.tm.mk_term(bitwuzla.Kind.BV_REDXOR, [a])

    def implies_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.IMPLIES, [a, b])

    def iff_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.IFF, [a, b])

    def add_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_ADD, [a, b])

    def sub_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SUB, [a, b])

    def mul_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_MUL, [a, b])

    def sdiv_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SDIV, [a, b])

    def udiv_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_UDIV, [a, b])

    def smod_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SMOD, [a, b])

    def sll_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SHL, [a, b])

    def srl_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SHR, [a, b])

    def sra_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_ASHR, [a, b])

    def and_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_AND, [a, b])

    def or_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_OR, [a, b])

    def xor_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_XOR, [a, b])

    def concat_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_CONCAT, [a, b])

    def eq_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.EQUAL, [a, b])

    def neq_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.DISTINCT, [a, b])

    def ugt_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_UGT, [a, b])

    def sgt_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SGT, [a, b])

    def ugte_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_UGE, [a, b])

    def sgte_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SGE, [a, b])

    def ult_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_ULT, [a, b])

    def slt_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SLT, [a, b])

    def ulte_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_ULE, [a, b])

    def slte_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SLE, [a, b])

    def uext_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_ZERO_EXTEND, [a], indices=[b])

    def sext_(self, a, b):
        return self.tm.mk_term(bitwuzla.Kind.BV_SIGN_EXTEND, [a], indices=[b])

    def ite_(self, a, b, c):
        return self.tm.mk_term(bitwuzla.Kind.ITE, 
            [self.tm.mk_term(bitwuzla.Kind.EQUAL, [a, self.tm.mk_bv_value(self.tm.mk_bv_sort(1), 0)]), b, c])

    def slice_(self, op, width, high, low):
        return self.tm.mk_term(bitwuzla.Kind.BV_EXTRACT, [op], indices=[high, low])

    def oplut(self):
        return {
            "and": self.and_,
            "or": self.or_,
            "xor": self.xor_,
            "add": self.add_,
            "sub": self.sub_,
            "mul": self.mul_,
            "udiv": self.udiv_,
            "sdiv": self.sdiv_,
            "smod": self.smod_,
            "sll": self.sll_,
            "srl": self.srl_,
            "sra": self.sra_,
            "concat": self.concat_,
            "eq": self.eq_,
            "neq": self.neq_,
            "ugt": self.ugt_,
            "sgt": self.sgt_,
            "ugte": self.ugte_,
            "sgte": self.sgte_,
            "ult": self.ult_,
            "slt": self.slt_,
            "ulte": self.ulte_,
            "slte": self.slte_,
            "uext": self.uext_,
            "sext": self.sext_,
            "ite": self.ite_,
            "slice": self.slice_,
            "not": self.not_,
            "inc": self.inc_,
            "dec": self.dec_,
            "neg": self.neg_,
            "redand": self.redand_,
            "redor": self.redor_,
            "redxor": self.redxor_,
            "implies": self.implies_,
            "iff": self.iff_,
        }
