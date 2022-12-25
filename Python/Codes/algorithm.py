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
import queue
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
class Label:
    """動的計画法の段階(グラフの頂点)に付与されるラベル"""
    vertex_this: Vertex
    label_prev: Label | None
    cumulative_time: float

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
    # 値のデータ構造をなぜ list にしたのか記憶がない…
    # 組み込みの sort が使えて楽できるので選んだのかな?
    # 本来ならば連結リストにでもしたうえで、ソートの箇所は自前で整列したほうがよい
    # ただし、コレクションの要素数はたかだか max_labels_per_vertex なので、
    # max_labels_per_vertex の値がよっぽど大きくないかぎりはどのデータ構造でも処理時間の違いは微小になりそう
    __labels: dict[Vertex, list[Label]] = dataclasses.field(
        init=False, default_factory=dict, compare=False,
    )
    # Vertex の探索順をなぜ queue.PriorityQueue で決めたのか記憶がない…
    # 探索順は (面, ダイヤ数) の辞書式順であり、この実装でもそういう動きをすることから楽できるので選んだのかな?
    # 本来ならば 面 , ダイヤ数 の 2重の for 文で回すのがよい
    # ただし、コレクションの要素数はたかだか len(levels) * max_required_gems なので、
    # len(levels), max_required_gems の値がよっぽど大きくないかぎりはこの実装でも処理時間は大きくは変わらなさそう
    __q: queue.PriorityQueue[Vertex] = dataclasses.field(
        init=False, default_factory=queue.PriorityQueue, compare=False,
    )

    def solve(self) -> list[tuple[list[Vertex], float]]:
        """チャートを求める"""
        # 最初に出発可能な頂点たち
        for num_gems, time in self.levels[0].times.items():
            v_start: Vertex = Vertex(self.levels[0], num_gems)
            self.__labels[v_start] = [Label(v_start, None, time)]
            self.__q.put(v_start)

        # (面, ダイヤ数) を辞書式の順番で探索
        # 実装が面倒なので、計算量は無視して queue.PriorityQueue で対応
        while self.__q.empty() is False:
            vertex_this: Vertex = self.__q.get()
            self.__generate_next(vertex_this)

        # (最終面, 最小必要ダイヤ数) の各ラベルからグラフを逆にたどってパスを構築
        sols: list[tuple[list[Vertex], float]] = []
        v_end: Vertex = Vertex(self.levels[-1], self.max_required_gems)
        for label_goal in self.__labels[v_end]:
            vs: list[Vertex] = [v_end]
            #
            label_this: Label = label_goal
            while label_this.label_prev is not None:
                label_this = label_this.label_prev
                vs.append(label_this.vertex_this)
            #
            vs.reverse()
            sols.append((vs, label_goal.cumulative_time))
        return sols

    def __generate_next(self, vertex_this: Vertex) -> None:
        """動的計画法の vertex_this の段階(グラフの頂点) から次を生成する"""
        # この頂点の各ラベルについて
        for label_this in self.__labels[vertex_this]:
            # 次に移動できる面と移動時間について
            for level_next, time_move in vertex_this.level.get_next_levels_and_times().items():
                # この頂点でのダイヤ数が足りず次に移動できる面を開放できない場合
                if vertex_this.cumlative_num_gems < level_next.num_required_gems:
                    continue
                # 次に移動した面で取得するダイヤ数とクリア時間について
                for num_gems_next, time_next in level_next.times.items():
                    #
                    # ダイヤ数 = この頂点のダイヤ数 + 次に移動した面で取得するダイヤ数
                    n_g: int = vertex_this.cumlative_num_gems + num_gems_next
                    # ダイヤ数を必要以上に取った場合
                    if n_g > self.max_required_gems:
                        continue
                    #
                    # 時間 = この頂点までの累積時間 + 次に移動した面への移動時間 + 次に移動した面のクリア時間
                    t: float = label_this.cumulative_time + time_move + time_next
                    #
                    # (次に移動した面, ダイヤ数) の頂点 のラベルたちとの比較
                    vertex_next: Vertex = Vertex(level_next, n_g)
                    # ラベルがない場合
                    if vertex_next not in self.__labels.keys():
                        self.__labels[vertex_next] = [
                            Label(vertex_next, label_this, t)
                        ]
                        self.__q.put(vertex_next)
                    # ラベルがあるが最大数以下の個数しかない場合
                    elif len(self.__labels[vertex_next]) < self.max_labels_per_vertex:
                        # 実装が面倒なので、計算量は無視して list で利用できる組み込みのソートで対応
                        # 組み込みのソートのアルゴリズムはティムソートであり、
                        # 整列済みの配列に1つ加えて再ソートするのは時間かからんやろという気持ち
                        self.__labels[vertex_next].append(
                            Label(vertex_next, label_this, t)
                        )
                        self.__labels[vertex_next].sort(
                            key=lambda x:x.cumulative_time
                        )
                    # ラベルがあり最大個数に達している場合
                    else:
                        # 時間 が累積時間が最も長いラベルの時間より短い場合
                        if t < self.__labels[vertex_next][-1].cumulative_time:
                            # 実装が面倒なので、計算量は無視して list で利用できる組み込みのソートで対応
                            # 組み込みのソートのアルゴリズムはティムソートであり、
                            # 整列済みの配列の末尾を新しいのに入れ替えて再ソートするのは時間かからんやろという気持ち
                            self.__labels[vertex_next][-1] = Label(
                                vertex_next, label_this, t
                            )
                            self.__labels[vertex_next].sort(
                                key=lambda x:x.cumulative_time
                            )
                        # そうでない場合
                        else:
                            pass
        return

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
