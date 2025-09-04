import datadec.constants
import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.datadec_utils import get_datadec_functions

DataDecide, select_params, select_data = get_datadec_functions()


ALL_PARAMS = select_params("all", exclude=["750M"])
ALL_DATA = select_data("all")
PPL_METRICS = datadec.constants.PPL_TYPES
OLMES_TASKS = datadec.constants.OLMES_TASKS
METRIC_NAMES = datadec.constants.METRIC_NAMES
PRIMARY_METRIC_NAME = "primary_metric"
DEFAULT_PROXY_METRIC_NAME = "correct_prob"
ID_COLS = ["params", "data", "step", "seed"]


def build_olmes_metric_list(tasks: list[str], metric_names: list[str]) -> list[str]:
    return [f"{task}_{metric_name}" for task in tasks for metric_name in metric_names]


def all_metrics() -> list[str]:
    return PPL_METRICS + build_olmes_metric_list(OLMES_TASKS, METRIC_NAMES)


def primary_olmes_metrics() -> list[str]:
    return build_olmes_metric_list(OLMES_TASKS, [PRIMARY_METRIC_NAME])


def default_olmes_proxy_metrics() -> list[str]:
    return build_olmes_metric_list(OLMES_TASKS, [DEFAULT_PROXY_METRIC_NAME])


def primary_metrics() -> list[str]:
    return PPL_METRICS + primary_olmes_metrics()


def easy_index_df(
    df: pd.DataFrame, params: list[str], data: list[str], metric: str
) -> pd.DataFrame:
    df = df[df["params"].isin(params) & df["data"].isin(data)]
    target_metrics = [metric]
    keep_columns = ID_COLS + target_metrics
    df = df[keep_columns].copy()
    melted_df = df.melt(
        id_vars=ID_COLS,
        value_vars=target_metrics,
        var_name="metric",
        value_name="value",
    )
    melted_df = melted_df.dropna(subset=["value"])

    melted_df["params"] = pd.Categorical(
        melted_df["params"], categories=params, ordered=True
    )
    melted_df["data"] = pd.Categorical(melted_df["data"], categories=data, ordered=True)

    return melted_df.sort_values(["params", "data", "step"])


def plot_seeds(dd: DataDecide, params: list[str], data: list[str], metric: str) -> None:
    filter_types = ["max_steps"]
    if metric in PPL_METRICS:
        filter_types.append("ppl")
    else:
        filter_types.append("olmes")
    df = dd.get_filtered_df(
        filter_types=filter_types,
        return_means=False,
        min_params=None,
        verbose=True,
    )
    print("Before indexing:", df.shape)
    df = easy_index_df(df, params, data, metric)
    print("After indexing:", df.shape)
    print("Unique params in data:", df["params"].cat.categories.tolist())
    print("Unique data in data:", df["data"].cat.categories.tolist())
    print(df.head())

    metric_label = metric.replace("_", " ").title()
    nparams = len(params)
    ndata = len(data)
    with FigureManager(
        PlotConfig(
            layout={
                "rows": nparams,
                "cols": ndata,
                "figsize": (4 * ndata, 4 * nparams),
                "tight_layout_pad": 0.5,
                "tight_layout_rect": (0.01, 0.01, 0.99, 0.95),
                "subplot_kwargs": {"sharex": True, "sharey": True},
            },
        )
    ) as fm:
        fm.fig.suptitle(
            f"{metric_label}: All Seeds, Model Size x Data Recipe",
            fontsize=16,
            y=0.95,
        )

        fm.plot_faceted(
            data=df,
            plot_type="line",
            rows="params",
            cols="data",
            lines="seed",
            x="step",
            y="value",
            linewidth=1.2,
            alpha=0.7,
            marker=None,
        )

        for row_idx in range(nparams):
            for col_idx in range(ndata):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == nparams - 1:
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if row_idx == 0:
                    ax.set_title(data[col_idx], pad=10)

                if col_idx == 0:
                    print(f"Row {row_idx}: Setting label '{params[row_idx]}'")
                    ax_left = ax.twinx()
                    ax_left.yaxis.set_label_position("left")
                    ax_left.spines["left"].set_position(("axes", -0.15))
                    ax_left.spines["left"].set_visible(False)
                    ax_left.set_yticks([])
                    ax_left.set_ylabel(
                        params[row_idx],
                        rotation=0,
                        size="large",
                        ha="right",
                        va="center",
                    )

                ax.grid(visible=True, alpha=0.3)
    plt.show()


def main() -> None:
    dd = DataDecide()
    params = ALL_PARAMS[-2:]
    data = ALL_DATA[-2:]
    print("Params (order):", params)
    print("Data (order):", data)
    plot_seeds(dd, params, data, "pile-valppl")


if __name__ == "__main__":
    main()
