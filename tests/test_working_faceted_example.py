import pandas as pd
import matplotlib.pyplot as plt

from dr_plotter.figure_config import FigureConfig
from dr_plotter.figure import FigureManager


def create_ml_training_data() -> pd.DataFrame:
    data = []
    epochs = 50

    metrics = ["loss", "accuracy"]
    datasets = ["train", "val", "test"]
    model_sizes = ["small", "medium", "large"]

    for epoch in range(1, epochs + 1):
        for metric in metrics:
            for dataset in datasets:
                for model_size in model_sizes:
                    if metric == "loss":
                        base_value = 0.9 if dataset == "train" else 0.85
                        decay_rate = (
                            0.02
                            if model_size == "large"
                            else 0.015
                            if model_size == "medium"
                            else 0.01
                        )
                        noise = 0.02 if dataset == "test" else 0.01
                        value = (
                            base_value * (0.95 ** (epoch * decay_rate))
                            + noise * (epoch % 5 - 2) * 0.1
                        )
                    else:  # accuracy
                        base_value = 0.1 if dataset == "train" else 0.15
                        growth_rate = (
                            0.03
                            if model_size == "large"
                            else 0.025
                            if model_size == "medium"
                            else 0.02
                        )
                        noise = 0.01 if dataset == "test" else 0.005
                        value = (
                            min(
                                0.98,
                                base_value
                                + (1 - base_value)
                                * (1 - 0.95 ** (epoch * growth_rate)),
                            )
                            + noise * (epoch % 3 - 1) * 0.1
                        )

                    data.append(
                        {
                            "epoch": epoch,
                            "metric": metric,
                            "dataset": dataset,
                            "model_size": model_size,
                            "value": max(0.01, min(0.99, value)),
                        }
                    )

    return pd.DataFrame(data)


def test_working_faceted_example():
    data = create_ml_training_data()

    print(f"Created ML training data with {len(data)} rows")
    print(f"Data columns: {list(data.columns)}")
    print("Unique values per dimension:")
    print(f"  - Metrics: {sorted(data['metric'].unique())}")
    print(f"  - Datasets: {sorted(data['dataset'].unique())}")
    print(f"  - Model sizes: {sorted(data['model_size'].unique())}")

    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(15, 8))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size",
            x="epoch",
            y="value",
        )

        assert fm._facet_grid_info is not None
        grid_info = fm._facet_grid_info

        print("\nGrid computation successful:")
        print(f"  - Grid type: {grid_info['layout_metadata']['grid_type']}")
        print(f"  - Row values: {grid_info['layout_metadata']['row_values']}")
        print(f"  - Col values: {grid_info['layout_metadata']['col_values']}")

        config = grid_info["config"]
        print("\nConfiguration applied:")
        print(f"  - Rows dimension: {config.rows}")
        print(f"  - Cols dimension: {config.cols}")
        print(f"  - Lines dimension: {config.lines}")
        print(f"  - X coordinate: {config.x}")
        print(f"  - Y coordinate: {config.y}")

        assert config.rows == "metric"
        assert config.cols == "dataset"
        assert config.lines == "model_size"
        assert config.x == "epoch"
        assert config.y == "value"

        layout_meta = grid_info["layout_metadata"]
        assert len(layout_meta["row_values"]) == 2
        assert len(layout_meta["col_values"]) == 3
        assert layout_meta["grid_type"] == "explicit"

        print("\n✅ Faceted plotting example completed successfully!")
        print("✅ Created 2×3 grid with 3 lines per subplot")
        print(
            f"✅ Shows {len(data['model_size'].unique())} model sizes across {len(data['metric'].unique())} metrics and {len(data['dataset'].unique())} datasets"
        )

        print("\n📊 This demonstrates significant API simplification:")
        print("   - Single plot_faceted() call replaces manual subplot management")
        print("   - Automatic data subsetting eliminates manual filtering")
        print("   - Built-in coordinate mapping simplifies parameter passing")
        print("   - Native support for multiple series (lines dimension)")


if __name__ == "__main__":
    test_working_faceted_example()
    plt.show()
