# =============================================================================
#   BTOR Symbolic Execution Engine and Backends                        
#
#   BSD 3-Clause License. Copyright (c) 2024, Adwait Godbole 
# =============================================================================

"""
    Abstract backend solver class
"""

from dataclasses import dataclass

@dataclass
class BTORSort:
    width: int

class BTORSolver:
    
    def __init__(self, id: str):
        self.id = id
        
    def mk_var(self, name: str, sort: BTORSort):
        pass
    
    def mk_const(self, val: int, sort: BTORSort):
        pass
    
    def mk_sort(self, width: int) -> BTORSort:
        pass
    
    def mk_assume(self, expr):
        pass
    
    def mk_assert(self, expr):
        pass
    
    def check_sat(self) -> bool:
        pass
    
    def get_model(self):
        pass
        
    def not_(self, a):
        pass

    def implies_(self, a, b):
        pass
    
    def iff_(self, a, b):
        pass
    
    def add_(self, a, b):
        pass
    
    def sub_(self, a, b):
        pass
    
    def mul_(self, a, b):
        pass
    
    def sdiv_(self, a, b):
        pass
    
    def udiv_(self, a, b):
        pass
    
    def smod_(self, a, b):
        pass
    
    def sll_(self, a, b):
        pass
    
    def srl_(self, a, b):
        pass
    
    def sra_(self, a, b):
        pass
    
    def and_(self, a, b):
        pass
    
    def or_(self, a, b):
        pass
    
    def xor_(self, a, b):
        pass
    
    def concat_(self, a, b):
        pass
    
    def eq_(self, a, b):
        pass
    
    def neq_(self, a, b):
        pass
    
    def ugt_(self, a, b):
        pass
    
    def sgt_(self, a, b):
        pass
    
    def ugte_(self, a, b):
        pass
    
    def sgte_(self, a, b):
        pass
    
    def ult_(self, a, b):
        pass
    
    def slt_(self, a, b):
        pass
    
    def ulte_(self, a, b):
        pass
    
    def slte_(self, a, b):
        pass
    
    def uext_(self, a, b):
        pass
    
    def ite_(self, a, b, c):
        pass
    
    def slice_(self, op, width, high, low):
        pass
    
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
