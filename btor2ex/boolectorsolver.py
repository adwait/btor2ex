# =============================================================================
#   BTOR Symbolic Execution Engine and Backends                        
#
#   BSD 3-Clause License. Copyright (c) 2024, Adwait Godbole 
# =============================================================================

"""
    Boolector backend solver
"""

import os

from .btorsolver import BTORSolver, BTORSort

import pyboolector

class BoolectorSolver(BTORSolver):
    
    def __init__(self, id: str = "boolector"):
        super().__init__(id)
        
        self.btor = pyboolector.Boolector()
        
        self.sort_cache = {}
        
        self.btor.Set_opt(pyboolector.BTOR_OPT_INCREMENTAL, 1)
        self.btor.Set_opt(pyboolector.BTOR_OPT_MODEL_GEN, 1)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_INCREMENTAL_RW, 1)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_REWRITE_LEVEL, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_SORT_EXP, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_ACKERMANN, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_BETA_REDUCE_ALL, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_ELIMINATE_SLICES, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_ELIMINATE_ITE, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_HEURISTIC, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_SPLIT, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_APP, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_LEMMA, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_LAZY, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_INFER, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_INFER_EX, 0)
        # self.btor.Set_opt(pyboolector.BTOR_OPT_JUST_INFER_AND, 0)
        
    def mk_var(self, name: str, sort: BTORSort):
        """Make var"""
        return self.btor.Var(self.sort_cache[sort.width], name)
    
    def mk_const(self, val: int, sort: BTORSort):
        """Make bitvec constant"""
        return self.btor.Const(val, sort.width)
    
    def mk_sort(self, width: int) -> BTORSort:
        """Make bitvec sort"""
        if width in self.sort_cache:
            return self.sort_cache[width]
        sort = self.btor.BitVecSort(width)
        self.sort_cache[width] = sort
        return BTORSort(width)
    
    def mk_assume(self, expr):
        """Make an assumption"""
        # NOTE: Assumptions are dropped after each check, 
        #   so we need to keep track of them and re-add them
        self.btor.Assume(expr)
        
    def mk_assert (self, expr):
        """Make an assertion"""
        self.btor.Assert(expr)
        
    def check_sat(self):
        """Check satisfiability"""
        return self.btor.Sat() == self.btor.SAT
    
    def get_model(self):
        """Get model"""
        self.btor.Print_model(outfile=".btormodel.tmp")
        with open(".btormodel.tmp", "r") as f:
            model = f.read()
        os.remove('.btormodel.tmp')
        return model
        
    def not_(self, a):
        return self.btor.Not(a)

    def implies_(self, a, b):
        return self.btor.Implies(a, b)
    
    def iff_(self, a, b):
        return self.btor.Iff(a, b)
    
    def add_(self, a, b):
        return self.btor.Add(a, b)
    
    def sub_(self, a, b):
        return self.btor.Sub(a, b)
    
    def mul_(self, a, b):
        return self.btor.Mul(a, b)
    
    def sdiv_(self, a, b):
        return self.btor.SDiv(a, b)
    
    def udiv_(self, a, b):
        return self.btor.UDiv(a, b)
    
    def smod_(self, a, b):
        return self.btor.SMod(a, b)
    
    def sll_(self, a, b):
        return self.btor.Sll(a, b)
    
    def srl_(self, a, b):
        return self.btor.Srl(a, b)
    
    def sra_(self, a, b):
        return self.btor.Sra(a, b)
    
    def and_(self, a, b):
        return self.btor.And(a, b)
    
    def or_(self, a, b):
        return self.btor.Or(a, b)
    
    def xor_(self, a, b):
        return self.btor.Xor(a, b)
    
    def concat_(self, a, b):
        return self.btor.Concat(a, b)
    
    def eq_(self, a, b):
        return self.btor.Eq(a, b)
    
    def neq_(self, a, b):
        return self.btor.Ne(a, b)
    
    def ugt_(self, a, b):
        return self.btor.Ugt(a, b)
    
    def sgt_(self, a, b):
        return self.btor.Sgt(a, b)
    
    def ugte_(self, a, b):
        return self.btor.Ugte(a, b)
    
    def sgte_(self, a, b):
        return self.btor.Sgte(a, b)
    
    def ult_(self, a, b):
        return self.btor.Ult(a, b)
    
    def slt_(self, a, b):
        return self.btor.Slt(a, b)
    
    def ulte_(self, a, b):
        return self.btor.Ulte(a, b)
    
    def slte_(self, a, b):
        return self.btor.Slte(a, b)
    
    def uext_(self, a, b):
        return self.btor.Uext(a, b)
    
    def ite_(self, a, b, c):
        return self.btor.Cond(a, b, c)
    
    def slice_(self, op, width, high, low):
        return self.btor.Slice(op, high, low)
    
    def oplut(self):
        return {
            "and": self.and_,
            "or": self.or_,
            "xor": self.xor_,
            "add" : self.add_,
            "sub" : self.sub_,
            "mul" : self.mul_,
            "udiv" : self.udiv_,
            "sdiv" : self.sdiv_,
            "smod" : self.smod_,
            "sll" : self.sll_,
            "srl" : self.srl_,
            "sra" : self.sra_,
            "concat" : self.concat_,
            "eq" : self.eq_,
            "neq" : self.neq_,
            "ugt" : self.ugt_,
            "sgt" : self.sgt_,
            "ugte" : self.ugte_,
            "sgte" : self.sgte_,
            "ult" : self.ult_,
            "slt" : self.slt_,
            "ulte" : self.ulte_,
            "slte" : self.slte_,
            "uext" : self.uext_,
            "ite" : self.ite_,
            "slice" : self.slice_,
            "not" : self.not_
        }
        