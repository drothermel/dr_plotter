# dr_plotter: Configuration-Driven Plotting for Research Data

`dr_plotter` is a plotting framework built on matplotlib that provides structured configuration management for research visualizations. The library emphasizes reproducible plots through declarative configuration and automated CLI generation.

```bash
# Update datadec dependency
uv lock --upgrade-package datadec
```

## Core Architecture

The library is organized around three primary components:

### Configuration System
Plot specifications are defined through dataclass-based configuration objects:
- `LayoutConfig`: Grid layout, figure sizing, axis properties
- `FacetingConfig`: Multi-panel plotting with dimension-based grouping  
- `LegendConfig`: Legend positioning and styling strategies
- `StyleConfig`: Theme application and visual styling
- `PlotConfig`: Composite configuration combining the above

### Figure Management
The `FigureManager` provides controlled plotting contexts:

```python
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig

with FigureManager(PlotConfig(layout={"rows": 2, "cols": 2})) as fm:
    fm.plot("scatter", 0, 0, data, x="time", y="value")
    fm.plot("line", 0, 1, data, x="time", y="metric") 
```

### Dynamic CLI System
The framework automatically generates command-line interfaces from configuration dataclasses. This eliminates manual CLI maintenance and ensures configuration consistency.

```bash
# Generate 70+ options automatically from config definitions
uv run dr-plotter dataset.parquet \
    --x time --y value \
    --rows-by experiment --cols-by condition \
    --pause 5
```

The CLI system provides:
- Automatic option generation from dataclass field definitions
- Type-aware argument parsing and validation
- Configuration file support (YAML)
- Real-time parameter validation through construction-based checking

## Faceted Plotting

The faceting system supports multi-dimensional data visualization through systematic subplot organization:

```python
from dr_plotter.configs import FacetingConfig

faceting = FacetingConfig(
    rows_by="experiment",     # Organize rows by experiment variable
    cols_by="condition",      # Organize columns by condition variable  
    wrap_by=None,            # Alternative: wrap panels in sequence
    fixed={"dataset": "A"},   # Fix certain dimensions
    order={"condition": ["control", "treatment"]}  # Control panel ordering
)
```

The system automatically:
- Partitions data based on specified dimensions
- Calculates appropriate grid layouts
- Maintains consistent styling across panels
- Handles missing data combinations

## Installation

```bash
uv sync
```

## Usage Examples

**Note**: The `examples/` directory contains legacy code that is currently incompatible with the current architecture and will not execute successfully.

### Basic CLI Usage

```bash
# Scatter plot with faceting by parameter values
uv run dr-plotter data.parquet \
    --x step --y loss --rows-by model_type

# Time series with custom layout  
uv run dr-plotter data.parquet \
    --x time --y accuracy --plot-type line \
    --figsize "(15, 8)" --no-tight-layout
```

### Programmatic Usage

```python
from dr_plotter import FigureManager
from dr_plotter.configs import PlotConfig, LayoutConfig, FacetingConfig

# Configure multi-panel layout
config = PlotConfig(
    layout=LayoutConfig(rows=2, cols=3, figsize=(18, 12)),
    faceting=FacetingConfig(rows_by="experiment", cols_by="metric")
)

# Create faceted visualization
with FigureManager(config) as fm:
    fm.plot_faceted(data, "scatter", faceting=config.faceting)
```

### Data Generation

Test data can be generated using the built-in functions:

```python
from dr_plotter.scripting.plot_data import experimental_data, matrix_data

# Generate time series data
data = experimental_data(
    pattern_type="time_series", 
    n_samples=200, 
    time_points=50
)

# Generate matrix data for heatmaps
matrix = matrix_data(
    rows=10, cols=8, 
    pattern_type="correlation"
)
```

## Configuration Management

Configurations can be specified programmatically or loaded from files:

```python
from dr_plotter.scripting import CLIConfig

# Load from YAML
config = CLIConfig.from_yaml("plot_config.yaml")

# Merge with command-line arguments
merged_config = config.merge_with_cli_args(cli_args)
```

## Design Philosophy

The library implements several core principles:

- **Configuration-Driven**: All plot specifications are declarative and serializable
- **Type Safety**: Comprehensive type hints and runtime validation
- **Reproducibility**: Consistent output from identical configurations
- **Extensibility**: Modular architecture supporting custom components
- **Research-Focused**: Optimized for scientific visualization workflows

For detailed design principles, see [docs/DESIGN_PHILOSOPHY.md](./docs/DESIGN_PHILOSOPHY.md).

## Contributing

Contributions are welcome. See [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.