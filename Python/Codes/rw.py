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
import queue
from typing import Any, ClassVar
#
from algorithm import Vertex
from level import Level
# -----------------------------------------------------------------------------


# Workspace base folder
# -----------------------------------------------------------------------------
workspace_base_folder_abspath: str = rf'{os.path.dirname(__file__)}\..\..'
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class Reader:
    """インスタンスのファイルの読み込み(クラスメソッドのみ)"""

    __max_gems_per_l: ClassVar[int]
    __max_unlock_ls_per_l: ClassVar[int]

    @classmethod
    def read_levels(cls) -> dict[tuple[int, int], Level]:
        """Levels シート(ファイル)を読み込み、 (手前の面から並んだ) Level オブジェクトの集合を生成して返す"""
        # CSV file -> DataFrame
        df_ins_levels: pd.DataFrame = pd.read_csv(
            rf'{workspace_base_folder_abspath}\Input\CTTT\CTTT_Levels.csv'
        )
        
        cls.__max_gems_per_l = max(
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
        cls.__max_unlock_ls_per_l = temp_ep
        del temp_ep, temp_pg

        # Set of levels
        levels: dict[tuple[int, int], Level] = {}
        for row in df_ins_levels.itertuples():
            l_from: Level = Level(
                (int(row[1]), int(row[2])), 
                str(row[3]), 
                cls.__to_zero_if_nan_else_cast(row[4]), 
                {i - 5: round(float(row[i]), 2) 
                 for i in range(5, 5 + cls.__max_gems_per_l + 1)}, 
            )
            levels[l_from.ep_pg] = l_from
            del l_from
        del row
        for row in df_ins_levels.itertuples():
            for j in range(
                    5 + cls.__max_gems_per_l + 1, 
                    5 + cls.__max_gems_per_l + 1 + 2 * cls.__max_unlock_ls_per_l, 
                    2):
                episode_to: int = cls.__to_zero_if_nan_else_cast(row[j])
                page_to: int = cls.__to_zero_if_nan_else_cast(row[j + 1])
                if episode_to != 0 and page_to != 0:
                    levels[int(row[1]), int(row[2])].add_to_be_unlock_levels(
                        levels[episode_to, page_to]
                    )
                del episode_to, page_to
            del j
        del row
        #
        levels = {l.ep_pg: l for l in [ll for ll in sorted(levels.values())]}
        return levels

    @classmethod
    def read_moves_and_update_levels(cls, 
            levels: dict[tuple[int, int], Level]
            ) -> None:
        """Moves シート(ファイル)を読み込み、内容を Levels オブジェクトの next_levels_and_times に加える"""
        # CSV file -> DataFrame
        df_ins_moves: pd.DataFrame = pd.read_csv(
            rf'{workspace_base_folder_abspath}\Input\CTTT\CTTT_Moves.csv'
        )

        for row in df_ins_moves.itertuples():
            l_from: Level = levels[int(row[1]), int(row[2])]
            l_to: Level = levels[int(row[3]), int(row[4])]
            l_from.add_next_levels_and_times(l_to, float(row[5]))
            del l_from, l_to
        del row

    @classmethod
    def __to_zero_if_nan_else_cast(cls, e: Any) -> int:
        """e が nan ならば 0 に変換し、そうでなければ int型 にキャストする"""
        return 0 if pd.isna(e) is True else int(e)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
class Writer:
    """処理結果のファイルへの書き込み(クラスメソッドのみ)"""

    @classmethod
    def output_moves_pks(cls, levels: dict[tuple[int, int], Level]) -> None:
        """level オブジェクト の to_be_unlock_level の情報を元に、 Moves ファイル(シート)の主キー部分を出力する"""
        moves_pks: list[tuple[Level, Level]] = []
        #
        ls_unlocked_q: queue.PriorityQueue[Level] = queue.PriorityQueue()
        ls_unlocked_set: set[Level] = set()
        l_first: Level = [l for l in levels.values()][0]
        ls_unlocked_q.put(l_first)
        ls_unlocked_set.add(l_first)
        del l_first
        #
        while ls_unlocked_q.empty() is False:
            l_from: Level = ls_unlocked_q.get()
            ls_unlocked_set.remove(l_from)
            #
            for l_to_be_unlocked in l_from.get_to_be_unlock_levels():
                ls_unlocked_q.put(l_to_be_unlocked)
                ls_unlocked_set.add(l_to_be_unlocked)
                del l_to_be_unlocked
            #
            for l_to in ls_unlocked_set:
                moves_pks.append((l_from, l_to))
                del l_to
            #
            del l_from
        del ls_unlocked_q, ls_unlocked_set
        #
        moves_pks.sort()
        #
        cols: list[str] = ['Ep-From', 'Pg-From', 'Ep-To', 'Pg-To', 'Time']
        df_moves_pks: pd.DataFrame = pd.DataFrame(columns=cols)
        for pk in moves_pks:
            df_moves_pks = df_moves_pks.append(
                pd.Series(
                    [pk[0].ep_pg[0], pk[0].ep_pg[1], 
                     pk[1].ep_pg[0], pk[1].ep_pg[1], ''], 
                    index=cols
                ), 
                ignore_index=True
            )
        del pk
        df_moves_pks.to_csv(
            rf'{workspace_base_folder_abspath}\Input\CTTT\CTTT_Moves_base.csv', 
            index=False
        )

    @classmethod
    def output_strategies(cls, 
            strategies: list[tuple[list[Vertex], float]]
            ) -> None:
        """ チャートとして strategies (複数個の場合あり)を出力する"""

        def to_str(v: Vertex) -> str:
            return f'{v.level.ep_pg[0]}-{v.level.ep_pg[1]:0>2}({v.cumlative_num_gems:0>3})'

        cols: list[str] = [
            'Rank', 'TimeDifference', 'Time', 'Strategy(Level(NumCumGems))'
        ]
        df_sols: pd.DataFrame = pd.DataFrame(columns=cols)

        time_prev: float = strategies[0][1]
        for rank, strategy in enumerate(strategies):
            time_diff: float = strategy[1] - time_prev

            level_num_cum_gems: str = ' -> '.join([to_str(v) for v in strategy[0]])

            df_sols = df_sols.append(
                pd.Series(
                    [rank + 1, f'{time_diff:.2f}', f'{strategy[1]:.2f}', level_num_cum_gems], 
                    index=cols
                ), 
                ignore_index=True
            )
            time_prev = strategy[1]
            del time_diff
        del rank, strategy
        del time_prev

        df_sols.to_csv(
            rf'{workspace_base_folder_abspath}\Output\CTTT_Solutions.csv', 
            index=False
        )
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
