import matplotlib.pyplot as plt
import pandas as pd

from dr_plotter import FigureManager
from dr_plotter.configs import FacetingConfig, FigureConfig, LegendConfig, PlotConfig
from dr_plotter.scripting.datadec_utils import get_datadec_functions


def load_and_prepare_data() -> pd.DataFrame:
    DataDecide, select_params, select_data = get_datadec_functions()

    target_recipes = ["C4", "DCLM-Baseline"]
    target_params = ["150M", "1B"]

    validated_recipes = select_data(target_recipes)
    validated_params = select_params(target_params)

    dd = DataDecide()
    df = dd.full_eval

    filtered_df = df[
        df["data"].isin(validated_recipes) & df["params"].isin(validated_params)
    ].copy()

    keep_columns = ["params", "data", "step", "seed", "pile-valppl"]
    filtered_df = filtered_df[keep_columns].copy()

    filtered_df = filtered_df.dropna(subset=["pile-valppl"])

    filtered_df["params"] = pd.Categorical(
        filtered_df["params"], categories=validated_params, ordered=True
    )
    filtered_df["data"] = pd.Categorical(
        filtered_df["data"], categories=validated_recipes, ordered=True
    )

    return filtered_df.sort_values(["params", "data", "seed", "step"])


def plot_simple_grid(df: pd.DataFrame) -> None:
    with FigureManager(
        config=PlotConfig(
            figure=FigureConfig(
                rows=2,  # 2 data recipes: C4, DCLM-Baseline
                cols=2,  # 2 model sizes: 150M, 1B
                figsize=(12, 8),
                tight_layout_pad=0.4,
                subplot_kwargs={"sharex": True, "sharey": True},
            ),
            legend=LegendConfig(
                strategy="figure",
                ncol=5,
                layout_bottom_margin=0.15,
            ),
        ),
    ) as fm:
        fm.fig.suptitle(
            "Simple Faceted Grid: Data Recipes × Model Sizes",
            fontsize=14,
            y=0.95,
        )

        facet_config = FacetingConfig(
            rows="data",  # Data recipes across rows
            cols="params",  # Model sizes across columns
            lines="seed",  # Different seeds get different colors
            x="step",
            y="pile-valppl",
        )

        fm.plot_faceted(
            data=df,
            plot_type="line",
            faceting=facet_config,
            linewidth=1.2,
            alpha=0.7,
        )

        for row_idx in range(2):
            for col_idx in range(2):
                ax = fm.get_axes(row_idx, col_idx)

                if row_idx == 1:  # Bottom row
                    ax.set_xlabel("Training Steps")
                else:
                    ax.set_xlabel("")

                if col_idx == 0:  # Left column
                    ax.set_ylabel("Pile Validation Perplexity")
                else:
                    ax.set_ylabel("")

                ax.grid(visible=True, alpha=0.3)
                ax.set_yscale("log")

    plt.show()


def main() -> None:
    print("Loading DataDecide data...")
    df = load_and_prepare_data()
    print(f"Loaded {len(df):,} rows")
    print(f"Model sizes: {df['params'].cat.categories.tolist()}")
    print(f"Data recipes: {df['data'].cat.categories.tolist()}")
    print(f"Seeds: {sorted(df['seed'].unique())}")

    print("Creating simple faceted grid...")
    plot_simple_grid(df)
    print("Done!")


if __name__ == "__main__":
    main()
