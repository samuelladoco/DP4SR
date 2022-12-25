# Project
# -----------------------------------------------------------------------------
# Title   : Dynamic Programming for Optimal Speedrun Strategy Exploration
# Author  : [Twitter] @samuelladoco  [Twitch] SLDCtwitch
# Contents: Dynamic programming algorithm (Dijkstra's algorithm for DAG)
# -----------------------------------------------------------------------------


# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import dataclasses
import functools
import heapq
#
from level import Level
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, order=True, )
class Vertex:
    """動的計画法の段階(グラフの頂点)"""
    level: Level
    cumlative_num_gems: int

    def __repr__(self) -> str:
        return f'({self.level.ep_pg}, {self.cumlative_num_gems})'
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, )
@functools.total_ordering
class Label:
    """動的計画法の段階(グラフの頂点)に付与されるラベル"""
    vertex_this: Vertex
    label_prev: Label | None
    cumulative_time: float

    @property
    # heapq の大小比較の仕様の都合上、累計タイムに -1 をかけたものを用意
    def __minus_times_cumulative_time(self) -> float:
        return -1 * self.cumulative_time

    # heapq の大小比較の仕様の都合上、累計タイムに -1 をかけたものを第1優先にして比較
    def __lt__(self, other) -> bool:
        if isinstance(other, Label):
            if self.__minus_times_cumulative_time < other.__minus_times_cumulative_time:
                return True
            elif self.__minus_times_cumulative_time == other.__minus_times_cumulative_time:
                if self.vertex_this < other.vertex_this:
                    return True
                elif self.vertex_this == other.vertex_this:
                    if self.label_prev == other.label_prev:
                        return False
                    elif self.label_prev is None:
                        return True
                    elif other.label_prev is None:
                        return False
                    elif self.label_prev < other.label_prev:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        return False

    def __eq__(self, other) -> bool:
        if isinstance(other, Label):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr_label_prev(self) -> str:
        return (
            'None' if self.label_prev is None else (
                f'({self.label_prev.vertex_this}, ' +
                f'{self.label_prev.cumulative_time:.2f})'
            )
        )

    def __repr__(self) -> str:
        return (
            f'vt={self.vertex_this}, ' +
            f'lp={self.__repr_label_prev()}, ' +
            f'ct={self.cumulative_time:.2f}'
        )
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
@dataclasses.dataclass(frozen=True, )
class OptimizerByDynamicProgramming:
    """
    動的計画法(今回の場合、非巡回有向グラフに対するダイクストラ法)によるチャートの最適化

    Parameters
    ----------
    levels : list[Level]
        (手前の面から並んだ)面のリスト
    max_labels_per_vertex : int
        求めたいチャートの個数（ 第 1 最適 ～ 最大で 第 max_labels_per_vertex 最適 まで）
    max_required_gems : int
        開放に必要なダイヤ数が最も多い面の必要ダイヤ数
    """
    levels: list[Level]
    max_labels_per_vertex: int
    max_required_gems: int = dataclasses.field(compare=False)
    # 値のデータ構造が list だが、 操作には heapq を使用する
    __labels: dict[Vertex, list[Label]] = dataclasses.field(
        init=False, default_factory=dict, compare=False,
    )

    def solve(self) -> list[tuple[list[Vertex], float]]:
        """チャートを求める"""
        # 最初の頂点たちにラベルを付与する
        for cumulative_num_gems, cumulative_time in self.levels[0].times.items():
            vertex_start: Vertex = Vertex(self.levels[0], cumulative_num_gems)
            self.__labels[vertex_start] = [
                Label(vertex_start, None, cumulative_time)
            ]

        # (面, ダイヤ数) を辞書式の順番で探索
        for level in self.levels:
            for cumulative_num_gems in range(0, self.max_required_gems + 1):
                vertex_this: Vertex = Vertex(level, cumulative_num_gems)
                # この頂点にラベルがない(入ってくる枝がない)場合
                if vertex_this not in self.__labels.keys():
                    continue
                # この頂点の各ラベルについて
                for label_this in self.__labels[vertex_this]:
                    # 次に移動できる面と移動時間について
                    for level_next, time_move in vertex_this.level.get_next_levels_and_times().items():
                        # この頂点でのダイヤ数が足りず次に移動できる面を開放できない場合
                        if vertex_this.cumlative_num_gems < level_next.num_required_gems:
                            continue
                        # 次に移動した面で取得するダイヤ数とクリア時間について
                        for num_gems_next, time_next in level_next.times.items():
                            # ダイヤ数 = この頂点のダイヤ数 + 次に移動した面で取得するダイヤ数
                            cumlative_num_gems_next: int = vertex_this.cumlative_num_gems + num_gems_next
                            # ダイヤ数を必要以上に取った場合
                            if cumlative_num_gems_next > self.max_required_gems:
                                continue
                            #
                            # 時間 = この頂点までの累積時間 + 次に移動した面への移動時間 + 次に移動した面のクリア時間
                            cumulative_time_next: float = label_this.cumulative_time + time_move + time_next
                            #
                            # (次に移動した面, ダイヤ数) の頂点 のラベルたちとの比較
                            vertex_next: Vertex = Vertex(level_next, cumlative_num_gems_next)
                            # ラベルがない場合
                            if vertex_next not in self.__labels.keys():
                                self.__labels[vertex_next] = []
                                heapq.heappush(
                                    self.__labels[vertex_next],
                                    Label(vertex_next, label_this, cumulative_time_next)
                                )
                            # ラベルがあるが最大数以下の個数しかない場合
                            elif len(self.__labels[vertex_next]) < self.max_labels_per_vertex:
                                heapq.heappush(
                                    self.__labels[vertex_next],
                                    Label(vertex_next, label_this, cumulative_time_next)
                                )
                            # ラベルがあり最大個数に達している場合
                            else:
                                # 時間が累積時間が最も長いラベルの時間より短い場合
                                # ( heapq と Label の大小比較の実装により、 self.__labels[vertex_next][0] は累積時間が最も長いラベルとなっている)
                                if cumulative_time_next < self.__labels[vertex_next][0].cumulative_time:
                                    heapq.heappushpop(
                                        self.__labels[vertex_next],
                                        Label(vertex_next, label_this, cumulative_time_next)
                                    )
                                # そうでない場合
                                else:
                                    pass

        # (最終面, 最小必要ダイヤ数) の各ラベルからグラフを逆にたどってパスを構築
        strategies: list[tuple[list[Vertex], float]] = []
        vertex_stop: Vertex = Vertex(self.levels[-1], self.max_required_gems)
        for label_stop in sorted(self.__labels[vertex_stop], key=lambda x: x.cumulative_time):
            vertices: list[Vertex] = [vertex_stop]
            #
            label_this: Label = label_stop
            while label_this.label_prev is not None:
                label_this = label_this.label_prev
                vertices.append(label_this.vertex_this)
            #
            vertices.reverse()
            strategies.append((vertices, label_stop.cumulative_time))

        return strategies

    def __repr_labels(self, labels: list[Label]) -> str:
        return "', '".join([str(l) for l in labels])

    def __repr__(self) -> str:
        s: str = ''
        s += f'levels=\n'
        s += f'\n'.join([str(l) for l in self.levels]) + '\n'
        s += f'mlpv={self.max_labels_per_vertex}\n'
        s += f'lables='
        if len(self.__labels) > 0:
            s += '\n' + f'\n'.join([
                f"{v}: ['{self.__repr_labels(ls)}']"
                for v, ls in self.__labels.items()
            ]) + '\n'
        else:
            s += '(Empty)'
        return s
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
