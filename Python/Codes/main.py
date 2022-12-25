# Project
# -----------------------------------------------------------------------------
# Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
# Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
# Contents: Main
# -----------------------------------------------------------------------------


# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
#
from algorithm import OptimizerByDynamicProgramming, Vertex
from level import Level
from rw import Reader, Writer
# -----------------------------------------------------------------------------


# Settings
# -----------------------------------------------------------------------------
# Instance name
instance_name: str = 'CTTT'
# Mode: output of primal keys of 'Moves' file or run of algorithm
output_moves_pks_only: bool = False
# -----------------------------------------------------------------------------


# Parameters
# -----------------------------------------------------------------------------
# Number of strategies (1st, ..., num_strategies-th (at maximum))
num_strategies: int = 10
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
levels: dict[tuple[int, int], Level]
#
# Output of primal keys of 'Moves' file
if output_moves_pks_only:
    levels = Reader.read_levels_only(instance_name)
    Writer.output_moves_pks(instance_name, levels)
# Run of algorithm
else:
    levels = Reader.read_levels_and_moves(instance_name)
    opt_by_dp: OptimizerByDynamicProgramming = OptimizerByDynamicProgramming(
        [l for l in levels.values()],
        num_strategies,
        max(l.num_required_gems for l in levels.values()),
    )
    strategies: list[tuple[list[Vertex], float]] = opt_by_dp.solve()
    Writer.output_strategies(instance_name, strategies)
# -----------------------------------------------------------------------------
