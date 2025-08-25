# Data Mapping Strategy

This document maps ExampleData generators to the 6 planned functionality-testing examples, ensuring optimal data selection for comprehensive parameter testing and visual variety.

## ExampleData Generator Inventory

### Basic Data Generators
- `simple_scatter(n=100, seed=42)` - Basic 2D scatter with correlation
- `time_series(periods=100, series=1, seed=42)` - Single or multiple time series
- `categorical_data(n_categories=5, n_per_category=20, seed=42)` - Categorical x-axis data
- `distribution_data(n_samples=1000, distributions=1, seed=42)` - Histogram data

### Grouped Data Generators
- `time_series_grouped(periods=50, groups=3, seed=42)` - Time series with hue groups
- `grouped_categories(n_categories=4, n_groups=3, n_per_combo=10, seed=42)` - Categories with grouping
- `complex_encoding_data(n_samples=120, seed=42)` - Multiple grouping variables

### Specialized Generators
- `heatmap_data(rows=10, cols=8, seed=42)` - Tidy format for heatmaps
- `gaussian_mixture(n_components=3, n_samples=500, seed=42)` - 2D mixture for contours
- `ranking_data(time_points=20, categories=6, seed=42)` - Rank evolution over time
- `ml_training_curves(epochs=50, learning_rates=None, metrics=None, seed=42)` - ML training data
- `multi_metric_data(n_samples=100, seed=42)` - Multiple y-columns

## Planned Example Assignments

### Example 1: Basic Plotting Functionality
**Purpose**: Test fundamental plot types without complex visual encoding
**File**: `01_basic_functionality.py`

**Data Assignments**:
- **Scatter**: `ExampleData.simple_scatter(n=80, seed=101)`
- **Line**: `ExampleData.time_series(periods=50, seed=102)`
- **Bar**: `ExampleData.categorical_data(n_categories=4, n_per_category=15, seed=103)`
- **Histogram**: `ExampleData.distribution_data(n_samples=300, seed=104)`

**Rationale**: Simple generators ensure focus on plot type mechanics rather than visual encoding complexity.

### Example 2: Visual Encoding Systems  
**Purpose**: Test hue_by, marker_by, and other encoding parameters
**File**: `02_visual_encoding.py`

**Data Assignments**:
- **Color Encoding**: `ExampleData.time_series_grouped(periods=40, groups=3, seed=201)`
- **Marker Encoding**: `ExampleData.complex_encoding_data(n_samples=90, seed=202)`
- **Multi-Variable Encoding**: `ExampleData.grouped_categories(n_categories=3, n_groups=2, seed=203)`

**Rationale**: Data with clear grouping variables enables systematic testing of all visual encoding channels.

### Example 3: Layout & Composition
**Purpose**: Test FigureManager subplot arrangements and coordination
**File**: `03_layout_composition.py`

**Data Assignments**:
- **2x2 Grid**: `ExampleData.multi_metric_data(n_samples=60, seed=301)`
- **Shared Data**: `ExampleData.complex_encoding_data(n_samples=100, seed=302)`
- **Time Alignment**: `ExampleData.ml_training_curves(epochs=30, seed=303)`

**Rationale**: Multi-metric data naturally creates subplot relationships while enabling layout testing.

### Example 4: Specialized Plot Types
**Purpose**: Test heatmap, contour, and violin plot functionality  
**File**: `04_specialized_plots.py`

**Data Assignments**:
- **Heatmap**: `ExampleData.heatmap_data(rows=8, cols=6, seed=401)`
- **Contour**: `ExampleData.gaussian_mixture(n_components=2, n_samples=400, seed=402)`
- **Violin**: `ExampleData.grouped_categories(n_categories=4, n_groups=2, n_per_combo=25, seed=403)`

**Rationale**: Specialized generators designed specifically for these plot types ensure proper data structure testing.

### Example 5: Advanced Features
**Purpose**: Test complex parameter combinations and edge cases
**File**: `05_advanced_features.py`

**Data Assignments**:
- **Multi-Series**: `ExampleData.time_series(periods=60, series=4, seed=501)`
- **Ranking Evolution**: `ExampleData.ranking_data(time_points=15, categories=5, seed=502)`
- **Complex Scatter**: `ExampleData.complex_encoding_data(n_samples=150, seed=503)`

**Rationale**: Complex data structures test parameter interaction and edge case handling.

### Example 6: Integration & Performance
**Purpose**: Test real-world usage patterns and larger datasets
**File**: `06_integration_patterns.py`

**Data Assignments**:
- **Large Dataset**: `ExampleData.distribution_data(n_samples=2000, distributions=3, seed=601)`
- **ML Dashboard**: `ExampleData.ml_training_curves(epochs=100, learning_rates=[0.001, 0.01, 0.1], seed=602)`
- **Multi-Experiment**: `ExampleData.complex_encoding_data(n_samples=300, seed=603)`

**Rationale**: Larger datasets and complex scenarios test performance and real-world integration patterns.

## Seed Value Strategy

### Deterministic Seeds
All examples use deterministic seeds to ensure reproducible outputs for verification. Seeds are assigned in ranges:
- Example 1: 101-110
- Example 2: 201-210  
- Example 3: 301-310
- Example 4: 401-410
- Example 5: 501-510
- Example 6: 601-610

### Visual Variety Optimization
Seeds were selected to provide:
- Clear grouping separations for encoding tests
- Balanced distributions for statistical plots
- Interesting patterns for contour plots
- Realistic trends for time series

## Parameter Combination Guidelines

### Data Size Recommendations
- **Scatter plots**: 60-150 points (avoids overplotting, maintains clarity)
- **Line plots**: 30-60 time points (shows trends without overwhelming)
- **Bar plots**: 3-5 categories (manageable legend sizes)
- **Histograms**: 300-1000 samples (smooth distributions)
- **Heatmaps**: 6-10 rows/cols (readable cell annotations)
- **Violin plots**: 15-30 samples per group (meaningful distribution shapes)

### Grouping Variable Limits
- **hue_by**: 2-4 groups maximum (legend readability)
- **marker_by**: 2-3 types maximum (visual distinction)
- **Combined encoding**: Total visual groups ≤ 6 (cognitive load)

### Data Structure Validation
Each data assignment includes validation criteria:
- Minimum variance in continuous variables
- Adequate separation between groups
- Balanced group sizes
- Expected column presence and types

## Implementation Notes

### Data Generator Usage Pattern
```python
# Standard pattern for all examples
data = ExampleData.generator_name(param1=value1, seed=specific_seed)

# Always validate data structure
assert 'required_column' in data.columns
assert data.groupby('group_column').size().min() >= min_group_size
```

### Consistent Parameterization
- Always specify seeds explicitly
- Use consistent naming conventions (group, category, value, time)
- Ensure data ranges compatible with plot types
- Validate data structure before plotting

This mapping strategy ensures each example has purpose-built data that enables comprehensive functionality testing while maintaining visual clarity and educational value.