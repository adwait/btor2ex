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
from tqdm import tqdm
from dataclasses import dataclass

from btoropt import program as prg

from .btorsolver import BTORSolver

logger = logging.getLogger(__name__)

Assignment = dict[str, int]

@dataclass
class BTORModel:
    # Signals with name and width.
    signals: dict[str, int]
    # Step assignments: time -> signal -> value
    assignments: dict[int, Assignment]

class BTOR2Ex:
    """
    Symbolically execute a BTOR program: the barebones
    """

    def __init__(self, solver: BTORSolver, prog: list[prg.Instruction], gui = None):
        """
        Args:
            solver (BTORSolver): backend solver
            prog (list[prg.Instruction]): BTOR program
        """
        self.slv = solver
        self.prog = prog

        self.names: dict[str, int] = {}
        self.widths: dict[int, int] = {}

        # List of variable assignments
        self.state: list[dict] = []
        # Bads
        self.bads: list[dict] = []
        # Constraints
        self.prgm_assms: list[dict] = []
        # Next mappings
        self.nexts: dict = {}
        # Sorts
        self.sorts: dict = {}

        self.oplut = self.slv.oplut()
        self.gui = gui

    def custom_iterwrapper(self, iterable, desc: str):
        """
        Custom tqdm iterator wrapper
        """
        if self.gui is not None:
            incr = 1.0/len(iterable)
            for i in iterable:
                self.gui.update_progress(desc, incr)
                yield i
            self.gui.reset_progress()
        else:
            for i in tqdm(iterable, desc):
                yield i

    def mk_name(self, var: str, step: int):
        return f"{var}_{step}"

    def preprocess(self):
        """
        Make a pass over the program without execution, gathers state and input information
        """
        assert len(self.state) == 0, "State must be empty for preprocessing"

        logger.debug("Preprocessing and loading first frame.")

        new_state_f = {}

        for inst in self.custom_iterwrapper(self.prog, "Preprocessing: "):
            # This is a sort instruction
            if isinstance(inst, prg.Sort):
                if inst.typ != "bitvec" and inst.typ != "bitvector":
                    logger.error("Unsupported sort %s", inst)
                    sys.exit(1)
                # Create the sort
                if inst.lid not in self.sorts:
                    self.sorts[inst.lid] = self.slv.mk_sort(inst.width)
                    self.widths[inst.lid] = inst.width
            elif isinstance(inst, prg.Input):
                # Create a new input
                self.names[inst.name] = inst.lid
                self.widths[inst.lid] = self.widths[inst.sid]
            elif isinstance(inst, prg.State):
                # Create a new state
                new_state_f[inst.lid] = self.slv.mk_var(
                    self.mk_name(inst.name, 1), self.sorts[inst.sid]
                )
                self.names[inst.name] = inst.lid
                self.widths[inst.lid] = self.widths[inst.sid]
            elif isinstance(inst, prg.Uext):
                # Handle Uexts which are creating new name bindings
                # TODO: might have to handle the recursive aliasing case/if there is more logic
                if inst.renaming:
                    self.names[inst.name] = inst.aliasid
                    self.widths[inst.lid] = self.widths[inst.operands[0].lid]
                    self.widths[inst.aliasid] = self.widths[inst.operands[0].lid]
            elif isinstance(inst, prg.Next):
                # Record mapping from state to next
                self.nexts[inst.lid] = inst.stid
            elif isinstance(inst, prg.Output):
                # Outputs are ignored
                pass

        self.state.append(new_state_f)
        logger.debug("Preprocessing complete")
        logger.debug("Sorts: %s", self.sorts)
        logger.debug("State: %s", self.state)
        logger.debug("Names: %s", self.names)
        return

    def execute(self):
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

        for inst in self.custom_iterwrapper(self.prog, f"Unrolling step {step}: "):
            # This is a sort instruction
            if isinstance(inst, prg.Sort):
                # Already preprocessed
                pass
            elif isinstance(inst, prg.Input):
                # Create a new input
                new_inputs = self.slv.mk_var(
                    self.mk_name(inst.name, step), self.sorts[inst.sid]
                )
                curr_f[inst.lid] = new_inputs
                # curr_inputs_f[inst.lid] = new_inputs
            elif isinstance(inst, prg.State):
                # Already preprocssed
                pass
            elif isinstance(inst, prg.Output):
                # Outputs are ignored
                pass
            elif isinstance(inst, prg.Init):
                if len(self.state) == 1:
                    curr_f[inst.operands[1].lid] = curr_f[inst.operands[2].lid]
            elif isinstance(inst, prg.Next):
                next_state_f[self.nexts[inst.lid]] = curr_f[inst.operands[2].lid]
            elif isinstance(inst, prg.Constraint):
                curr_assms_f[inst.lid] = curr_f[inst.operands[0].lid]
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
                    case prg.Not | prg.Inc | prg.Dec | prg.Neg | prg.Redand | prg.Redor | prg.Redxor:
                        op1 = curr_f[inst.operands[1].lid]
                        curr_f[inst.lid] = self.oplut[inst.inst](op1)
                    # Binary instructions
                    case prg.Add | prg.Sub | prg.Mul | prg.Sdiv | prg.Udiv | prg.Smod | prg.Sll | prg.Srl | prg.Sra | prg.And | prg.Or | prg.Xor | prg.Concat | prg.Eq | prg.Neq | prg.Ugt | prg.Sgt | prg.Ugte | prg.Sgte | prg.Ult | prg.Slt | prg.Ulte | prg.Slte:
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
                    case prg.Sext:
                        op1 = curr_f[inst.operands[1].lid]
                        width = inst.operands[2]
                        curr_f[inst.lid] = self.slv.sext_(op1, width)
                    case prg.Slice:
                        sort = inst.operands[0]
                        op1 = curr_f[inst.operands[1].lid]
                        high = inst.highbit
                        low = inst.lowbit
                        curr_f[inst.lid] = self.slv.slice_(op1, sort.width, high, low)
                    case _:
                        logger.error("Unknown instruction %s", inst)
                        sys.exit(1)

        # Set unchanged state variables to previous values
        for id, expr in self.state[-1].items():
            if id not in next_state_f:
                next_state_f[id] = expr

        # for ip, v in curr_inputs_f.items():
        self.state[-1] = curr_f
        # [ip] = v
        # Push the next state onto the stack
        self.state.append(next_state_f)
        self.bads.append(curr_bads_f)
        self.prgm_assms.append(curr_assms_f)

        logger.debug("Unrolled step %d", step)
        logger.debug("State: %s", next_state_f)
        logger.debug("Bads: %s", curr_bads_f)
        logger.debug("Assms: %s", curr_assms_f)


    def get_model(self) -> BTORModel:
        complete_assignments: dict[int, Assignment] = {}
        complete_signals: dict[str, int] = {}
        for name, lid in self.names.items():
            complete_signals[name] = self.widths[lid]
        
        for i, assignment in enumerate(self.state):
            curr_assignment: Assignment = {}
            for id, expr in assignment.items():
                curr_assignment[id] = expr.assignment

            complete_assignment = {}
            for name in complete_signals:
                reflid = self.names[name]
                complete_assignment[name] = curr_assignment.get(reflid, 0)
            complete_assignments[i] = complete_assignment
        
        model = BTORModel(signals=complete_signals, assignments=complete_assignments)
        return model


    def bmc(self, d=1) -> bool:
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
                for assmdict in self.prgm_assms:
                    for _, assm in assmdict.items():
                        self.slv.mk_assume(assm)
                self.slv.mk_assert(bad)
                result = self.slv.check_sat()
                logger.debug("At depth %d, result %s", i, "BUG" if result else "SAFE")
                if result:
                    logger.debug("Found a bug")
                    model = self.slv.get_model()
                    logger.debug("Model:\n%s", model)
                    return False

            logger.debug("No bug found at depth %d", i)

        # Safe
        return True
