# Project
# -----------------------------------------------------------------------------
# Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
# Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
# Contents: Main
# -----------------------------------------------------------------------------


# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import sys
#
from algorithm import OptimizerByDynamicProgramming, Vertex
from level import Level
from rw import Reader, Writer
# -----------------------------------------------------------------------------


# Parameters
# -----------------------------------------------------------------------------
# Number of strategies (1st, ..., num_strategies-th (at maximum))
num_strategies: int = 1
# -----------------------------------------------------------------------------


# Mode: Output primal keys of 'Moves' sheet (file) or run of algorithm
# -----------------------------------------------------------------------------
output_moves_pks_only: bool = False
levels: dict[tuple[int, int], Level] = Reader.read_levels()
# 
# Output of primal keys of 'Moves' sheet (file)
if output_moves_pks_only:
    Writer.output_moves_pks(levels)
    sys.exit(0)
# 
# Run of algorithm
Reader.read_moves_and_update_levels(levels)
opt_by_dp: OptimizerByDynamicProgramming = OptimizerByDynamicProgramming(
    [l for l in levels.values()], 
    num_strategies, 
    max(l.num_required_gems for l in levels.values())
)
strategies: list[tuple[list[Vertex], float]] = opt_by_dp.solve()
del opt_by_dp
Writer.output_strategies(strategies)
del strategies
# -----------------------------------------------------------------------------
