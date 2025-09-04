#!/usr/bin/env python3

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dr_plotter.configs import PlotConfig
from dr_plotter.figure_manager import FigureManager


def create_ranking_data(
    time_points: int = 20, categories: int = 6, seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)
    records = []
    category_names = [f"Team_{chr(65 + i)}" for i in range(categories)]
    
    positions = {cat: np.random.rand() * 100 for cat in category_names}
    
    for t in range(time_points):
        for cat in category_names:
            positions[cat] += np.random.randn() * 5
            positions[cat] = max(0, positions[cat])
            records.append({"time": t, "category": cat, "score": positions[cat]})
    
    return pd.DataFrame(records)


def main() -> None:
    bump_data = create_ranking_data(time_points=15, categories=4, seed=107)
    
    print("Bump plot data preview:")
    print(bump_data.head(10))
    print(f"\nData shape: {bump_data.shape}")
    print(f"Categories: {sorted(bump_data['category'].unique())}")
    print(f"Time range: {bump_data['time'].min()} to {bump_data['time'].max()}")
    
    with FigureManager(
        PlotConfig(
            layout={
                "rows": 1,
                "cols": 1,
                "figsize": (10, 6),
            }
        )
    ) as fm:
        fm.plot(
            "bump",
            0, 0,
            bump_data,
            time_col="time",
            value_col="score", 
            category_col="category",
            marker="o",
            linewidth=2,
            title="Bump Plot: Team Rankings Over Time",
        )
    
    plt.show()


if __name__ == "__main__":
    main()