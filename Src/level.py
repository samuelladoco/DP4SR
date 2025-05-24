# Project
#   Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
#   Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
#   Contents: Classes on game features


# Import
from __future__ import annotations

import dataclasses
from typing import Any


# Classes
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
        この面でダイヤ取得数が key のときにクリアにかかる時間が value の辞書
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
        self.__to_be_unlocked_levels.sort(key=lambda x: x.ep_pg)
        return [l1 for l1 in self.__to_be_unlocked_levels]

    def add_to_be_unlock_levels(self, l1: Level) -> None:
        """この面をクリアすると開放される面のリストに l を加える"""
        assert l1 not in self.__to_be_unlocked_levels, (
            f"{self} の to_be_unlocked_levels には {l1} が追加済みです"
        )
        self.__to_be_unlocked_levels.append(l1)

    def get_next_levels_and_times(self) -> dict[Level, float]:
        """
        この面をクリアした次に行くことができる面と移動時間の辞書(手前の面から順)を取得する"""
        nls: list[Level] = [l1 for l1 in self.__next_levels_and_times.keys()]
        nls.sort(key=lambda x: x.ep_pg)
        return {l1: self.__next_levels_and_times[l1] for l1 in nls}

    def add_next_levels_and_times(self, l1: Level, t: float) -> None:
        """
        この面をクリアした次に行くことができる
        面と移動時間の辞書に l: t を加える
        """
        assert l1 not in self.__next_levels_and_times.keys(), (
            f"{self} の next_levels_and_times には {l1} が追加済みです"
        )
        self.__next_levels_and_times[l1] = t

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Level):
            return self.ep_pg == other.ep_pg
        return False

    def __hash__(self) -> int:
        return hash(self.ep_pg)

    def __repr__(self) -> str:
        return (
            f"{self.ep_pg}: "
            + f"n={self.name}, "
            + f"#rg={self.num_required_gems}, "
            + f"t={[f'{n}: {t:.2f}' for n, t in self.times.items()]}, "
            + f"tbul={[f'{l1.ep_pg}' for l1 in self.get_to_be_unlock_levels()]}, "
            + f"nlts={[f'{l1.ep_pg}: {t:.2f}' for l1, t in self.get_next_levels_and_times().items()]}"
        )
