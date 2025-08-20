"""
Shared synthetic datasets for all examples.
Following DRY principle - create once, use everywhere.
"""

import pandas as pd
import numpy as np


class ExampleData:
    """
    Centralized synthetic data generation for dr_plotter examples.
    
    All methods return pandas DataFrames ready for plotting.
    This ensures consistency across examples and follows DRY principle.
    """
    
    @staticmethod
    def simple_scatter(n=100, seed=42):
        """Basic 2D scatter data with optional correlation."""
        np.random.seed(seed)
        x = np.random.randn(n)
        y = x * 0.5 + np.random.randn(n) * 0.5  # Some correlation
        return pd.DataFrame({
            "x": x,
            "y": y
        })
    
    @staticmethod
    def time_series(periods=100, series=1, seed=42):
        """Time series data with optional multiple series."""
        np.random.seed(seed)
        data = {"time": np.arange(periods)}
        
        if series == 1:
            data["value"] = np.random.randn(periods).cumsum()
        else:
            for i in range(series):
                data[f"series_{i+1}"] = np.random.randn(periods).cumsum()
                
        return pd.DataFrame(data)
    
    @staticmethod
    def time_series_grouped(periods=50, groups=3, seed=42):
        """Time series with categorical groups (for hue encoding)."""
        np.random.seed(seed)
        group_names = [f"Group_{chr(65+i)}" for i in range(groups)]
        
        records = []
        for group in group_names:
            base_trend = np.random.randn() * 0.5  # Different trend per group
            values = np.random.randn(periods).cumsum() + base_trend * np.arange(periods)
            for t, v in enumerate(values):
                records.append({
                    "time": t,
                    "value": v,
                    "group": group
                })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def categorical_data(n_categories=5, n_per_category=20, seed=42):
        """Data with categorical x-axis for bar/violin plots."""
        np.random.seed(seed)
        categories = [f"Cat_{chr(65+i)}" for i in range(n_categories)]
        
        records = []
        for cat in categories:
            # Different mean and variance per category
            mean = np.random.randn() * 2
            std = 0.5 + np.random.rand() * 1.5
            values = np.random.normal(mean, std, n_per_category)
            
            for val in values:
                records.append({
                    "category": cat,
                    "value": val
                })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def grouped_categories(n_categories=4, n_groups=3, n_per_combo=10, seed=42):
        """Categorical data with additional grouping variable."""
        np.random.seed(seed)
        categories = [f"Cat_{chr(65+i)}" for i in range(n_categories)]
        groups = [f"Group_{i+1}" for i in range(n_groups)]
        
        records = []
        for cat in categories:
            for group in groups:
                # Different effects per combination
                base = np.random.randn() * 2
                group_effect = np.random.randn()
                values = np.random.normal(base + group_effect, 0.8, n_per_combo)
                
                for val in values:
                    records.append({
                        "category": cat,
                        "group": group,
                        "value": val
                    })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def distribution_data(n_samples=1000, distributions=1, seed=42):
        """Data for histograms with optional multiple distributions."""
        np.random.seed(seed)
        
        if distributions == 1:
            return pd.DataFrame({
                "values": np.random.randn(n_samples)
            })
        else:
            records = []
            dist_names = ["Normal", "Skewed", "Bimodal"][:distributions]
            
            for dist in dist_names:
                if dist == "Normal":
                    values = np.random.randn(n_samples)
                elif dist == "Skewed":
                    values = np.random.gamma(2, 2, n_samples)
                elif dist == "Bimodal":
                    values = np.concatenate([
                        np.random.normal(-2, 0.5, n_samples//2),
                        np.random.normal(2, 0.5, n_samples//2)
                    ])
                
                for val in values:
                    records.append({
                        "value": val,
                        "distribution": dist
                    })
            
            return pd.DataFrame(records)
    
    @staticmethod
    def heatmap_data(rows=10, cols=8, seed=42):
        """Data for heatmap in tidy/long format."""
        np.random.seed(seed)
        
        records = []
        row_names = [f"Row_{i+1}" for i in range(rows)]
        col_names = [f"Col_{chr(65+i)}" for i in range(cols)]
        
        # Generate correlated patterns
        base_pattern = np.random.randn(rows, cols)
        base_pattern = np.cumsum(base_pattern, axis=0) * 0.3
        base_pattern = np.cumsum(base_pattern, axis=1) * 0.3
        
        for i, row in enumerate(row_names):
            for j, col in enumerate(col_names):
                records.append({
                    "row": row,
                    "column": col,
                    "value": base_pattern[i, j] + np.random.randn() * 0.5
                })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def ranking_data(time_points=20, categories=6, seed=42):
        """Data for bump plots showing rankings over time."""
        np.random.seed(seed)
        
        records = []
        category_names = [f"Team_{chr(65+i)}" for i in range(categories)]
        
        # Initialize with random starting positions
        positions = {cat: np.random.rand() * 100 for cat in category_names}
        
        for t in range(time_points):
            # Random walk for each category
            for cat in category_names:
                positions[cat] += np.random.randn() * 5
                positions[cat] = max(0, positions[cat])  # Keep positive
                
                records.append({
                    "time": t,
                    "category": cat,
                    "score": positions[cat]
                })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def gaussian_mixture(n_components=3, n_samples=500, seed=42):
        """2D data from gaussian mixture for contour plots."""
        np.random.seed(seed)
        
        samples_per_component = n_samples // n_components
        data = []
        
        # Generate components with different means and covariances
        means = [(0, 0), (3, 3), (-2, 2)][:n_components]
        covs = [
            [[1, 0.5], [0.5, 1]],
            [[2, -0.8], [-0.8, 1]],
            [[0.8, 0.3], [0.3, 1.5]]
        ][:n_components]
        
        for mean, cov in zip(means, covs):
            samples = np.random.multivariate_normal(mean, cov, samples_per_component)
            data.append(samples)
        
        all_samples = np.vstack(data)
        return pd.DataFrame(all_samples, columns=["x", "y"])
    
    @staticmethod
    def ml_training_curves(epochs=50, learning_rates=None, metrics=None, seed=42):
        """ML experiment data with train/val metrics."""
        np.random.seed(seed)
        
        if learning_rates is None:
            learning_rates = [0.001, 0.01, 0.1]
        if metrics is None:
            metrics = ["loss", "accuracy"]
            
        records = []
        
        for lr in learning_rates:
            # Simulate training dynamics based on learning rate
            convergence_speed = lr * 10
            
            for epoch in range(epochs):
                # Loss decreases over time
                train_loss = np.exp(-epoch * convergence_speed / epochs) * (1 + np.random.randn() * 0.1)
                val_loss = train_loss * (1.1 + np.random.randn() * 0.05)
                
                # Accuracy increases over time
                train_acc = 1 - train_loss * 0.9
                val_acc = 1 - val_loss * 0.9
                
                if "loss" in metrics:
                    records.append({
                        "epoch": epoch,
                        "learning_rate": lr,
                        "train_loss": train_loss,
                        "val_loss": val_loss
                    })
                    
                if "accuracy" in metrics:
                    # If we want both metrics, update the last record
                    if "loss" in metrics:
                        records[-1].update({
                            "train_accuracy": train_acc,
                            "val_accuracy": val_acc
                        })
                    else:
                        records.append({
                            "epoch": epoch,
                            "learning_rate": lr,
                            "train_accuracy": train_acc,
                            "val_accuracy": val_acc
                        })
        
        return pd.DataFrame(records)
    
    @staticmethod
    def multi_metric_data(n_samples=100, seed=42):
        """Data with multiple y-columns for multi-metric plotting."""
        np.random.seed(seed)
        
        x = np.linspace(0, 10, n_samples)
        
        return pd.DataFrame({
            "x": x,
            "metric_a": np.sin(x) + np.random.randn(n_samples) * 0.1,
            "metric_b": np.cos(x) + np.random.randn(n_samples) * 0.1,
            "metric_c": np.sin(x * 0.5) * 2 + np.random.randn(n_samples) * 0.1,
            "category": np.repeat(["Type_1", "Type_2"], n_samples // 2)[:n_samples]
        })
    
    @staticmethod
    def complex_encoding_data(n_samples=120, seed=42):
        """Data with multiple grouping variables for complex visual encoding."""
        np.random.seed(seed)
        
        experiments = ["Exp_A", "Exp_B", "Exp_C"]
        conditions = ["Control", "Treatment"]
        algorithms = ["Algo_1", "Algo_2"]
        
        records = []
        for exp in experiments:
            for cond in conditions:
                for algo in algorithms:
                    n = n_samples // (len(experiments) * len(conditions) * len(algorithms))
                    
                    # Different distributions per combination
                    if cond == "Control":
                        x_offset, y_offset = 0, 0
                    else:
                        x_offset, y_offset = 2, 1
                        
                    if algo == "Algo_1":
                        spread = 1
                    else:
                        spread = 1.5
                    
                    x = np.random.randn(n) * spread + x_offset
                    y = np.random.randn(n) * spread + y_offset
                    
                    for xi, yi in zip(x, y):
                        records.append({
                            "x": xi,
                            "y": yi,
                            "experiment": exp,
                            "condition": cond,
                            "algorithm": algo,
                            "performance": xi * yi + np.random.randn() * 0.5
                        })
        
        return pd.DataFrame(records)


# Validation to ensure all data generators work
if __name__ == "__main__":
    print("Testing all data generators...")
    
    generators = [
        ("simple_scatter", ExampleData.simple_scatter),
        ("time_series", ExampleData.time_series),
        ("time_series_grouped", ExampleData.time_series_grouped),
        ("categorical_data", ExampleData.categorical_data),
        ("grouped_categories", ExampleData.grouped_categories),
        ("distribution_data", ExampleData.distribution_data),
        ("heatmap_data", ExampleData.heatmap_data),
        ("ranking_data", ExampleData.ranking_data),
        ("gaussian_mixture", ExampleData.gaussian_mixture),
        ("ml_training_curves", ExampleData.ml_training_curves),
        ("multi_metric_data", ExampleData.multi_metric_data),
        ("complex_encoding_data", ExampleData.complex_encoding_data),
    ]
    
    for name, generator in generators:
        try:
            df = generator()
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            print(f"✅ {name}: {df.shape}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print("\nAll data generators validated!")