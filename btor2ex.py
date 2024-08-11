# =============================================================================
#   BTOR Symbolic Execution Engine and Backends                        
#
#   BSD 3-Clause License. Copyright (c) 2024, Adwait Godbole 
# =============================================================================

"""
    Symbolic execution engine performing generic BMC
"""

import logging
import sys

from btoropt import program as prg

from btorsolver import BTORSolver

logger = logging.getLogger(__name__)

class BTOR2Ex():
    """
        Symbolically execute a BTOR program: the barebones 
    """
    def __init__(self, solver: BTORSolver, prog: list[prg.Instruction]):
        """
        Args:
            solver (BTORSolver): backend solver
            prog (list[prg.Instruction]): BTOR program
        """
        self.slv = solver
        self.prog = prog
        
        self.names = {}
        
        # List of variable assignments
        self.state : list[dict]  = []
        # Bads 
        self.bads : list[dict] = []
        # Constraints
        self.assms : list[dict] = []
        # Next mappings
        self.nexts : dict = {}
        # Sorts
        self.sorts : dict = {}
        
        
        self.oplut = self.slv.oplut()
    
    def mk_name (self, var: str, step: int):
        return f"{var}_{step}"
    
    def preprocess (self):
        """
        Make a pass over the program without execution, gathers state and input information
        """
        assert len(self.state) == 0, "State must be empty for preprocessing"
        
        logger.info("Preprocessing and loading first frame.")
        
        new_state_f = {}
        
        for inst in self.prog:
            # This is a sort instruction
            if isinstance(inst, prg.Sort):
                if inst.typ != "bitvec" and inst.typ != "bitvector":
                    logger.error("Unsupported sort %s", inst)
                    sys.exit(1)
                # Create the sort
                if inst.lid not in self.sorts:
                    self.sorts[inst.lid] = self.slv.mk_sort(inst.width)
            elif isinstance(inst, prg.Input):
                # Create a new input
                self.names[inst.name] = inst.lid
            elif isinstance(inst, prg.State):
                # Create a new state
                new_state_f[inst.lid] = self.slv.mk_var(
                    self.mk_name(inst.name, 1), self.sorts[inst.sid])
                self.names[inst.name] = inst.lid
            elif isinstance(inst, prg.Uext):
                # Handle Uexts which are creating new name bindings
                # TODO: might have to handle the recursive aliasing case/if there is more logic
                if inst.renaming:
                    self.names[inst.name] = inst.aliasid
            elif isinstance(inst, prg.Next):
                # Record mapping from state to next
                self.nexts[inst.lid] = inst.stid
            elif isinstance(inst, prg.Output):
                # Outputs are ignored
                pass

        self.state.append(new_state_f)
        logger.info("Preprocessing complete")
        logger.debug("Sorts: %s", self.sorts)
        logger.debug("State: %s", self.state)
        logger.debug("Names: %s", self.names)
        return        
        
    def execute (self):
        """Symbolically unroll the program by one step"""
        step = len(self.state)
        if step == 0:
            self.preprocess()
            step += 1
        
        curr_f = {}
        # curr_inputs_f = {}
        curr_assms_f = {}
        curr_bads_f = {}
        next_state_f = {}

        # Deepcopy the current state
        for id, expr in self.state[-1].items():
            curr_f[id] = expr
        
        for inst in self.prog:
            
            # This is a sort instruction
            if isinstance(inst, prg.Sort):
                # Already preprocessed
                pass
            elif isinstance(inst, prg.Input):
                # Create a new input
                new_inputs = self.slv.mk_var(
                    self.mk_name(inst.name, step), self.sorts[inst.sid])
                curr_f[inst.lid] = new_inputs
                # curr_inputs_f[inst.lid] = new_inputs
            elif isinstance(inst, prg.State):
                # Already preprocssed
                pass
            elif isinstance(inst, prg.Output):
                # Outputs are ignored
                pass
            elif isinstance(inst, prg.Init):
                logger.error("Input instructions are not supported %s", inst)
                sys.exit(1)
            elif isinstance(inst, prg.Next):
                next_state_f[self.nexts[inst.lid]] = curr_f[inst.operands[2].lid]
            elif isinstance(inst, prg.Constraint):
                curr_assms_f[inst.lid] = (curr_f[inst.operands[0].lid])
            elif isinstance(inst, prg.Const):
                curr_f[inst.lid] = self.slv.mk_const(inst.value, self.sorts[inst.sid])
            elif isinstance(inst, prg.Zero):
                curr_f[inst.lid] = self.slv.mk_const(0, self.sorts[inst.sid])
            elif isinstance(inst, prg.One):
                curr_f[inst.lid] = self.slv.mk_const(1, self.sorts[inst.sid])
            elif isinstance(inst, prg.Ones):
                logger.error("Ones instructions are not supported %s", inst)
                sys.exit(1)
            elif isinstance(inst, prg.Bad):
                # Record bad
                curr_bads_f[inst.lid] = curr_f[inst.operands[0].lid]
            else:
                match inst.__class__: 
                    # Unary instructions
                    case prg.Not:
                        op1 = curr_f[inst.operands[1].lid]
                        curr_f[inst.lid] = self.not_(op1)
                    # Binary instructions
                    case prg.Add | prg.Sub | prg.Mul | prg.Sdiv | prg.Udiv | prg.Smod | prg.Sll \
                        | prg.Srl | prg.Sra | prg.And | prg.Or | prg.Xor | prg.Concat \
                        | prg.Eq | prg.Neq | prg.Ugt | prg.Sgt | prg.Ugte | prg.Sgte \
                        | prg.Ult | prg.Slt | prg.Ulte | prg.Slte:
                        op1 = curr_f[inst.operands[1].lid]
                        op2 = curr_f[inst.operands[2].lid]
                        curr_f[inst.lid] = self.oplut[inst.inst](op1, op2)
                    case prg.Ite:
                        opc = curr_f[inst.operands[1].lid]
                        opt = curr_f[inst.operands[2].lid]
                        ope = curr_f[inst.operands[3].lid]
                        curr_f[inst.lid] = self.slv.ite_(opc, opt, ope)
                    case prg.Uext:
                        op1 = curr_f[inst.operands[1].lid]
                        width = inst.operands[2]
                        curr_f[inst.lid] = self.slv.uext_(op1, width)
                    case prg.Slice:
                        sort = inst.operands[0]
                        op1 = curr_f[inst.operands[1].lid]
                        high = inst.lowbit+inst.width-1
                        low = inst.lowbit
                        curr_f[inst.lid] = self.slv.slice_(op1, sort.width, high, low)
                    case _:
                        logger.error("Unknown instruction %s", inst)
                        sys.exit(1)
        
        # for ip, v in curr_inputs_f.items():
        self.state[-1] = curr_f
        # [ip] = v
        # Push the next state onto the stack
        self.state.append(next_state_f)
        self.bads.append(curr_bads_f)
        self.assms.append(curr_assms_f)
        
        
        logger.debug("Unrolled step %d", step)
        logger.debug("State: %s", next_state_f)
        logger.debug("Bads: %s", curr_bads_f)
        logger.debug("Assms: %s", curr_assms_f)
        
    def bmc (self, d=1) -> bool:
        """Perform BMC on the program
        Args:
            d (int, optional): BMC depth. Defaults to 1.
        Returns:
            bool: is the program safe (UNSAT)
        """
        for i in range(d):
            # Unroll
            self.execute()
            # Check
            baddict = self.bads[-1]
            for _, bad in baddict.items():
                # Apply all assumptions
                for assmdict in self.assms:
                    for _, assm in assmdict.items():
                        self.slv.mk_assume(assm)
                self.slv.mk_assert(bad)
                result = self.slv.check_sat()
                logger.info("At depth %d, result %s", i, "BUG" if result else "SAFE")
                if result:
                    logger.info("Found a bug")
                    model = self.slv.get_model()
                    logger.info("Model:\n%s", model)
                    return False
            
            logger.info("No bug found at depth %d", i)
        
        # Safe
        return True

