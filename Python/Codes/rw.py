# Project
# -----------------------------------------------------------------------------
# Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
# Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
# Contents: Reading and writing of files
# -----------------------------------------------------------------------------


# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import os
import pandas as pd
import pathlib
import queue
from typing import Any
#
from algorithm import Vertex
from level import Level
# -----------------------------------------------------------------------------


# Workspace base folder
# -----------------------------------------------------------------------------
workspace_base_folder: pathlib.Path = (
    pathlib.Path(rf'{os.path.dirname(__file__)}').parents[1]
)
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class Reader:
    """インスタンスのファイルの読み込み(クラスメソッドのみ)"""

    @classmethod
    def read_levels_only(cls,
            instance_name: str,
            ) -> dict[tuple[int, int], Level]:
        """
        Levels ファイルを読み込み、(手前の面から並んだ) Level オブジェクトの集合を生成して返す
        ( ただし next_levels_and_times は設定されていない )
        """

        df_ins_levels: pd.DataFrame = pd.read_csv(
            workspace_base_folder / 'Input' / instance_name / 'Levels.csv'
        )

        max_gems_per_l: int = max(
            int(str(c).strip('Time_NumGems-')) for c in df_ins_levels.columns
            if (str(c).strip('Time_NumGems-')).isdigit() is True
        )
        #
        temp_ep: int = max(
            int(str(c).strip('Unlock_Ep-')) for c in df_ins_levels.columns
            if (str(c).strip('Unlock_Ep-')).isdigit() is True
        )
        temp_pg: int = max(
            int(str(c).strip('Unlock_Pg-')) for c in df_ins_levels.columns
            if (str(c).strip('Unlock_Pg-')).isdigit() is True
        )
        assert temp_ep == temp_pg, (
            f'Unlock_Ep- の最大数 {temp_ep} != Unlock_Pg- の最大数 {temp_pg} です'
        )
        max_unlock_ls_per_l: int = temp_ep

        # Set of levels
        levels: dict[tuple[int, int], Level] = {}
        # そんなに行数もないので itertuples() で回してもいいか
        for row in df_ins_levels.itertuples():
            l_from: Level = Level(
                (int(row[1]), int(row[2])),
                str(row[3]),
                cls.__to_zero_if_nan_else_cast(row[4]),
                {
                    i - 5: round(float(row[i]), 2)
                    for i in range(5, 5 + max_gems_per_l + 1)
                },
            )
            levels[l_from.ep_pg] = l_from
        #
        # そんなに行数もないので itertuples() で回してもいいか
        for row in df_ins_levels.itertuples():
            for j in range(
                    5 + max_gems_per_l + 1,
                    5 + max_gems_per_l + 1 + 2 * max_unlock_ls_per_l,
                    2):
                episode_to: int = cls.__to_zero_if_nan_else_cast(row[j])
                page_to: int = cls.__to_zero_if_nan_else_cast(row[j + 1])
                if episode_to != 0 and page_to != 0:
                    levels[int(row[1]), int(row[2])].add_to_be_unlock_levels(
                        levels[episode_to, page_to]
                    )

        return {l.ep_pg: l for l in [ll for ll in sorted(levels.values())]}

    @classmethod
    def read_levels_and_moves(cls,
            instance_name: str,
            ) -> dict[tuple[int, int], Level]:
        """
        Levels, Moves ファイルを読み込み、(手前の面から並んだ) Level オブジェクトの集合を生成して返す
        ( next_levels_and_times も設定される )
        """
        levels: dict[tuple[int, int], Level] = Reader.read_levels_only(instance_name)

        df_ins_moves: pd.DataFrame = pd.read_csv(
            workspace_base_folder / 'Input' / instance_name / 'Moves.csv'
        )

        for row in df_ins_moves.itertuples():
            l_from: Level = levels[int(row[1]), int(row[2])]
            l_to: Level = levels[int(row[3]), int(row[4])]
            l_from.add_next_levels_and_times(l_to, float(row[5]))

        return levels

    @classmethod
    def __to_zero_if_nan_else_cast(cls, e: Any) -> int:
        """e が nan ならば 0 に変換し、そうでなければ int型 にキャストする"""
        return 0 if pd.isna(e) is True else int(e)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
class Writer:
    """処理結果のファイルへの書き込み(クラスメソッドのみ)"""

    @classmethod
    def output_moves_pks(cls,
            instance_name: str,
            levels: dict[tuple[int, int], Level],
            ) -> None:
        """level オブジェクト の to_be_unlock_level の情報を元に、 Moves ファイルの主キー部分を出力する"""
        moves_pks: list[tuple[Level, Level]] = []
        #
        ls_unlocked_q: queue.PriorityQueue[Level] = queue.PriorityQueue()
        ls_unlocked_set: set[Level] = set()
        l_first: Level = [l for l in levels.values()][0]
        ls_unlocked_q.put(l_first)
        ls_unlocked_set.add(l_first)
        #
        while ls_unlocked_q.empty() is False:
            l_from: Level = ls_unlocked_q.get()
            ls_unlocked_set.remove(l_from)
            #
            for l_to_be_unlocked in l_from.get_to_be_unlock_levels():
                ls_unlocked_q.put(l_to_be_unlocked)
                ls_unlocked_set.add(l_to_be_unlocked)
            #
            for l_to in ls_unlocked_set:
                moves_pks.append((l_from, l_to))
        #
        moves_pks.sort()
        #
        rows: list[list[Any]] = []
        cols: list[str] = ['Ep-From', 'Pg-From', 'Ep-To', 'Pg-To', 'Time']
        for pk in moves_pks:
            rows.append(
                [pk[0].ep_pg[0], pk[0].ep_pg[1], pk[1].ep_pg[0], pk[1].ep_pg[1], ''],
            )
        df_moves_pks: pd.DataFrame = pd.DataFrame(data=rows, columns=cols, )
        df_moves_pks.to_csv(
            workspace_base_folder / 'Output' / f'Moves_base_{instance_name}.csv',
            index=False,
        )

    @classmethod
    def output_strategies(cls,
            instance_name: str,
            strategies: list[tuple[list[Vertex], float]],
            ) -> None:
        """ チャートとして strategies (複数個の場合あり)を出力する"""

        rows: list[list[Any]] = []
        cols: list[str] = [
            'Rank', 'TimeDifference', 'Time', 'Strategy(Level(NumCumGems))'
        ]
        time_prev: float = strategies[0][1]
        rank: int = 1
        for index, strategy in enumerate(strategies):
            time_diff: float = strategy[1] - time_prev
            #
            level_num_cum_gems: str = ' -> '.join([
                f'{v.level.ep_pg[0]}-{v.level.ep_pg[1]:0>2}({v.cumlative_num_gems:0>3})'
                for v in strategy[0]
            ])
            #
            if time_diff > 0.0009:
                rank = index + 1
            rows.append(
                [rank, f'{time_diff:.2f}', f'{strategy[1]:.2f}', level_num_cum_gems],
            )
            time_prev = strategy[1]

        df_sols: pd.DataFrame = pd.DataFrame(data=rows, columns=cols, )
        df_sols.to_csv(
            workspace_base_folder / 'Output' / f'Solutions_{instance_name}.csv',
            index=False,
        )
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
