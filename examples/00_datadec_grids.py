import datadec.constants
import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager
from dr_plotter.scripting.datadec_utils import get_datadec_functions

DataDecide, select_params, select_data = get_datadec_functions()


def add_row_title(ax: plt.Axes, title: str, offset: float = -0.15) -> None:
    ax_left = ax.twinx()
    ax_left.yaxis.set_label_position("left")
    ax_left.spines["left"].set_position(("axes", offset))
    ax_left.spines["left"].set_visible(False)
    ax_left.set_yticks([])
    ax_left.set_ylabel(
        title,
        rotation=0,
        size="large",
        ha="right",
        va="center",
    )


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

    # Have to melt to drop the NaN values mid-run before plotting
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
    df = easy_index_df(df, params, data, metric)

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
                "tight_layout_rect": (0.01, 0.01, 0.99, 0.97),
                "subplot_kwargs": {"sharex": True, "sharey": True},
                "figure_title": f"{metric_label}: All Seeds, Model Size x Data Recipe",
            },
            legend={
                "strategy": "subplot",
                "position": "best",
                "channel_titles": {"seed": "Seed"},
            },
            kwargs={"suptitle_y": 0.98},  # Custom position - overrides theme default
        )
    ) as fm:
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
            row_order=params,
            col_order=data,
            row_titles=True,
            col_titles=True,
            exterior_x_label="Training Steps",
        )

    plt.show()


def main() -> None:
    dd = DataDecide()
    plot_seeds(dd, ALL_PARAMS[-2:], ALL_DATA[-2:], "pile-valppl")


if __name__ == "__main__":
    main()
