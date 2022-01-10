# Project
# -----------------------------------------------------------------------------
# Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
# Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
# Contents: Classes on game features
# -----------------------------------------------------------------------------


# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import dataclasses
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, order=True)
class Level:
    """
    面

    Parameters
    ----------
    ep_pg : tuple[int, int]
        この面の (エピソード番号, ページ番号)
    name : str
        この面の名前
    num_required_gems : int
        この面に入るのに必要なダイヤ数
    times : dict[int, float]
        この面でダイヤ取得数が key のときにクリアにかかる時間が value である辞書
    """
    ep_pg: tuple[int, int]
    name: str = dataclasses.field(compare=False)
    num_required_gems: int = dataclasses.field(compare=False)
    times: dict[int, float] = dataclasses.field(compare=False)
    __to_be_unlocked_levels: list[Level] = dataclasses.field(
        init=False, default_factory=list, compare=False
    )
    __next_levels_and_times: dict[Level, float] = dataclasses.field(
        init=False, default_factory=dict, compare=False
    )

    def get_to_be_unlock_levels(self) -> list[Level]:
        """この面をクリアすると開放される面のリスト(手前の面から順)を取得する"""
        self.__to_be_unlocked_levels.sort(key=lambda x:x.ep_pg)
        return [l for l in self.__to_be_unlocked_levels]

    def add_to_be_unlock_levels(self, l: Level) -> None:
        """この面をクリアすると開放される面のリストに l を加える"""
        assert l not in self.__to_be_unlocked_levels, (
            f'{self} の to_be_unlocked_levels には {l} が追加済みです'
        )
        self.__to_be_unlocked_levels.append(l)

    def get_next_levels_and_times(self) -> dict[Level, float]:
        """この面をクリアした次に行くことができる面と移動時間の辞書(手前の面から順)を取得する"""
        nls: list[Level] = [l for l in self.__next_levels_and_times.keys()]
        nls.sort(key=lambda x: x.ep_pg)
        return {l: self.__next_levels_and_times[l] for l in nls}

    def add_next_levels_and_times(self, l: Level, t: float) -> None:
        """この面をクリアした次に行くことができる面と移動時間の辞書に l: t を加える"""
        assert l not in self.__next_levels_and_times.keys(), (
            f'{self} の next_levels_and_times には {l} が追加済みです'
        )
        self.__next_levels_and_times[l] = t

    def __repr__(self) -> str:
        return (
            f'{self.ep_pg}: ' + 
            f'n={self.name}, ' + 
            f'#rg={self.num_required_gems}, ' +
            f't={[f"{n}: {t:.2f}" for n, t in self.times.items()]}, '
            f'tbul={[f"{l.ep_pg}" for l in self.get_to_be_unlock_levels()]}, ' +
            f'nlts={[f"{l.ep_pg}: {t:.2f}" for l, t in self.get_next_levels_and_times().items()]}'
        )
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
