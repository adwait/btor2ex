# =============================================================================
#   BTOR Symbolic Execution Engine and Backends                        
#
#   BSD 3-Clause License. Copyright (c) 2024, Adwait Godbole 
# =============================================================================

"""
    Finite state machine for the proof schedule.
"""

from btoropt import Pass
from btoropt import program as prg

class PrFSM(Pass):
    """Proof FSM"""

    def __init__(self, cname: str = "fv__counter", numsteps: int = 2) -> None:
        """
        Args:
            cname (str, optional): Proof FSM counter name. Defaults to "fv__counter".
            numsteps (int, optional): counter steps. Defaults to 2.
        """
        self.numsteps = numsteps
        # log of the number of stages
        self.counterwidth = (numsteps-1).bit_length()
        # name
        self.cname = cname
    
    def subprogram (self, startlid = 1) -> list[prg.Instruction]:
        """Create the BTOR snippet implementing the counter
        Args:
            startlid (int, optional): starting instruction label. Defaults to 1.
        Returns:
            list[prg.Instruction]: list of instructions
        """
        lid = startlid
        # Create sort for the counter
        sort = prg.Sort(lid, "bitvec", self.counterwidth)
        lid += 1
        # Create zero constant
        zero = prg.Const(lid, sort, 0)
        lid += 1
        # Create one constant
        one = prg.Const(lid, sort, 1)
        lid += 1
        # Create counter
        counter = prg.State(lid, sort, self.cname)
        lid += 1
        # Addone expression
        addone = prg.Add(lid, sort, one, counter)
        lid += 1
        # next transition function
        next = prg.Next(lid, sort, counter, addone)

        return [sort, zero, one, counter, addone, next]


    def run (self, p: list[prg.Instruction]) -> list[prg.Instruction]:
        """Run pass"""
        # create subprogram
        return self.subprogram(p[-1].lid + 1)

