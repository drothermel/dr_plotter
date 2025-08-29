# Faceted Plotting Implementation: Chunk 6 - Validation & Polish

## Project Context

You are implementing **Chunk 6** - Validation & Polish, the final chunk to complete dr_plotter's native faceting support.

**Your role**: Add comprehensive validation, error handling, documentation, and final integration polish to transform our working implementation into a production-ready feature.

**Foundation**: Chunks 1-5 completed successfully with working style coordination (94/94 faceting tests passing, 141/141 total tests passing) and comprehensive architecture.

## Key References

**MANDATORY**: Before starting, read these docs:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Previous chunk implementation notes and patterns
- `docs/plans/context_restoration_guide_faceted_plotting.md` - Current capabilities and scope

## Your Tasks

### Task 1: Comprehensive Error Handling & Validation

**Problem**: Current error messages may be unclear or unhelpful. Users need clear guidance when they make configuration mistakes.

**Files to enhance**:
- `src/dr_plotter/faceting/validation.py` - Enhance validation functions
- `src/dr_plotter/faceting_config.py` - Improve FacetingConfig validation messages
- `src/dr_plotter/figure.py` - Add helpful error context in plot_faceted()

**Implementation**:

1. **Enhanced Data Validation with Context**:
```python
# In src/dr_plotter/faceting/validation.py
def validate_faceting_data_requirements(
    data: pd.DataFrame, config: FacetingConfig
) -> None:
    if data.empty:
        assert False, (
            "Cannot create faceted plot with empty DataFrame. "
            "Please provide data with at least one row."
        )
    
    if len(data) < 2:
        print(f"Warning: DataFrame has only {len(data)} row(s). "
              f"Faceted plots work best with multiple data points per subplot.")
    
    # Enhanced missing column error with suggestions
    required_columns = []
    if config.rows is not None:
        required_columns.append(config.rows)
    if config.cols is not None:
        required_columns.append(config.cols)
    if config.lines is not None:
        required_columns.append(config.lines)
    if config.x is not None:
        required_columns.append(config.x)
    if config.y is not None:
        required_columns.append(config.y)

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        available = sorted(data.columns.tolist())
        similar_suggestions = _suggest_similar_columns(missing_columns, available)
        
        error_msg = f"Missing required columns: {missing_columns}\n"
        error_msg += f"Available columns: {available}\n"
        if similar_suggestions:
            error_msg += f"Did you mean: {similar_suggestions}?"
        
        assert False, error_msg

def _suggest_similar_columns(missing: List[str], available: List[str]) -> Dict[str, List[str]]:
    """Suggest similar column names for typos."""
    import difflib
    suggestions = {}
    
    for missing_col in missing:
        # Find columns with similar names (handles typos)
        matches = difflib.get_close_matches(missing_col, available, n=3, cutoff=0.6)
        if matches:
            suggestions[missing_col] = matches
    
    return suggestions
```

2. **Configuration Validation with Clear Guidance**:
```python
# Enhanced FacetingConfig.validate() in src/dr_plotter/faceting_config.py
def validate(self) -> None:
    # More helpful error for missing dimensions
    if not (self.rows or self.cols):
        assert False, (
            "Must specify at least one faceting dimension.\n"
            "Examples:\n"
            "  - rows='metric' (facet by metric across rows)\n"
            "  - cols='dataset' (facet by dataset across columns)\n" 
            "  - rows='metric', cols='dataset' (2D grid)"
        )

    # Enhanced wrapped layout validation with examples
    has_explicit_grid = self.rows and self.cols
    has_wrap_layout = self.ncols or self.nrows
    if has_explicit_grid and has_wrap_layout:
        assert False, (
            f"Cannot specify both explicit grid and wrap layout.\n"
            f"Current config: rows='{self.rows}', cols='{self.cols}', ncols={self.ncols}, nrows={self.nrows}\n"
            f"Choose one approach:\n"
            f"  - Explicit grid: rows='{self.rows}', cols='{self.cols}'\n"
            f"  - Wrapped layout: rows='{self.rows}', ncols={self.ncols or self.nrows}\n"
        )

    # Targeting validation with helpful suggestions
    if self.target_row is not None and self.target_rows is not None:
        assert False, (
            f"Cannot specify both target_row and target_rows.\n"
            f"Current: target_row={self.target_row}, target_rows={self.target_rows}\n"
            f"Use target_row for single row or target_rows for multiple rows."
        )
```

3. **Runtime Validation with Data Context**:
```python
# In src/dr_plotter/figure.py - enhance plot_faceted validation
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, **kwargs) -> None:
    # ... existing parameter resolution ...
    
    # Enhanced plot type validation
    valid_plot_types = ['line', 'scatter', 'bar', 'fill_between', 'heatmap']  # Get from actual plotters
    if plot_type not in valid_plot_types:
        assert False, (
            f"Unsupported plot type: '{plot_type}'\n"
            f"Supported types: {valid_plot_types}\n"
            f"Note: All standard dr_plotter plot types should work with faceting."
        )
    
    # Enhanced grid validation against FigureManager state
    try:
        grid_rows, grid_cols, layout_metadata = self._compute_facet_grid(data, config)
    except Exception as e:
        # Catch and enhance grid computation errors
        assert False, (
            f"Failed to compute faceting grid: {str(e)}\n"
            f"Data shape: {data.shape}\n"
            f"Faceting config: rows='{config.rows}', cols='{config.cols}', "
            f"ncols={config.ncols}, nrows={config.nrows}\n"
            f"Check that your data contains the specified dimension columns."
        )
    
    # Enhanced subplot configuration validation
    if config.x_labels is not None:
        try:
            validate_nested_list_dimensions(config.x_labels, grid_rows, grid_cols, "x_labels")
        except AssertionError as e:
            assert False, (
                f"x_labels configuration error: {str(e)}\n"
                f"Computed grid: {grid_rows} rows × {grid_cols} cols\n"
                f"x_labels shape: {len(config.x_labels)} rows × {len(config.x_labels[0]) if config.x_labels else 0} cols\n"
                f"Tip: x_labels must match the computed grid dimensions."
            )
```

4. **Common Mistake Prevention**:
```python
# Add helpful warnings for common configuration mistakes
def _validate_common_mistakes(self, config: FacetingConfig, data: pd.DataFrame) -> None:
    """Check for and warn about common configuration mistakes."""
    
    # Warn about single-value dimensions
    if config.rows and config.rows in data.columns:
        unique_rows = data[config.rows].nunique()
        if unique_rows == 1:
            print(f"Warning: rows='{config.rows}' has only 1 unique value. "
                  f"Consider using a dimension with multiple values.")
    
    # Warn about excessive grid sizes
    if config.rows and config.cols:
        if config.rows in data.columns and config.cols in data.columns:
            n_rows = data[config.rows].nunique()
            n_cols = data[config.cols].nunique()
            total_subplots = n_rows * n_cols
            
            if total_subplots > 20:
                print(f"Warning: Large grid ({n_rows}×{n_cols} = {total_subplots} subplots). "
                      f"Consider using wrapped layouts or filtering data.")
    
    # Warn about sparse data
    if config.lines and config.lines in data.columns:
        avg_points_per_group = len(data) / data[config.lines].nunique()
        if avg_points_per_group < 3:
            print(f"Warning: Few data points per {config.lines} group "
                  f"(avg {avg_points_per_group:.1f}). Plots may be sparse.")
```

5. **Error Recovery Suggestions**:
```python
# Add error recovery suggestions for common issues
def _suggest_error_recovery(self, error_type: str, context: Dict[str, Any]) -> str:
    """Provide helpful suggestions for recovering from errors."""
    
    suggestions = {
        'missing_columns': [
            "Check column names for typos",
            "Use data.columns to see available columns", 
            "Ensure your data has the expected structure"
        ],
        'empty_subsets': [
            "Check if your data has all combinations of row/col values",
            "Consider using target_row/target_col for sparse data",
            "Use empty_subplot_strategy='silent' to suppress warnings"
        ],
        'large_grid': [
            "Use wrapped layouts: rows='metric', ncols=4",
            "Filter data to fewer categories",
            "Consider hierarchical faceting approaches"
        ]
    }
    
    if error_type in suggestions:
        return "Suggestions:\n" + "\n".join(f"  • {s}" for s in suggestions[error_type])
    return ""
```

### Task 2: Performance Optimization & Scalability

**Problem**: Faceting must scale reasonably with dataset size and grid complexity without significant performance regressions.

**Files to optimize**:
- `src/dr_plotter/faceting/data_preparation.py` - Optimize data subsetting
- `src/dr_plotter/faceting/grid_computation.py` - Optimize grid computation
- `src/dr_plotter/faceting/style_coordination.py` - Optimize style coordination
- `src/dr_plotter/figure.py` - Optimize faceted plotting pipeline

**Implementation**:

1. **Data Preparation Optimization**:
```python
# In src/dr_plotter/faceting/data_preparation.py
def prepare_subplot_data_subsets(
    data: pd.DataFrame, 
    row_values: List[str], 
    col_values: List[str],
    row_col: Optional[str], 
    col_col: Optional[str],
    target_positions: Optional[List[Tuple[int, int]]] = None
) -> Dict[Tuple[int, int], pd.DataFrame]:
    """Optimized data preparation with early filtering and memory efficiency."""
    
    # Early return for single subset case
    if row_col is None and col_col is None:
        if target_positions and len(target_positions) == 1:
            return {target_positions[0]: data}
        return {(0, 0): data}
    
    # Pre-filter data to only include relevant combinations
    if row_col and col_col:
        relevant_row_values = set(row_values)
        relevant_col_values = set(col_values)
        
        # Filter data early to reduce memory usage
        mask = (
            data[row_col].isin(relevant_row_values) & 
            data[col_col].isin(relevant_col_values)
        )
        filtered_data = data[mask]
        
        if len(filtered_data) == 0:
            return {}
    else:
        filtered_data = data
    
    # Optimize subset creation - only create subsets for target positions
    if target_positions:
        position_set = set(target_positions)
    else:
        # Create all positions if no targeting
        position_set = {(r, c) for r in range(len(row_values)) for c in range(len(col_values))}
    
    # Use groupby for efficient subsetting when possible
    data_subsets = {}
    
    if row_col and col_col and len(position_set) > 4:
        # For larger grids, use pandas groupby for efficiency
        try:
            grouped = filtered_data.groupby([row_col, col_col])
            
            for (row_idx, col_idx) in position_set:
                if row_idx < len(row_values) and col_idx < len(col_values):
                    row_val = row_values[row_idx]
                    col_val = col_values[col_idx]
                    
                    try:
                        subset = grouped.get_group((row_val, col_val))
                        data_subsets[(row_idx, col_idx)] = subset
                    except KeyError:
                        # Empty subset - handled by empty_subplot_strategy
                        pass
        except Exception:
            # Fall back to individual filtering if groupby fails
            data_subsets = _prepare_subsets_individual_filtering(
                filtered_data, row_values, col_values, row_col, col_col, position_set
            )
    else:
        # For smaller grids, use individual filtering
        data_subsets = _prepare_subsets_individual_filtering(
            filtered_data, row_values, col_values, row_col, col_col, position_set
        )
    
    return data_subsets

def _prepare_subsets_individual_filtering(
    data: pd.DataFrame, 
    row_values: List[str], 
    col_values: List[str],
    row_col: Optional[str], 
    col_col: Optional[str],
    position_set: Set[Tuple[int, int]]
) -> Dict[Tuple[int, int], pd.DataFrame]:
    """Fallback method using individual filtering."""
    data_subsets = {}
    
    for (row_idx, col_idx) in position_set:
        filters = {}
        if row_col and row_idx < len(row_values):
            filters[row_col] = row_values[row_idx]
        if col_col and col_idx < len(col_values):
            filters[col_col] = col_values[col_idx]
        
        subset = create_data_subset(data, filters)
        if not subset.empty:
            data_subsets[(row_idx, col_idx)] = subset
    
    return data_subsets
```

2. **Grid Computation Optimization**:
```python
# In src/dr_plotter/faceting/grid_computation.py
def compute_grid_layout_metadata(
    data: pd.DataFrame, 
    config: FacetingConfig,
    grid_rows: int, 
    grid_cols: int
) -> Dict[str, Any]:
    """Optimized grid computation with caching and early returns."""
    
    # Cache dimension analysis results to avoid recomputation
    if not hasattr(compute_grid_layout_metadata, '_dimension_cache'):
        compute_grid_layout_metadata._dimension_cache = {}
    
    cache_key = _create_cache_key(data, config)
    if cache_key in compute_grid_layout_metadata._dimension_cache:
        cached_result = compute_grid_layout_metadata._dimension_cache[cache_key]
        # Verify cache is still valid
        if cached_result['data_shape'] == data.shape:
            return cached_result['metadata']
    
    # Compute fresh metadata
    metadata = _compute_fresh_metadata(data, config, grid_rows, grid_cols)
    
    # Cache result for future use (limit cache size)
    if len(compute_grid_layout_metadata._dimension_cache) < 10:
        compute_grid_layout_metadata._dimension_cache[cache_key] = {
            'metadata': metadata,
            'data_shape': data.shape
        }
    
    return metadata

def _create_cache_key(data: pd.DataFrame, config: FacetingConfig) -> str:
    """Create cache key based on config and data columns."""
    key_parts = []
    
    if config.rows:
        key_parts.append(f"rows:{config.rows}")
    if config.cols:
        key_parts.append(f"cols:{config.cols}")
    if config.lines:
        key_parts.append(f"lines:{config.lines}")
    
    # Include data hash for columns (not full data)
    relevant_columns = [c for c in [config.rows, config.cols, config.lines] if c and c in data.columns]
    if relevant_columns:
        column_hash = hash(tuple(sorted(relevant_columns)))
        key_parts.append(f"cols_hash:{column_hash}")
    
    return "|".join(key_parts)
```

3. **Style Coordination Memory Optimization**:
```python
# In src/dr_plotter/faceting/style_coordination.py
class FacetStyleCoordinator:
    def __init__(self) -> None:
        self._dimension_values: Dict[str, Set[str]] = {}
        self._style_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._cycle_positions: Dict[str, int] = {}
        self._max_cached_dimensions = 5  # Limit memory usage
    
    def register_dimension_values(self, dimension: str, values: List[str]) -> None:
        """Memory-optimized dimension registration."""
        
        # Limit cache size to prevent unbounded growth
        if len(self._dimension_values) >= self._max_cached_dimensions and dimension not in self._dimension_values:
            # Remove least recently used dimension
            self._evict_lru_dimension()
        
        if dimension not in self._dimension_values:
            self._dimension_values[dimension] = set()
        
        # Only add new values to reduce set operations
        new_values = set(values) - self._dimension_values[dimension]
        if new_values:
            self._dimension_values[dimension].update(new_values)
            
            # Only recompute assignments for new values
            self._assign_styles_to_new_values(dimension, sorted(new_values, key=str))
    
    def _evict_lru_dimension(self) -> None:
        """Remove least recently used dimension to limit memory."""
        if self._dimension_values:
            # Simple eviction - remove first dimension (could be enhanced with true LRU)
            oldest_dimension = next(iter(self._dimension_values))
            del self._dimension_values[oldest_dimension]
            del self._style_assignments[oldest_dimension]
            del self._cycle_positions[oldest_dimension]
    
    def get_subplot_styles(self, row: int, col: int, dimension: Optional[str], 
                          subplot_data: pd.DataFrame, **plot_kwargs) -> Dict[str, Any]:
        """Optimized style lookup with early returns."""
        
        # Fast path for no coordination needed
        if dimension is None or dimension not in self._style_assignments:
            return plot_kwargs
        
        if dimension not in subplot_data.columns:
            return plot_kwargs
        
        # Optimize for common single-value case
        dimension_values = subplot_data[dimension].unique()
        if len(dimension_values) == 1:
            value = dimension_values[0]
            if value in self._style_assignments[dimension]:
                result_kwargs = plot_kwargs.copy()
                result_kwargs.update(self._style_assignments[dimension][value])
                return result_kwargs
        
        # Handle multi-value case
        return self._convert_to_plot_params(
            {v: self._style_assignments[dimension].get(v, {}) for v in dimension_values},
            dimension_values.tolist(),
            plot_kwargs
        )
```

4. **Pipeline Optimization**:
```python
# In src/dr_plotter/figure.py - optimize plot_faceted pipeline
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, **kwargs) -> None:
    """Optimized faceted plotting pipeline."""
    
    # Early validation to avoid expensive computation on invalid inputs
    if data.empty:
        assert False, "Cannot create faceted plot with empty DataFrame."
    
    # Fast path for single subplot case
    config = self._resolve_faceting_config(faceting, **kwargs)
    if not config.rows and not config.cols:
        # Single subplot - use regular plot method
        self.plot(plot_type, 0, 0, data, x=config.x, y=config.y, hue_by=config.lines, **kwargs)
        return
    
    # Optimize for small datasets (< 1000 rows)
    if len(data) < 1000:
        # Skip some optimizations for small datasets
        return self._plot_faceted_standard_pipeline(data, plot_type, config, **kwargs)
    
    # Full optimized pipeline for larger datasets
    return self._plot_faceted_optimized_pipeline(data, plot_type, config, **kwargs)

def _plot_faceted_optimized_pipeline(self, data: pd.DataFrame, plot_type: str, 
                                   config: FacetingConfig, **kwargs) -> None:
    """Optimized pipeline for larger datasets."""
    
    # Validate once at the beginning
    validate_faceting_data_requirements(data, config)
    
    # Batch grid computation operations
    grid_info = self._compute_facet_grid_optimized(data, config)
    grid_rows, grid_cols = grid_info['rows'], grid_info['cols']
    layout_metadata = grid_info['metadata']
    
    # Optimize data preparation with targeting awareness
    target_positions = resolve_target_positions(config, grid_rows, grid_cols)
    data_subsets = prepare_subplot_data_subsets(
        data, 
        layout_metadata.get('row_values', []),
        layout_metadata.get('col_values', []),
        config.rows, 
        config.cols,
        target_positions=target_positions  # Only prepare needed subsets
    )
    
    # Batch style coordination
    if config.lines:
        style_coordinator = self._get_or_create_style_coordinator()
        # Pre-register all values at once
        all_lines_values = data[config.lines].unique().tolist()
        style_coordinator.register_dimension_values(config.lines, all_lines_values)
    
    # Optimized plotting loop
    plot_kwargs = {k: v for k, v in kwargs.items() if k not in {'rows', 'cols', 'lines', 'x', 'y'}}
    
    for (row_idx, col_idx) in target_positions:
        if (row_idx, col_idx) in data_subsets:
            subset_data = data_subsets[(row_idx, col_idx)]
            
            # Get coordinated styles
            if config.lines and hasattr(self, '_facet_style_coordinator'):
                coordinated_styles = self._facet_style_coordinator.get_subplot_styles(
                    row_idx, col_idx, config.lines, subset_data, **plot_kwargs
                )
            else:
                coordinated_styles = plot_kwargs
            
            # Apply subplot configuration and plot
            self._apply_subplot_configuration(row_idx, col_idx, config)
            self.plot(plot_type, row_idx, col_idx, subset_data, 
                     x=config.x, y=config.y, hue_by=config.lines, **coordinated_styles)
```

5. **Performance Monitoring and Benchmarks**:
```python
# Add performance monitoring utilities
def _benchmark_faceting_performance(self, data_size: str, grid_size: str) -> Dict[str, float]:
    """Benchmark faceting performance for different scenarios."""
    import time
    
    benchmarks = {
        'small_data_small_grid': (100, 2, 2),      # 100 rows, 2×2 grid
        'medium_data_medium_grid': (1000, 3, 4),   # 1K rows, 3×4 grid  
        'large_data_small_grid': (10000, 2, 3),    # 10K rows, 2×3 grid
        'medium_data_large_grid': (5000, 4, 5),    # 5K rows, 4×5 grid
    }
    
    if data_size not in benchmarks:
        return {}
    
    n_rows, grid_r, grid_c = benchmarks[data_size]
    test_data = _generate_benchmark_data(n_rows, grid_r, grid_c)
    
    # Benchmark full faceting pipeline
    start_time = time.time()
    with FigureManager(figure=FigureConfig(rows=grid_r, cols=grid_c)) as fm:
        fm.plot_faceted(
            data=test_data,
            plot_type="scatter",
            rows="metric",
            cols="dataset", 
            lines="model",
            x="step",
            y="value"
        )
    total_time = time.time() - start_time
    
    return {
        'total_time': total_time,
        'time_per_subplot': total_time / (grid_r * grid_c),
        'time_per_datapoint': total_time / n_rows
    }
```

### Task 3: API Consistency & Integration

**Problem**: Faceting must integrate seamlessly with existing dr_plotter features and maintain consistent API patterns.

**Files to enhance**:
- `src/dr_plotter/figure.py` - Integrate with themes, legends, and existing features
- `src/dr_plotter/faceting_config.py` - Ensure parameter consistency with FigureConfig
- `tests/test_faceting_integration.py` - Add comprehensive integration tests

**Implementation**:

1. **Theme System Integration**:
```python
# In src/dr_plotter/figure.py - enhance theme integration
def _get_or_create_style_coordinator(self) -> FacetStyleCoordinator:
    """Create style coordinator with theme integration."""
    if self._facet_style_coordinator is None:
        from dr_plotter.faceting.style_coordination import FacetStyleCoordinator
        
        # Pass theme information to style coordinator
        theme_info = None
        if hasattr(self, '_theme') and self._theme:
            theme_info = {
                'color_cycle': getattr(self._theme, 'color_cycle', None),
                'marker_cycle': getattr(self._theme, 'marker_cycle', None),
                'line_style_cycle': getattr(self._theme, 'line_style_cycle', None)
            }
        
        self._facet_style_coordinator = FacetStyleCoordinator(theme=theme_info)
    return self._facet_style_coordinator

# Enhanced FacetStyleCoordinator constructor
# In src/dr_plotter/faceting/style_coordination.py
class FacetStyleCoordinator:
    def __init__(self, theme: Optional[Dict[str, Any]] = None) -> None:
        self._dimension_values: Dict[str, Set[str]] = {}
        self._style_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._cycle_positions: Dict[str, int] = {}
        self._max_cached_dimensions = 5
        self._theme = theme or {}
    
    def _get_next_style_from_cycle(self, dimension: str) -> Dict[str, Any]:
        """Get next style from theme-aware cycle."""
        position = self._cycle_positions[dimension]
        
        # Use theme colors if available
        if 'color_cycle' in self._theme and self._theme['color_cycle']:
            colors = self._theme['color_cycle']
        else:
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Use theme markers if available
        if 'marker_cycle' in self._theme and self._theme['marker_cycle']:
            markers = self._theme['marker_cycle']
        else:
            markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        return {
            'color': colors[position % len(colors)],
            'marker': markers[position % len(markers)]
        }
```

2. **Legend System Integration**:
```python
# In src/dr_plotter/figure.py - enhance legend integration
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, **kwargs) -> None:
    # ... existing implementation ...
    
    # After plotting all subplots, handle legend coordination
    if config.lines and self.legend_manager:
        self._coordinate_faceted_legends(config, data)

def _coordinate_faceted_legends(self, config: FacetingConfig, data: pd.DataFrame) -> None:
    """Coordinate legend display across faceted subplots."""
    
    # Get unique values for legend
    if config.lines and config.lines in data.columns:
        legend_values = sorted(data[config.lines].unique(), key=str)
        
        # Get coordinated colors for legend entries
        style_coordinator = self._get_or_create_style_coordinator()
        legend_entries = []
        
        for value in legend_values:
            if value in style_coordinator._style_assignments.get(config.lines, {}):
                style = style_coordinator._style_assignments[config.lines][value]
                legend_entries.append(LegendEntry(
                    label=str(value),
                    color=style.get('color', '#1f77b4'),
                    marker=style.get('marker', 'o'),
                    line_style=style.get('linestyle', '-')
                ))
        
        # Apply legend using existing legend manager
        if legend_entries:
            # Update legend manager with coordinated entries
            self.legend_manager.add_entries(legend_entries)
            self.legend_manager.apply_legend(self.fig)

# Ensure FacetingConfig parameter names align with existing patterns
# In src/dr_plotter/faceting_config.py
@dataclass
class FacetingConfig:
    # Core faceting dimensions (consistent with existing parameter patterns)
    rows: Optional[str] = None
    cols: Optional[str] = None  
    lines: Optional[str] = None  # Consistent with existing hue_by patterns
    
    # Layout control (consistent with FigureConfig patterns)
    ncols: Optional[int] = None
    nrows: Optional[int] = None
    
    # Ordering (consistent with existing ordering patterns)
    row_order: Optional[List[str]] = None
    col_order: Optional[List[str]] = None  
    lines_order: Optional[List[str]] = None
    
    # Targeting (consistent with subplot indexing)
    target_row: Optional[int] = None
    target_col: Optional[int] = None
    target_rows: Optional[List[int]] = None
    target_cols: Optional[List[int]] = None
    
    # Plot parameters (consistent with existing plot method signatures)
    x: Optional[str] = None
    y: Optional[str] = None
    
    # Subplot configuration (consistent with FigureConfig nested list patterns)
    x_labels: Optional[List[List[Optional[str]]]] = None
    y_labels: Optional[List[List[Optional[str]]]] = None
    xlim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    ylim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    
    # Advanced features (consistent with existing configuration patterns)
    subplot_titles: Optional[str | List[List[Optional[str]]]] = None
    title_template: Optional[str] = None
    shared_x: Optional[str | bool] = None
    shared_y: Optional[str | bool] = None
    empty_subplot_strategy: str = "warn"
    color_wrap: bool = False
```

3. **Parameter Resolution Consistency**:
```python
# In src/dr_plotter/figure.py - ensure consistent parameter handling
def _resolve_faceting_config(self, faceting: Optional[FacetingConfig], **kwargs) -> FacetingConfig:
    """Resolve faceting configuration with consistent parameter patterns."""
    
    # Direct parameter resolution (consistent with existing plot methods)
    config_dict = {}
    
    # Core parameters (match existing plot method patterns)
    for param in ['rows', 'cols', 'lines', 'x', 'y']:
        if param in kwargs:
            config_dict[param] = kwargs.pop(param)
        elif faceting and hasattr(faceting, param):
            config_dict[param] = getattr(faceting, param)
    
    # Layout parameters (consistent with FigureConfig)
    for param in ['ncols', 'nrows']:
        if param in kwargs:
            config_dict[param] = kwargs.pop(param)
        elif faceting and hasattr(faceting, param):
            config_dict[param] = getattr(faceting, param)
    
    # Targeting parameters (consistent with subplot indexing conventions)
    for param in ['target_row', 'target_col', 'target_rows', 'target_cols']:
        if param in kwargs:
            config_dict[param] = kwargs.pop(param)
        elif faceting and hasattr(faceting, param):
            config_dict[param] = getattr(faceting, param)
    
    # Subplot configuration (consistent with FigureConfig nested lists)
    for param in ['x_labels', 'y_labels', 'xlim', 'ylim']:
        if param in kwargs:
            config_dict[param] = kwargs.pop(param)
        elif faceting and hasattr(faceting, param):
            config_dict[param] = getattr(faceting, param)
    
    # Create and validate configuration
    resolved_config = FacetingConfig(**config_dict)
    resolved_config.validate()
    
    return resolved_config

def _ensure_plot_kwargs_consistency(self, **kwargs) -> Dict[str, Any]:
    """Ensure plot kwargs follow existing dr_plotter conventions."""
    
    # Map any faceting-specific parameter names to standard plot parameters
    consistent_kwargs = {}
    
    for key, value in kwargs.items():
        # Ensure color parameter consistency
        if key in ['color', 'c']:
            consistent_kwargs['color'] = value
        # Ensure marker parameter consistency  
        elif key in ['marker', 'm']:
            consistent_kwargs['marker'] = value
        # Ensure linestyle parameter consistency
        elif key in ['linestyle', 'ls']:
            consistent_kwargs['linestyle'] = value
        # Pass through all other parameters unchanged
        else:
            consistent_kwargs[key] = value
    
    return consistent_kwargs
```

4. **Existing Feature Compatibility**:
```python
# Ensure faceting works with existing dr_plotter features

def _validate_faceting_compatibility_with_existing_features(self, config: FacetingConfig) -> None:
    """Validate that faceting configuration is compatible with existing figure setup."""
    
    # Check compatibility with external axes
    if self.external_mode and (config.rows or config.cols):
        print("Warning: Faceting with external axes may not work as expected. "
              "Consider using FigureManager without external_ax for faceting.")
    
    # Check grid compatibility
    if hasattr(self, 'figure_config'):
        fig_rows, fig_cols = self.figure_config.rows, self.figure_config.cols
        
        # Warn if faceting grid doesn't match figure grid
        if config.rows and config.cols:
            # Will be validated in _compute_facet_grid, but warn early
            pass
    
    # Check legend compatibility
    if self.legend_manager and config.lines:
        # Legend will be handled by _coordinate_faceted_legends
        pass

# Ensure plot method integration
def plot(self, plot_type: str, row: int, col: int, data: pd.DataFrame, 
         hue_by: Optional[str] = None, **kwargs) -> None:
    """Enhanced plot method with faceting awareness."""
    
    # Check if this is part of a faceted plot
    is_faceted_plot = hasattr(self, '_facet_grid_info') and self._facet_grid_info is not None
    
    if is_faceted_plot:
        # Apply faceting-specific enhancements
        kwargs = self._apply_faceting_plot_enhancements(row, col, hue_by, **kwargs)
    
    # Call existing plot implementation
    return self._plot_implementation(plot_type, row, col, data, hue_by=hue_by, **kwargs)

def _apply_faceting_plot_enhancements(self, row: int, col: int, 
                                    hue_by: Optional[str], **kwargs) -> Dict[str, Any]:
    """Apply faceting-specific plot enhancements."""
    
    # If coordinated colors are provided, use them
    if '_coordinated_colors' in kwargs:
        # Handle coordinated styling (from style coordination)
        coordinated_colors = kwargs.pop('_coordinated_colors')
        coordinated_markers = kwargs.pop('_coordinated_markers', None)
        
        # Apply coordinated styling through existing parameter patterns
        if hue_by and len(coordinated_colors) > 1:
            kwargs['palette'] = coordinated_colors  # Use existing palette parameter
        elif len(coordinated_colors) == 1:
            kwargs['color'] = coordinated_colors[0]
    
    return kwargs
```

5. **Integration Testing Framework**:
```python
# Add comprehensive integration tests
# In tests/test_faceting_integration.py

class TestExistingFeatureIntegration:
    def test_faceting_with_themes(self):
        """Test that faceting respects existing theme system."""
        from dr_plotter.theme import create_custom_theme
        
        custom_theme = create_custom_theme(
            color_palette=['red', 'blue', 'green'],
            marker_styles=['o', 's', '^']
        )
        
        data = create_test_data()
        
        with FigureManager(
            figure=FigureConfig(rows=2, cols=2),
            theme=custom_theme
        ) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",
                cols="dataset", 
                lines="model_size",
                x="step",
                y="value"
            )
            
            # Verify theme colors are used in faceting
            style_coordinator = fm._facet_style_coordinator
            assert style_coordinator is not None
            # Check that theme colors appear in style assignments
            model_styles = style_coordinator._style_assignments.get("model_size", {})
            theme_colors = custom_theme.color_palette
            
            used_colors = [style.get('color') for style in model_styles.values()]
            assert any(color in used_colors for color in theme_colors)
    
    def test_faceting_with_legends(self):
        """Test that faceting integrates with legend system."""
        data = create_test_data()
        
        legend_config = LegendConfig(
            strategy=LegendStrategy.GROUPED_BY_CHANNEL,
            position='right'
        )
        
        with FigureManager(
            figure=FigureConfig(rows=2, cols=2),
            legend=legend_config
        ) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset",
                lines="model_size",
                x="step", 
                y="value"
            )
            
            # Verify legend was created and positioned correctly
            assert fm.legend_manager is not None
            # Check that legend entries match faceted dimension values
    
    def test_faceting_parameter_consistency(self):
        """Test that faceting parameters follow dr_plotter conventions."""
        data = create_test_data()
        
        # Test parameter name consistency
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Both config and direct parameters should work
            fm.plot_faceted(
                data=data,
                plot_type="scatter",
                rows="metric",  # Direct parameter
                cols="dataset", # Direct parameter
                x="step",       # Consistent with plot() method
                y="value",      # Consistent with plot() method
                color='blue',   # Standard plot parameter
                alpha=0.7       # Standard plot parameter
            )
        
        # Test that it works the same with FacetingConfig
        config = FacetingConfig(rows="metric", cols="dataset", x="step", y="value")
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            fm.plot_faceted(
                data=data,
                plot_type="scatter", 
                faceting=config,
                color='blue',
                alpha=0.7
            )
    
    def test_backward_compatibility_preserved(self):
        """Test that existing dr_plotter functionality works unchanged."""
        data = create_test_data()
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            # Regular plot should work exactly as before
            fm.plot("scatter", 0, 0, data, x="step", y="value", 
                   hue_by="model_size", alpha=0.6)
            
            # No faceting state should be created
            assert not hasattr(fm, '_facet_grid_info') or fm._facet_grid_info is None
            
            # Legend should work as before
            if fm.legend_manager:
                fm.legend_manager.apply_legend(fm.fig)
```

### Task 4: Documentation & Examples

**Problem**: Users need clear documentation and examples to understand and use the faceting system effectively.

**Files to create/enhance**:
- `src/dr_plotter/figure.py` - Add comprehensive docstrings to plot_faceted
- `src/dr_plotter/faceting_config.py` - Document all parameters with examples
- `examples/faceted_plotting_guide.py` - Create comprehensive usage examples
- `docs/faceting_migration_guide.md` - Migration guide from manual subplot management

**Implementation**:

1. **Comprehensive Method Documentation**:
```python
# In src/dr_plotter/figure.py - enhance plot_faceted docstring
def plot_faceted(
    self, 
    data: pd.DataFrame, 
    plot_type: str, 
    faceting: Optional[FacetingConfig] = None,
    **kwargs
) -> None:
    """
    Create faceted plots with automatic subplot layout and consistent styling.
    
    Transform multi-dimensional data into organized subplot grids with minimal code.
    Replaces manual subplot management with intelligent automatic layout.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to plot. Must contain columns specified in faceting dimensions.
    plot_type : str  
        Type of plot to create. Supports all standard dr_plotter plot types:
        'line', 'scatter', 'bar', 'fill_between', 'heatmap', etc.
    faceting : FacetingConfig, optional
        Faceting configuration object. If None, uses parameters from kwargs.
        
    **kwargs
        Faceting parameters (used if faceting=None) and plot styling parameters.
        
        Faceting Parameters:
        - rows : str, optional
            Column name to facet across rows. Each unique value gets a row.
        - cols : str, optional  
            Column name to facet across columns. Each unique value gets a column.
        - lines : str, optional
            Column name for within-subplot grouping (hue). Creates different 
            colored/styled lines/points within each subplot.
        - ncols : int, optional
            Number of columns for wrapped layout. Use with 'rows' only.
            Example: rows='metric' (6 metrics), ncols=3 → 2×3 grid
        - nrows : int, optional
            Number of rows for wrapped layout. Use with 'cols' only.
            
        Targeting Parameters (for layered faceting):
        - target_row : int, optional
            Plot only in specific row (0-indexed).
        - target_col : int, optional  
            Plot only in specific column (0-indexed).
        - target_rows : List[int], optional
            Plot only in specific rows.
        - target_cols : List[int], optional
            Plot only in specific columns.
            
        Subplot Configuration:
        - x_labels : List[List[Optional[str]]], optional
            Custom x-axis labels for each subplot. Must match grid dimensions.
        - y_labels : List[List[Optional[str]]], optional
            Custom y-axis labels for each subplot.
        - xlim : List[List[Optional[Tuple[float, float]]]], optional
            Custom x-axis limits for each subplot.
        - ylim : List[List[Optional[Tuple[float, float]]]], optional  
            Custom y-axis limits for each subplot.
            
        Plot Parameters:
        - x : str, optional
            Column name for x-axis data.
        - y : str, optional
            Column name for y-axis data.
        - All standard plot kwargs (color, alpha, linewidth, etc.)
    
    Examples
    --------
    Basic 2D faceting:
    >>> fm.plot_faceted(data, 'line', rows='metric', cols='dataset', 
    ...                 lines='model', x='step', y='value')
    
    Wrapped layout (6 metrics in 2×3 grid):
    >>> fm.plot_faceted(data, 'scatter', rows='metric', ncols=3,
    ...                 x='step', y='value', alpha=0.6)
    
    Layered faceting (multiple plot calls on same grid):
    >>> fm.plot_faceted(scatter_data, 'scatter', rows='metric', cols='dataset',
    ...                 lines='model', x='step', y='value', alpha=0.4)
    >>> fm.plot_faceted(trend_data, 'line', rows='metric', cols='dataset', 
    ...                 lines='model', x='step', y='trend', linewidth=2)
    
    Targeted plotting (overlay on specific subplots):
    >>> fm.plot_faceted(base_data, 'scatter', rows='metric', cols='dataset',
    ...                 x='step', y='value')
    >>> fm.plot_faceted(highlight_data, 'line', rows='metric', cols='dataset',
    ...                 target_row=0, target_cols=[1, 2], 
    ...                 x='step', y='value', color='red', linewidth=3)
    
    Custom subplot configuration:
    >>> x_labels = [['Time', 'Epochs'], ['Steps', 'Iterations']]
    >>> fm.plot_faceted(data, 'line', rows='metric', cols='dataset',
    ...                 x_labels=x_labels, x='step', y='value')
    
    Notes
    -----
    - Same 'lines' dimension values get consistent colors across all subplots
    - Multiple plot_faceted() calls on same FigureManager create layered plots
    - Targeting allows selective plotting for complex layered visualizations  
    - Grid dimensions are computed automatically from data
    - Empty subplots are handled according to empty_subplot_strategy
    
    Raises
    ------
    AssertionError
        If required columns are missing, configuration is invalid, or 
        grid dimensions don't match FigureManager setup.
    """
```

2. **FacetingConfig Documentation**:
```python
# In src/dr_plotter/faceting_config.py - enhance class docstring
@dataclass
class FacetingConfig:
    """
    Configuration for faceted plotting with automatic subplot layout.
    
    Defines how data should be organized across subplot grids and how
    plots should be styled consistently across subplots.
    
    Parameters
    ----------
    rows : str, optional
        Column name to facet across rows. Each unique value becomes a row.
        Example: rows='metric' with ['loss', 'accuracy'] → 2-row grid
        
    cols : str, optional  
        Column name to facet across columns. Each unique value becomes a column.
        Example: cols='dataset' with ['train', 'val', 'test'] → 3-column grid
        
    lines : str, optional
        Column name for within-subplot grouping. Creates different colored/styled
        elements within each subplot with consistent styling across subplots.
        Example: lines='model_size' with ['7B', '13B'] → 2 colored lines per subplot
        
    ncols : int, optional
        Number of columns for wrapped row layout. Use with 'rows' only.
        Example: rows='metric' (6 values), ncols=3 → 2×3 grid (6 metrics wrapped)
        Cannot be used with 'cols'.
        
    nrows : int, optional  
        Number of rows for wrapped column layout. Use with 'cols' only.
        Example: cols='model' (8 models), nrows=4 → 4×2 grid (8 models wrapped)
        Cannot be used with 'rows'.
        
    row_order : List[str], optional
        Custom ordering for row dimension values. If None, uses sorted order.
        Example: row_order=['val_loss', 'train_loss'] (custom metric order)
        
    col_order : List[str], optional
        Custom ordering for column dimension values.
        
    lines_order : List[str], optional  
        Custom ordering for lines dimension values. Affects legend order.
        
    target_row : int, optional
        Plot only in specific row (0-indexed). For layered faceting.
        Cannot be used with target_rows.
        
    target_col : int, optional
        Plot only in specific column (0-indexed). For layered faceting.  
        Cannot be used with target_cols.
        
    target_rows : List[int], optional
        Plot only in specific rows. For layered faceting.
        Example: target_rows=[0, 2] → plot only in first and third rows
        
    target_cols : List[int], optional
        Plot only in specific columns. For layered faceting.
        
    x : str, optional
        Column name for x-axis data. Convenience parameter.
        
    y : str, optional  
        Column name for y-axis data. Convenience parameter.
        
    x_labels : List[List[Optional[str]]], optional
        Custom x-axis labels for each subplot. Nested list structure must
        match computed grid dimensions (rows × cols).
        Example: x_labels=[['Time', 'Steps'], ['Hours', 'Epochs']] for 2×2 grid
        
    y_labels : List[List[Optional[str]]], optional
        Custom y-axis labels for each subplot.
        
    xlim : List[List[Optional[Tuple[float, float]]]], optional
        Custom x-axis limits for each subplot.
        Example: xlim=[[(0, 100), None], [(50, 150), (0, 200)]] for 2×2 grid
        
    ylim : List[List[Optional[Tuple[float, float]]]], optional
        Custom y-axis limits for each subplot.
        
    subplot_titles : str or List[List[Optional[str]]], optional
        Subplot titles. If str, used as template with dimension values.
        If nested list, explicit titles for each subplot.
        
    title_template : str, optional  
        Template for automatic subplot titles using dimension values.
        Example: '{metric} - {dataset}' → 'accuracy - train'
        
    shared_x : str or bool, optional
        Share x-axis across subplots. Options: True/False, 'all', 'row', 'col'
        
    shared_y : str or bool, optional
        Share y-axis across subplots. Options: True/False, 'all', 'row', 'col'
        
    empty_subplot_strategy : str, default 'warn'
        How to handle empty subplots. Options: 'warn', 'error', 'silent'
        
    color_wrap : bool, default False
        Whether to wrap colors when more groups than colors available.
        
    Examples
    --------
    Basic 2D grid:
    >>> config = FacetingConfig(rows='metric', cols='dataset', lines='model')
    
    Wrapped layout:  
    >>> config = FacetingConfig(rows='metric', ncols=3, lines='model_size')
    
    Targeted layering:
    >>> config = FacetingConfig(rows='metric', cols='dataset', target_row=0)
    
    Custom subplot configuration:
    >>> config = FacetingConfig(
    ...     rows='metric', cols='dataset',
    ...     x_labels=[['Time', 'Steps'], ['Hours', 'Epochs']],
    ...     xlim=[[(0, 100), (0, 200)], [(50, 150), (100, 300)]]
    ... )
    
    Notes
    -----
    - Must specify at least one of 'rows' or 'cols'
    - Cannot mix explicit grid (rows+cols) with wrapped layout (ncols/nrows)
    - Targeting parameters are for layered faceting scenarios
    - Nested list parameters must match computed grid dimensions
    """
```

3. **Comprehensive Usage Examples**:
```python
# Create examples/faceted_plotting_guide.py
"""
Dr_Plotter Faceted Plotting Comprehensive Guide

This guide demonstrates all faceting capabilities with real-world examples.
Run each section independently to see different faceting patterns.
"""

import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.faceting_config import FacetingConfig

def create_ml_training_data():
    """Create realistic ML training data for examples."""
    np.random.seed(42)
    data = []
    
    for step in range(0, 1000, 10):
        for metric in ['train_loss', 'val_loss', 'train_acc', 'val_acc']:
            for model_size in ['7B', '13B', '30B', '65B']:
                for dataset in ['squad', 'glue', 'c4']:
                    if metric.endswith('loss'):
                        value = 2.0 * np.exp(-step/300) + np.random.normal(0, 0.1)
                    else:  # accuracy
                        value = 0.9 * (1 - np.exp(-step/400)) + np.random.normal(0, 0.05)
                    
                    data.append({
                        'step': step,
                        'metric': metric,
                        'model_size': model_size,
                        'dataset': dataset, 
                        'value': value
                    })
    
    return pd.DataFrame(data)

def example_1_basic_2d_faceting():
    """Example 1: Basic 2D faceting - the most common use case."""
    print("=== Example 1: Basic 2D Faceting ===")
    
    data = create_ml_training_data()
    
    # Before faceting (manual subplot management):
    # - 95+ lines of subplot creation, data filtering, and plotting
    # - Manual color/marker coordination
    # - Complex legend management
    
    # After faceting (single API call):
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",      # 4 metrics → 2×2 grid (will adjust to 2×3)  
            cols="dataset",     # 3 datasets → columns
            lines="model_size", # 4 model sizes → colored lines
            x="step",
            y="value",
            linewidth=2,
            alpha=0.8
        )
        
        print(f"Created {2*3} subplots with {len(data['model_size'].unique())} "
              f"consistently colored model sizes")
        print("Same model sizes have identical colors across all subplots")

def example_2_wrapped_layouts():
    """Example 2: Wrapped layouts for many categories."""
    print("\n=== Example 2: Wrapped Layouts ===")
    
    # Create data with many metrics
    data = create_ml_training_data()
    metrics = ['train_loss', 'val_loss', 'train_acc', 'val_acc', 'train_f1', 'val_f1']
    data = data[data['metric'].isin(metrics)]  # 6 metrics
    
    # Wrap 6 metrics into 2×3 grid instead of 6×1
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="scatter",
            rows="metric",      # 6 metrics
            ncols=3,           # Wrap into 2×3 grid
            lines="model_size", # Consistent colors
            x="step", 
            y="value",
            alpha=0.6,
            s=20
        )
        
        print("Wrapped 6 metrics into 2×3 grid instead of 6×1")
        print("Much better use of figure space")

def example_3_layered_faceting():
    """Example 3: Layered faceting - multiple plot types on same grid."""
    print("\n=== Example 3: Layered Faceting ===") 
    
    data = create_ml_training_data()
    
    # Create different data layers
    scatter_data = data[data['step'] % 50 == 0]  # Sparse points
    line_data = data[data['step'] % 20 == 0]     # Trend lines
    
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        # Layer 1: Base scatter points  
        fm.plot_faceted(
            data=scatter_data,
            plot_type="scatter",
            rows="metric",
            cols="dataset",
            lines="model_size",  # Colors coordinated across layers
            x="step", 
            y="value",
            alpha=0.4,
            s=30
        )
        
        # Layer 2: Trend lines (same grid, same colors!)
        fm.plot_faceted(
            data=line_data,
            plot_type="line", 
            rows="metric",
            cols="dataset", 
            lines="model_size",  # Same colors as scatter layer
            x="step",
            y="value",
            linewidth=2,
            alpha=0.8
        )
        
        print("Created layered visualization:")
        print("- Scatter points showing data distribution")  
        print("- Line trends with SAME colors as scatter points")
        print("Model sizes have consistent colors across both layers")

def example_4_targeted_plotting():
    """Example 4: Targeted plotting for complex layered visualizations.""" 
    print("\n=== Example 4: Targeted Plotting ===")
    
    data = create_ml_training_data()
    
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        # Base layer: All subplots
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric", 
            cols="dataset",
            lines="model_size",
            x="step",
            y="value",
            alpha=0.6,
            linewidth=1
        )
        
        # Highlight layer: Only specific subplots
        highlight_data = data[data['model_size'] == '65B']  # Best model
        
        fm.plot_faceted(
            data=highlight_data,
            plot_type="line",
            rows="metric",
            cols="dataset", 
            lines="model_size",
            target_row=0,           # Only first row (train metrics)
            target_cols=[1, 2],     # Only glue and c4 datasets
            x="step",
            y="value", 
            linewidth=4,            # Thick highlight
            color='red'             # Override coordinated color
        )
        
        print("Created targeted overlay:")
        print("- Base lines for all models in all subplots")
        print("- Thick red highlight for best model in specific subplots only")

def example_5_custom_subplot_configuration():
    """Example 5: Custom subplot configuration with labels and limits."""
    print("\n=== Example 5: Custom Subplot Configuration ===")
    
    data = create_ml_training_data()
    
    # Custom labels and limits for each subplot
    x_labels = [
        ['Training Steps', 'Training Steps', 'Training Steps'],  # Row 0
        ['Validation Steps', 'Validation Steps', 'Validation Steps']  # Row 1  
    ]
    
    xlim = [
        [(0, 500), (0, 800), (100, 900)],    # Row 0 limits
        [(50, 600), (0, 1000), (200, 800)]   # Row 1 limits
    ]
    
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="scatter",
            rows="metric",
            cols="dataset", 
            lines="model_size",
            x_labels=x_labels,   # Custom labels
            xlim=xlim,          # Custom limits
            x="step",
            y="value",
            alpha=0.7,
            s=25
        )
        
        print("Applied custom configuration:")
        print("- Different x-axis labels for each subplot")
        print("- Different x-axis limits for each subplot") 
        print("- Per-subplot control while maintaining color coordination")

def example_6_migration_comparison():
    """Example 6: Before/After comparison showing migration benefits."""
    print("\n=== Example 6: Migration Comparison ===")
    
    data = create_ml_training_data().head(200)  # Smaller dataset for demo
    
    print("BEFORE FACETING (manual subplot management):")
    print("```python")
    print("# 95+ lines of code required:")
    print("fig, axes = plt.subplots(2, 3, figsize=(18, 10))")
    print("metrics = sorted(data['metric'].unique())")
    print("datasets = sorted(data['dataset'].unique())") 
    print("model_colors = {'7B': 'blue', '13B': 'orange', ...}")
    print("")
    print("for i, metric in enumerate(metrics[:2]):")  
    print("    for j, dataset in enumerate(datasets):")
    print("        ax = axes[i, j]")
    print("        subset = data[(data['metric'] == metric) &")
    print("                     (data['dataset'] == dataset)]")
    print("        for model in sorted(subset['model_size'].unique()):")
    print("            model_data = subset[subset['model_size'] == model]")
    print("            ax.plot(model_data['step'], model_data['value'],")
    print("                   color=model_colors[model], label=model)")
    print("        ax.set_title(f'{metric} - {dataset}')")
    print("        ax.set_xlabel('Step')")
    print("        ax.set_ylabel('Value')")
    print("# ... more lines for legend coordination, styling, etc.")
    print("```")
    
    print("\nAFTER FACETING (single API call):")
    print("```python")
    print("# 5 lines of code:")
    print("fm.plot_faceted(")
    print("    data=data, plot_type='line',")  
    print("    rows='metric', cols='dataset', lines='model_size',")
    print("    x='step', y='value'")
    print(")")
    print("```")
    
    # Actually create the faceted version
    with FigureManager(figure=FigureConfig(rows=2, cols=3, figsize=(18, 10))) as fm:
        fm.plot_faceted(
            data=data,
            plot_type="line",
            rows="metric",
            cols="dataset",
            lines="model_size", 
            x="step",
            y="value"
        )
        
        print(f"\nFaceting Benefits:")
        print(f"- Reduced from 95+ lines to 5 lines (95% reduction)")
        print(f"- Automatic color coordination across subplots")
        print(f"- Automatic grid layout computation")
        print(f"- Automatic legend management") 
        print(f"- Support for layered plots and targeting")
        print(f"- Consistent with dr_plotter API patterns")

if __name__ == "__main__":
    """Run all examples to demonstrate faceting capabilities."""
    
    print("Dr_Plotter Faceted Plotting Guide")
    print("=" * 50)
    
    # Run all examples
    example_1_basic_2d_faceting()
    example_2_wrapped_layouts()
    example_3_layered_faceting()
    example_4_targeted_plotting()
    example_5_custom_subplot_configuration() 
    example_6_migration_comparison()
    
    print(f"\n" + "=" * 50)
    print("All examples completed!")
    print("Try modifying the examples to explore different faceting patterns.")
```

4. **Migration Guide**:
```markdown
# Create docs/faceting_migration_guide.md
# Faceted Plotting Migration Guide

This guide helps you migrate from manual subplot management to dr_plotter's native faceting system.

## Why Migrate?

**Before faceting** - Manual subplot management requires:
- 95+ lines of boilerplate code for complex grids
- Manual data filtering and subsetting
- Manual color/marker coordination across subplots  
- Complex legend management
- Error-prone subplot indexing

**After faceting** - Single API call:
- 5 lines of code for the same result
- Automatic data organization and layout
- Consistent styling across subplots and layers
- Integrated legend management  
- Robust error handling and validation

## Migration Patterns

### Pattern 1: Basic Grid Layout

**Before:**
```python
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
metrics = ['train_loss', 'val_loss']
datasets = ['squad', 'glue', 'c4'] 
colors = {'7B': 'blue', '13B': 'orange', '30B': 'green'}

for i, metric in enumerate(metrics):
    for j, dataset in enumerate(datasets):
        ax = axes[i, j]
        subset = data[(data['metric'] == metric) & (data['dataset'] == dataset)]
        
        for model in ['7B', '13B', '30B']:
            model_data = subset[subset['model_size'] == model]
            ax.plot(model_data['step'], model_data['value'], 
                   color=colors[model], label=model, linewidth=2)
        
        ax.set_title(f'{metric} - {dataset}')
        ax.set_xlabel('Step')
        ax.set_ylabel('Value')
        if i == 0 and j == 0:
            ax.legend()
```

**After:**
```python
fm.plot_faceted(
    data=data, plot_type='line',
    rows='metric', cols='dataset', lines='model_size',
    x='step', y='value', linewidth=2
)
```

### Pattern 2: Wrapped Layouts  

**Before:**
```python
# Complex logic to arrange 6 metrics in 2×3 grid
metrics = data['metric'].unique()
n_metrics = len(metrics)
n_cols = 3
n_rows = (n_metrics + n_cols - 1) // n_cols  # Ceiling division

fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 10))
axes = axes.flatten()

for i, metric in enumerate(metrics):
    if i >= len(axes):
        break
    ax = axes[i]
    # ... plotting logic ...
    
# Hide unused subplots
for i in range(n_metrics, len(axes)):
    axes[i].set_visible(False)
```

**After:**
```python  
fm.plot_faceted(
    data=data, plot_type='scatter',
    rows='metric', ncols=3,  # Automatic wrapping
    lines='model_size', x='step', y='value'
)
```

### Pattern 3: Layered Plots

**Before:**
```python  
# Layer 1: Scatter
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
# ... complex subplot management for scatter ...

# Layer 2: Lines - must manually ensure color consistency  
colors_used = {}  # Track colors from first layer
for i, metric in enumerate(metrics):
    for j, dataset in enumerate(datasets):
        ax = axes[i, j]
        # ... complex logic to reuse same colors ...
```

**After:**
```python
# Layer 1: Scatter
fm.plot_faceted(scatter_data, 'scatter', 
               rows='metric', cols='dataset', lines='model_size',
               x='step', y='value', alpha=0.4)

# Layer 2: Lines - colors automatically coordinated!
fm.plot_faceted(line_data, 'line',
               rows='metric', cols='dataset', lines='model_size', 
               x='step', y='value', linewidth=2)
```

## Step-by-Step Migration

### Step 1: Identify Your Grid Structure
- **Rows dimension**: What varies across rows?
- **Columns dimension**: What varies across columns?  
- **Lines dimension**: What creates different colors/markers within subplots?

### Step 2: Replace Manual Subplot Creation
```python
# Replace this:
fig, axes = plt.subplots(n_rows, n_cols)

# With this:
fm = FigureManager(figure=FigureConfig(rows=n_rows, cols=n_cols))
```

### Step 3: Replace Manual Data Filtering
```python
# Replace complex filtering:
for i, row_val in enumerate(row_values):
    for j, col_val in enumerate(col_values):
        subset = data[(data[row_dim] == row_val) & (data[col_dim] == col_val)]
        
# With automatic faceting:
fm.plot_faceted(data, plot_type, rows=row_dim, cols=col_dim, ...)
```

### Step 4: Replace Manual Color Coordination
```python
# Replace manual color management:
colors = {'A': 'blue', 'B': 'orange', 'C': 'green'}
for group in groups:
    ax.plot(..., color=colors[group])

# With automatic coordination:
fm.plot_faceted(data, plot_type, ..., lines='group_column')
```

### Step 5: Simplify Legend Management
```python
# Replace complex legend logic:
handles, labels = [], []
for ax in axes.flat:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)
# ... deduplication and positioning ...

# With automatic legend:
# Legends are handled automatically by faceting system
```

## Common Pitfalls and Solutions

### Pitfall 1: Column Name Confusion
```python
# Wrong - using display names
fm.plot_faceted(data, 'line', rows='Train Loss', cols='Squad Dataset')

# Right - using actual column names  
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')
```

### Pitfall 2: Forgetting Grid Setup
```python
# Wrong - grid too small for faceted data
fm = FigureManager(figure=FigureConfig(rows=1, cols=1))  
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')  # Error!

# Right - appropriate grid size
fm = FigureManager(figure=FigureConfig(rows=2, cols=3))
fm.plot_faceted(data, 'line', rows='metric', cols='dataset')
```

### Pitfall 3: Mixed Parameter Styles
```python
# Inconsistent - some params in config, some direct
config = FacetingConfig(rows='metric', cols='dataset') 
fm.plot_faceted(data, 'line', faceting=config, lines='model')  # Mixed

# Better - all in config or all direct
fm.plot_faceted(data, 'line', rows='metric', cols='dataset', lines='model')
```

## Performance Considerations

### Large Datasets
```python
# For datasets > 10K rows, consider filtering first:
recent_data = data[data['step'] > 500]  # Filter before faceting
fm.plot_faceted(recent_data, 'line', ...)
```

### Many Subplots  
```python
# For >20 subplots, consider wrapped layouts:
fm.plot_faceted(data, 'scatter', rows='metric', ncols=4)  # Instead of 1×20
```

### Multiple Layers
```python
# Create all layers before styling adjustments:
fm.plot_faceted(layer1_data, 'scatter', ...)
fm.plot_faceted(layer2_data, 'line', ...)  
fm.plot_faceted(layer3_data, 'line', ...)
# Then apply figure-level styling
```

## Benefits Summary

✅ **95% code reduction** - From 95+ lines to 5 lines
✅ **Automatic color coordination** - Same values get same colors  
✅ **Layered plotting** - Multiple plot calls on same grid
✅ **Targeted plotting** - Selective subplot targeting
✅ **Error prevention** - Robust validation and helpful errors
✅ **Consistent API** - Follows dr_plotter patterns
✅ **Performance optimized** - Efficient for large datasets
✅ **Extensible** - Easy to add new plot types and features

Start with basic 2D faceting and gradually adopt advanced features as needed!
```

### Task 5: Edge Cases & Robustness

**Problem**: Faceting must handle all edge cases gracefully with helpful error messages and fallback behavior.

**Files to enhance**:
- `src/dr_plotter/faceting/validation.py` - Add edge case validation
- `src/dr_plotter/faceting/data_preparation.py` - Handle sparse and missing data
- `src/dr_plotter/figure.py` - Robust error handling in plot_faceted
- `tests/test_faceting_edge_cases.py` - Comprehensive edge case testing

**Implementation**:

1. **Empty and Sparse Data Handling**:
```python
# In src/dr_plotter/faceting/validation.py
def validate_data_completeness(data: pd.DataFrame, config: FacetingConfig) -> None:
    """Validate data completeness and warn about potential issues."""
    
    # Handle completely empty DataFrame
    if data.empty:
        assert False, (
            "Cannot create faceted plot with empty DataFrame. "
            "Please provide data with at least one row."
        )
    
    # Check for dimensions with no data
    required_dims = []
    if config.rows:
        required_dims.append(config.rows)
    if config.cols:
        required_dims.append(config.cols)
    if config.lines:
        required_dims.append(config.lines)
    
    for dim in required_dims:
        if dim in data.columns:
            unique_count = data[dim].nunique()
            total_null = data[dim].isnull().sum()
            
            if unique_count == 0:
                assert False, (
                    f"Dimension '{dim}' has no non-null values. "
                    f"Cannot create faceted plot without valid dimension values."
                )
            
            if unique_count == 1:
                single_value = data[dim].dropna().iloc[0] if len(data[dim].dropna()) > 0 else "null"
                print(f"Warning: Dimension '{dim}' has only one unique value: '{single_value}'. "
                      f"This will create a single-row/column grid. Consider using a different dimension.")
            
            if total_null > len(data) * 0.5:
                print(f"Warning: Dimension '{dim}' has {total_null}/{len(data)} null values ({total_null/len(data)*100:.1f}%). "
                      f"Many subplots may be empty.")

def validate_subplot_data_coverage(data: pd.DataFrame, config: FacetingConfig) -> Dict[str, Any]:
    """Analyze data coverage across potential subplots."""
    
    coverage_info = {
        'total_combinations': 1,
        'populated_combinations': 0,
        'empty_combinations': [],
        'sparse_combinations': []
    }
    
    # Calculate theoretical grid size
    if config.rows and config.rows in data.columns:
        row_values = data[config.rows].dropna().unique()
        coverage_info['total_combinations'] *= len(row_values)
        coverage_info['row_values'] = row_values.tolist()
    
    if config.cols and config.cols in data.columns:
        col_values = data[config.cols].dropna().unique()  
        coverage_info['total_combinations'] *= len(col_values)
        coverage_info['col_values'] = col_values.tolist()
    
    # Check actual data coverage
    if config.rows and config.cols:
        if config.rows in data.columns and config.cols in data.columns:
            # Group by both dimensions to find populated combinations
            grouped = data.groupby([config.rows, config.cols]).size()
            coverage_info['populated_combinations'] = len(grouped)
            
            # Find empty combinations
            for row_val in coverage_info.get('row_values', []):
                for col_val in coverage_info.get('col_values', []):
                    if (row_val, col_val) not in grouped.index:
                        coverage_info['empty_combinations'].append((row_val, col_val))
                    elif grouped.loc[(row_val, col_val)] < 3:
                        coverage_info['sparse_combinations'].append(
                            (row_val, col_val, grouped.loc[(row_val, col_val)])
                        )
    
    # Warn about coverage issues
    if coverage_info['empty_combinations']:
        empty_count = len(coverage_info['empty_combinations'])
        if empty_count > coverage_info['total_combinations'] * 0.3:
            print(f"Warning: {empty_count}/{coverage_info['total_combinations']} "
                  f"subplot combinations have no data ({empty_count/coverage_info['total_combinations']*100:.1f}%). "
                  f"Consider filtering data or using different dimensions.")
    
    if coverage_info['sparse_combinations']:
        sparse_count = len(coverage_info['sparse_combinations'])
        print(f"Warning: {sparse_count} subplot(s) have very few data points (< 3). "
              f"Plots may not be meaningful.")
    
    return coverage_info

# In src/dr_plotter/faceting/data_preparation.py
def handle_empty_subplots(data_subsets: Dict[Tuple[int, int], pd.DataFrame], 
                         empty_subplot_strategy: str) -> Dict[Tuple[int, int], pd.DataFrame]:
    """Handle empty subplots according to strategy."""
    
    empty_positions = []
    for pos, subset in data_subsets.items():
        if subset.empty:
            empty_positions.append(pos)
    
    if empty_positions:
        if empty_subplot_strategy == "error":
            assert False, (
                f"Empty subplots found at positions {empty_positions}. "
                f"Set empty_subplot_strategy='warn' or 'silent' to allow empty subplots, "
                f"or filter your data to ensure all subplot combinations have data."
            )
        elif empty_subplot_strategy == "warn":
            print(f"Warning: Empty subplots at positions {empty_positions}. "
                  f"These subplots will remain empty.")
        elif empty_subplot_strategy == "silent":
            pass  # Do nothing
        else:
            assert False, f"Invalid empty_subplot_strategy: '{empty_subplot_strategy}'. Use 'warn', 'error', or 'silent'."
    
    return data_subsets
```

2. **Invalid Configuration Handling**:
```python
# In src/dr_plotter/figure.py - robust configuration validation
def _validate_faceting_configuration_robustly(self, config: FacetingConfig, data: pd.DataFrame) -> None:
    """Comprehensive validation of faceting configuration against data."""
    
    # Basic configuration validation
    config.validate()
    
    # Data-aware validation
    try:
        validate_faceting_data_requirements(data, config)
    except AssertionError as e:
        # Enhance error with recovery suggestions
        error_msg = str(e)
        if "Missing columns" in error_msg:
            available_cols = sorted(data.columns.tolist())
            error_msg += f"\n\nRecovery suggestions:"
            error_msg += f"\n• Check column names for typos"
            error_msg += f"\n• Use data.columns to see available columns: {available_cols[:5]}..."
            if len(available_cols) > 5:
                error_msg += f" (and {len(available_cols)-5} more)"
        
        assert False, error_msg
    
    # Check for dimension compatibility
    if config.rows and config.cols:
        if config.rows in data.columns and config.cols in data.columns:
            # Check if combination would create reasonable grid
            n_rows = data[config.rows].nunique()
            n_cols = data[config.cols].nunique()
            total_subplots = n_rows * n_cols
            
            if total_subplots > 50:
                print(f"Warning: Large grid ({n_rows}×{n_cols} = {total_subplots} subplots) "
                      f"may be difficult to read. Consider:")
                print(f"• Using wrapped layouts: rows='{config.rows}', ncols=4")
                print(f"• Filtering data to fewer categories")
                print(f"• Using different grouping dimensions")
    
    # Validate targeting against computed grid
    if any([config.target_row, config.target_col, config.target_rows, config.target_cols]):
        # Will be validated during grid computation, but give early warning
        pass
    
    # Check for reasonable data distribution
    coverage_info = validate_subplot_data_coverage(data, config)
    return coverage_info

def _handle_faceting_errors_gracefully(self, error: Exception, data: pd.DataFrame, 
                                     config: FacetingConfig) -> None:
    """Provide helpful error context and recovery suggestions."""
    
    error_context = {
        'data_shape': data.shape,
        'data_columns': data.columns.tolist(),
        'config_summary': {
            'rows': config.rows,
            'cols': config.cols, 
            'lines': config.lines,
            'ncols': config.ncols,
            'nrows': config.nrows
        }
    }
    
    error_msg = f"Faceted plotting failed: {str(error)}\n"
    error_msg += f"\nContext:\n"
    error_msg += f"• Data shape: {error_context['data_shape']}\n"
    error_msg += f"• Available columns: {error_context['data_columns'][:5]}..."
    if len(error_context['data_columns']) > 5:
        error_msg += f" (and {len(error_context['data_columns'])-5} more)\n"
    else:
        error_msg += "\n"
    error_msg += f"• Faceting config: {error_context['config_summary']}\n"
    
    # Add specific recovery suggestions based on error type
    if "Missing columns" in str(error):
        error_msg += f"\nRecovery suggestions:\n"
        error_msg += f"• Check that column names match exactly (case-sensitive)\n"
        error_msg += f"• Use data.head() to inspect your data structure\n"
        error_msg += f"• Verify data loading worked correctly\n"
    elif "grid" in str(error).lower():
        error_msg += f"\nGrid-related recovery suggestions:\n"
        error_msg += f"• Ensure FigureManager grid size matches your data dimensions\n"
        error_msg += f"• Check if you need wrapped layout (ncols/nrows)\n"
        error_msg += f"• Consider filtering data to reduce grid size\n"
    elif "empty" in str(error).lower():
        error_msg += f"\nEmpty data recovery suggestions:\n" 
        error_msg += f"• Check data filtering - you may have filtered out all data\n"
        error_msg += f"• Use data.groupby(['{config.rows}', '{config.cols}']).size() to check coverage\n"
        error_msg += f"• Set empty_subplot_strategy='warn' to allow empty subplots\n"
    
    assert False, error_msg
```

3. **Boundary Condition Handling**:
```python
# Handle edge cases in grid computation
# In src/dr_plotter/faceting/grid_computation.py
def compute_grid_dimensions_robust(data: pd.DataFrame, config: FacetingConfig) -> Tuple[int, int]:
    """Robust grid dimension computation with edge case handling."""
    
    # Handle single dimension cases
    if config.rows and not config.cols and not config.ncols:
        # Single row dimension - create single column
        return (data[config.rows].nunique(), 1)
    
    if config.cols and not config.rows and not config.nrows:
        # Single column dimension - create single row
        return (1, data[config.cols].nunique())
    
    # Handle wrapped layouts with edge cases
    if config.rows and config.ncols:
        n_items = data[config.rows].nunique()
        n_cols = config.ncols
        
        if n_cols <= 0:
            assert False, f"ncols must be positive, got {n_cols}"
        if n_cols > n_items:
            print(f"Warning: ncols ({n_cols}) is larger than number of items ({n_items}). "
                  f"Some columns will be empty.")
        
        n_rows = (n_items + n_cols - 1) // n_cols  # Ceiling division
        return (n_rows, n_cols)
    
    if config.cols and config.nrows:
        n_items = data[config.cols].nunique()
        n_rows = config.nrows
        
        if n_rows <= 0:
            assert False, f"nrows must be positive, got {n_rows}"
        if n_rows > n_items:
            print(f"Warning: nrows ({n_rows}) is larger than number of items ({n_items}). "
                  f"Some rows will be empty.")
        
        n_cols = (n_items + n_rows - 1) // n_rows  # Ceiling division
        return (n_rows, n_cols)
    
    # Handle explicit grid
    if config.rows and config.cols:
        n_rows = data[config.rows].nunique()
        n_cols = data[config.cols].nunique()
        
        if n_rows == 0 or n_cols == 0:
            assert False, "Cannot create grid with zero rows or columns. Check your data dimensions."
        
        return (n_rows, n_cols)
    
    # Fallback - shouldn't reach here if validation worked
    assert False, "Invalid grid configuration - must specify at least one dimension"

def validate_targeting_against_grid(config: FacetingConfig, grid_rows: int, grid_cols: int) -> None:
    """Validate targeting parameters against computed grid."""
    
    # Validate single targeting
    if config.target_row is not None:
        if config.target_row < 0 or config.target_row >= grid_rows:
            assert False, (
                f"target_row={config.target_row} is out of bounds. "
                f"Grid has {grid_rows} rows (0-{grid_rows-1})."
            )
    
    if config.target_col is not None:
        if config.target_col < 0 or config.target_col >= grid_cols:
            assert False, (
                f"target_col={config.target_col} is out of bounds. "
                f"Grid has {grid_cols} columns (0-{grid_cols-1})."
            )
    
    # Validate multiple targeting
    if config.target_rows is not None:
        for i, row in enumerate(config.target_rows):
            if row < 0 or row >= grid_rows:
                assert False, (
                    f"target_rows[{i}]={row} is out of bounds. "
                    f"Grid has {grid_rows} rows (0-{grid_rows-1})."
                )
    
    if config.target_cols is not None:
        for i, col in enumerate(config.target_cols):
            if col < 0 or col >= grid_cols:
                assert False, (
                    f"target_cols[{i}]={col} is out of bounds. "
                    f"Grid has {grid_cols} columns (0-{grid_cols-1})."
                )
```

4. **Data Type and Format Edge Cases**:
```python
# In src/dr_plotter/faceting/validation.py
def validate_data_types(data: pd.DataFrame, config: FacetingConfig) -> None:
    """Validate that data types are suitable for faceting."""
    
    # Check dimension columns for reasonable types
    dimension_cols = [col for col in [config.rows, config.cols, config.lines] if col and col in data.columns]
    
    for col in dimension_cols:
        dtype = data[col].dtype
        
        # Handle datetime columns
        if pd.api.types.is_datetime64_any_dtype(dtype):
            unique_count = data[col].nunique()
            if unique_count > 20:
                print(f"Warning: Datetime column '{col}' has {unique_count} unique values. "
                      f"This may create a very large grid. Consider binning datetime values.")
        
        # Handle float columns (may have precision issues)
        elif pd.api.types.is_float_dtype(dtype):
            unique_count = data[col].nunique()
            if unique_count > 50:
                print(f"Warning: Float column '{col}' has {unique_count} unique values. "
                      f"Floating point precision may create unexpected groups. "
                      f"Consider rounding or binning values.")
        
        # Handle object columns
        elif dtype == 'object':
            # Check for very long strings
            if data[col].dropna().astype(str).str.len().max() > 50:
                print(f"Warning: Column '{col}' contains very long strings. "
                      f"This may cause display issues in subplot labels.")
        
        # Check for mixed types in object columns
        if dtype == 'object':
            sample_types = set(type(x).__name__ for x in data[col].dropna().head(100))
            if len(sample_types) > 1:
                print(f"Warning: Column '{col}' appears to have mixed data types: {sample_types}. "
                      f"This may cause unexpected grouping behavior.")

def validate_data_ranges(data: pd.DataFrame, config: FacetingConfig) -> None:
    """Validate data ranges for plotting columns."""
    
    plot_cols = [col for col in [config.x, config.y] if col and col in data.columns]
    
    for col in plot_cols:
        if pd.api.types.is_numeric_dtype(data[col]):
            # Check for extreme values
            col_min, col_max = data[col].min(), data[col].max()
            col_range = col_max - col_min
            
            if col_range == 0:
                print(f"Warning: Column '{col}' has constant value {col_min}. "
                      f"Plots may not show variation.")
            
            # Check for potential outliers
            q1, q3 = data[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                outlier_threshold = 3 * iqr
                outliers = ((data[col] < (q1 - outlier_threshold)) | 
                           (data[col] > (q3 + outlier_threshold))).sum()
                if outliers > 0:
                    print(f"Warning: Column '{col}' has {outliers} potential outliers "
                          f"that may affect plot scaling.")
```

5. **Memory and Performance Edge Cases**:
```python
# In src/dr_plotter/figure.py
def _check_performance_constraints(self, data: pd.DataFrame, config: FacetingConfig) -> None:
    """Check for performance issues and warn user."""
    
    data_size = len(data)
    memory_usage_mb = data.memory_usage(deep=True).sum() / 1024 / 1024
    
    # Calculate estimated grid size
    estimated_subplots = 1
    if config.rows and config.rows in data.columns:
        estimated_subplots *= data[config.rows].nunique()
    if config.cols and config.cols in data.columns:
        estimated_subplots *= data[config.cols].nunique()
    elif config.ncols:
        estimated_subplots = estimated_subplots * config.ncols if config.rows else config.ncols
    elif config.nrows:
        estimated_subplots = estimated_subplots * config.nrows if config.cols else config.nrows
    
    # Warn about large datasets
    if data_size > 100000:
        print(f"Warning: Large dataset ({data_size:,} rows, {memory_usage_mb:.1f}MB). "
              f"Faceting may be slow. Consider:")
        print(f"• Sampling data: data.sample(n=10000)")
        print(f"• Filtering recent data: data[data['date'] > recent_date]")
        print(f"• Using fewer dimension categories")
    
    # Warn about many subplots
    if estimated_subplots > 30:
        print(f"Warning: Large grid ({estimated_subplots} subplots estimated). "
              f"Consider:")
        print(f"• Wrapped layouts: ncols=4 or nrows=3")
        print(f"• Filtering to fewer categories")
        print(f"• Using different grouping dimensions")
    
    # Warn about memory usage
    estimated_memory_mb = memory_usage_mb * estimated_subplots * 0.1  # Rough estimate
    if estimated_memory_mb > 500:  # 500MB
        print(f"Warning: High estimated memory usage ({estimated_memory_mb:.0f}MB). "
              f"Consider reducing data size or subplot count.")

def _fallback_on_faceting_failure(self, data: pd.DataFrame, plot_type: str, 
                                config: FacetingConfig, **kwargs) -> None:
    """Attempt fallback plotting if faceting fails completely."""
    
    print("Faceting failed. Attempting fallback to single plot...")
    
    try:
        # Try single plot with hue_by
        if config.lines and config.lines in data.columns:
            self.plot(plot_type, 0, 0, data, 
                     x=config.x, y=config.y, hue_by=config.lines, **kwargs)
            print(f"Successfully created single plot with hue_by='{config.lines}'")
        else:
            self.plot(plot_type, 0, 0, data, 
                     x=config.x, y=config.y, **kwargs)  
            print("Successfully created basic single plot")
            
    except Exception as fallback_error:
        print(f"Fallback plotting also failed: {fallback_error}")
        print("Please check your data and plot parameters.")
        raise  # Re-raise the fallback error
```

6. **Comprehensive Edge Case Testing**:
```python
# Create tests/test_faceting_edge_cases.py
"""
Comprehensive edge case testing for faceted plotting.
Tests all boundary conditions and error cases.
"""

import pytest
import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.faceting_config import FacetingConfig

class TestDataEdgeCases:
    def test_empty_dataframe(self):
        """Test handling of completely empty DataFrame."""
        empty_data = pd.DataFrame()
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            with pytest.raises(AssertionError, match="empty DataFrame"):
                fm.plot_faceted(empty_data, "scatter", rows="metric", x="x", y="y")
    
    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrame."""
        single_row = pd.DataFrame({
            'metric': ['accuracy'], 
            'x': [1], 
            'y': [0.8]
        })
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            # Should work but with warnings
            fm.plot_faceted(single_row, "scatter", rows="metric", x="x", y="y")
    
    def test_all_null_dimension_column(self):
        """Test dimension column with all null values."""
        null_data = pd.DataFrame({
            'metric': [None, None, None],
            'x': [1, 2, 3],
            'y': [1, 2, 3]
        })
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            with pytest.raises(AssertionError, match="no non-null values"):
                fm.plot_faceted(null_data, "scatter", rows="metric", x="x", y="y")
    
    def test_single_unique_value_dimension(self):
        """Test dimension with only one unique value."""
        single_val = pd.DataFrame({
            'metric': ['accuracy', 'accuracy', 'accuracy'],
            'x': [1, 2, 3], 
            'y': [0.8, 0.9, 0.85]
        })
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            # Should work but with warning about single value
            fm.plot_faceted(single_val, "scatter", rows="metric", x="x", y="y")
    
    def test_sparse_data_coverage(self):
        """Test data with many missing combinations."""
        sparse_data = pd.DataFrame({
            'metric': ['acc', 'acc', 'loss'],  # Missing loss for dataset2
            'dataset': ['data1', 'data1', 'data1'], # Missing data2 entirely  
            'x': [1, 2, 3],
            'y': [0.8, 0.9, 0.4]
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Should work with warnings about empty subplots
            fm.plot_faceted(sparse_data, "scatter", 
                          rows="metric", cols="dataset", x="x", y="y")

class TestConfigurationEdgeCases:
    def test_invalid_targeting_out_of_bounds(self):
        """Test targeting parameters that exceed grid bounds."""
        data = pd.DataFrame({
            'metric': ['acc', 'loss'] * 5,
            'dataset': ['d1', 'd2'] * 5,
            'x': range(10),
            'y': range(10)
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            with pytest.raises(AssertionError, match="out of bounds"):
                fm.plot_faceted(data, "scatter", 
                              rows="metric", cols="dataset", 
                              target_row=5,  # Out of bounds
                              x="x", y="y")
    
    def test_wrapped_layout_edge_cases(self):
        """Test wrapped layouts with edge cases."""
        data = pd.DataFrame({
            'metric': ['acc', 'loss', 'f1'] * 3, 
            'x': range(9),
            'y': range(9)
        })
        
        # Test ncols > number of items
        with FigureManager(figure=FigureConfig(rows=1, cols=5)) as fm:
            # Should work with warning
            fm.plot_faceted(data, "scatter", rows="metric", ncols=5, x="x", y="y")
    
    def test_extremely_large_grid_warning(self):
        """Test warning for very large grids.""" 
        # Create data that would result in large grid
        large_categories = [f"cat_{i}" for i in range(15)]
        data = pd.DataFrame({
            'row_dim': np.random.choice(large_categories, 100),
            'col_dim': np.random.choice(large_categories, 100),
            'x': range(100),
            'y': np.random.randn(100)
        })
        
        with FigureManager(figure=FigureConfig(rows=15, cols=15)) as fm:
            # Should warn about large grid but still work
            fm.plot_faceted(data, "scatter", 
                          rows="row_dim", cols="col_dim", x="x", y="y")

class TestDataTypeEdgeCases:
    def test_datetime_dimensions(self):
        """Test faceting with datetime columns."""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        data = pd.DataFrame({
            'date': np.random.choice(dates, 100),
            'metric': np.random.choice(['acc', 'loss'], 100),
            'x': range(100),
            'y': np.random.randn(100)
        })
        
        with FigureManager(figure=FigureConfig(rows=5, cols=2)) as fm:
            # Should warn about many datetime values but work
            fm.plot_faceted(data, "scatter", rows="date", cols="metric", x="x", y="y")
    
    def test_float_precision_dimensions(self):
        """Test faceting with float columns that have precision issues."""
        data = pd.DataFrame({
            'float_dim': [0.1, 0.1000001, 0.2, 0.2000001] * 25,  # Precision issues
            'x': range(100),
            'y': np.random.randn(100)
        })
        
        with FigureManager(figure=FigureConfig(rows=4, cols=1)) as fm:
            # Should warn about float precision
            fm.plot_faceted(data, "scatter", rows="float_dim", x="x", y="y")
    
    def test_mixed_type_columns(self):
        """Test columns with mixed data types."""
        data = pd.DataFrame({
            'mixed_col': [1, '2', 3.0, 'four', None] * 20,
            'x': range(100), 
            'y': np.random.randn(100)
        })
        
        with FigureManager(figure=FigureConfig(rows=3, cols=1)) as fm:
            # Should warn about mixed types
            fm.plot_faceted(data, "scatter", rows="mixed_col", x="x", y="y")

class TestPerformanceEdgeCases:
    def test_large_dataset_warning(self):
        """Test warning for very large datasets."""
        large_data = pd.DataFrame({
            'metric': np.random.choice(['acc', 'loss'], 150000),
            'dataset': np.random.choice(['d1', 'd2'], 150000), 
            'x': range(150000),
            'y': np.random.randn(150000)
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Should warn about large dataset
            fm.plot_faceted(large_data, "scatter", 
                          rows="metric", cols="dataset", x="x", y="y")
    
    def test_memory_intensive_scenario(self):
        """Test scenario that would use significant memory."""
        # Many subplots × reasonable data size = high memory
        categories = [f"cat_{i}" for i in range(10)]
        data = pd.DataFrame({
            'row_dim': np.random.choice(categories, 5000), 
            'col_dim': np.random.choice(categories, 5000),
            'lines_dim': np.random.choice(categories, 5000),
            'x': range(5000),
            'y': np.random.randn(5000)
        })
        
        with FigureManager(figure=FigureConfig(rows=10, cols=10)) as fm:
            # Should warn about memory usage
            fm.plot_faceted(data, "scatter",
                          rows="row_dim", cols="col_dim", lines="lines_dim",
                          x="x", y="y")

class TestErrorRecoveryEdgeCases:
    def test_faceting_fallback_to_single_plot(self):
        """Test fallback when faceting fails."""
        # This would require mocking internal failures
        # Implementation depends on actual fallback strategy
        pass
    
    def test_partial_failure_recovery(self):
        """Test recovery from partial failures in plotting.""" 
        # Test scenarios where some subplots fail but others succeed
        pass
```

### Task 6: Final Integration & Polish

**Problem**: Final cleanup and integration to ensure faceting is production-ready and seamlessly integrated.

**Files to polish**:
- `src/dr_plotter/figure.py` - Clean up and optimize final implementation
- `src/dr_plotter/faceting/` - Remove any remaining code duplication
- `src/dr_plotter/__init__.py` - Ensure proper exports for public API
- All implementation files - Final type hint verification and code quality

**Implementation**:

1. **Code Deduplication and Cleanup**:
```python
# In src/dr_plotter/figure.py - consolidate duplicate validation logic
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, **kwargs) -> None:
    """Final polished implementation with all optimizations."""
    
    # Consolidated validation pipeline
    config = self._resolve_faceting_config(faceting, **kwargs)
    self._validate_faceting_pipeline(data, config)
    
    # Optimized execution pipeline
    try:
        self._execute_faceting_pipeline(data, plot_type, config, **kwargs)
    except Exception as e:
        self._handle_faceting_errors_gracefully(e, data, config)
        raise

def _validate_faceting_pipeline(self, data: pd.DataFrame, config: FacetingConfig) -> None:
    """Consolidated validation pipeline - single point of validation."""
    
    # Step 1: Basic configuration validation
    config.validate()
    
    # Step 2: Data completeness and type validation
    from dr_plotter.faceting.validation import (
        validate_faceting_data_requirements,
        validate_data_completeness, 
        validate_data_types,
        validate_data_ranges
    )
    
    validate_faceting_data_requirements(data, config)
    validate_data_completeness(data, config)
    validate_data_types(data, config)
    validate_data_ranges(data, config)
    
    # Step 3: Performance constraint checking
    self._check_performance_constraints(data, config)
    
    # Step 4: Feature compatibility validation
    self._validate_faceting_compatibility_with_existing_features(config)

def _execute_faceting_pipeline(self, data: pd.DataFrame, plot_type: str, 
                              config: FacetingConfig, **kwargs) -> None:
    """Optimized execution pipeline - single path through faceting."""
    
    # Grid computation with caching
    grid_rows, grid_cols, layout_metadata = self._compute_facet_grid_optimized(data, config)
    self._validate_facet_grid_against_existing(grid_rows, grid_cols)
    
    # Validate nested list parameters against computed grid
    self._validate_nested_parameters_against_grid(config, grid_rows, grid_cols)
    
    # Data preparation with targeting optimization
    target_positions = resolve_target_positions(config, grid_rows, grid_cols)
    data_subsets = prepare_subplot_data_subsets(
        data, 
        layout_metadata.get('row_values', []),
        layout_metadata.get('col_values', []),
        config.rows, 
        config.cols,
        target_positions=target_positions
    )
    
    # Handle empty subplots according to strategy
    from dr_plotter.faceting.data_preparation import handle_empty_subplots
    data_subsets = handle_empty_subplots(data_subsets, config.empty_subplot_strategy)
    
    # Style coordination setup
    if config.lines:
        style_coordinator = self._get_or_create_style_coordinator()
        dimension_analysis = analyze_data_dimensions(data, config)
        lines_values = dimension_analysis.get("lines", [])
        style_coordinator.register_dimension_values(config.lines, lines_values)
    
    # Execute plotting with style coordination
    self._execute_coordinated_plotting(plot_type, target_positions, data_subsets, config, **kwargs)
    
    # Final state management
    self._store_faceting_state(config, layout_metadata, grid_rows, grid_cols, data_subsets)
    
    # Legend coordination if applicable
    if config.lines and self.legend_manager:
        self._coordinate_faceted_legends(config, data)

def _validate_nested_parameters_against_grid(self, config: FacetingConfig, 
                                           grid_rows: int, grid_cols: int) -> None:
    """Consolidated nested parameter validation."""
    
    nested_params = [
        ('x_labels', config.x_labels),
        ('y_labels', config.y_labels), 
        ('xlim', config.xlim),
        ('ylim', config.ylim)
    ]
    
    for param_name, param_value in nested_params:
        if param_value is not None:
            validate_nested_list_dimensions(param_value, grid_rows, grid_cols, param_name)

def _execute_coordinated_plotting(self, plot_type: str, target_positions: List[Tuple[int, int]],
                                data_subsets: Dict[Tuple[int, int], pd.DataFrame], 
                                config: FacetingConfig, **kwargs) -> None:
    """Execute plotting with full coordination."""
    
    plot_kwargs = {k: v for k, v in kwargs.items() 
                  if k not in {'rows', 'cols', 'lines', 'x', 'y', 'faceting'}}
    
    for (row_idx, col_idx) in target_positions:
        if (row_idx, col_idx) in data_subsets:
            subset_data = data_subsets[(row_idx, col_idx)]
            
            # Apply per-subplot configuration
            self._apply_subplot_configuration(row_idx, col_idx, config)
            
            # Get coordinated styles
            coordinated_styles = plot_kwargs
            if config.lines and hasattr(self, '_facet_style_coordinator'):
                coordinated_styles = self._facet_style_coordinator.get_subplot_styles(
                    row_idx, col_idx, config.lines, subset_data, **plot_kwargs
                )
            
            # Execute plot with all enhancements
            self.plot(plot_type, row_idx, col_idx, subset_data, 
                     x=config.x, y=config.y, hue_by=config.lines, **coordinated_styles)
```

2. **Import Structure Optimization**:
```python
# In src/dr_plotter/__init__.py - ensure proper public API exports
"""
Dr_Plotter: Advanced plotting library with native faceting support.
"""

from .figure import FigureManager
from .figure_config import FigureConfig  
from .faceting_config import FacetingConfig  # NEW: Export faceting config
from .legend_manager import LegendConfig, LegendStrategy
from .theme import Theme, BASE_THEME

# Export key faceting functionality for advanced users
from .faceting import (
    FacetStyleCoordinator,  # For custom style coordination
    GridLayout,             # For advanced grid manipulation
)

__version__ = "1.0.0"  # Update version for faceting release

__all__ = [
    # Core classes
    "FigureManager",
    "FigureConfig", 
    "FacetingConfig",      # NEW
    "LegendConfig",
    "LegendStrategy",
    "Theme",
    "BASE_THEME",
    
    # Advanced faceting (for power users)
    "FacetStyleCoordinator",  # NEW
    "GridLayout",             # NEW
    
    # Version
    "__version__",
]

# In src/dr_plotter/faceting/__init__.py - optimize imports
"""
Faceting module: Core functionality for multi-dimensional plotting.

This module provides the foundational components for faceted plotting:
- Grid computation and layout algorithms
- Data analysis and preparation for subplots  
- Style coordination across subplots and layers
- Validation and error handling
"""

# Core functionality - always imported
from .grid_computation import (
    compute_grid_dimensions,
    compute_grid_layout_metadata,
    resolve_target_positions,
)

from .data_analysis import (
    extract_dimension_values,
    analyze_data_dimensions,
    detect_missing_combinations,
)

from .data_preparation import (
    create_data_subset,
    prepare_subplot_data_subsets,
)

from .validation import (
    validate_required_columns,
    validate_dimension_values,
    get_available_columns_message,
    validate_faceting_data_requirements,
    validate_nested_list_dimensions,
)

from .types import GridLayout, SubplotPosition, DataSubsets

# Advanced functionality - imported on demand  
from .style_coordination import FacetStyleCoordinator

# Clean __all__ export
__all__ = [
    # Grid computation
    "compute_grid_dimensions",
    "compute_grid_layout_metadata", 
    "resolve_target_positions",
    
    # Data analysis
    "extract_dimension_values",
    "analyze_data_dimensions",
    "detect_missing_combinations",
    
    # Data preparation  
    "create_data_subset",
    "prepare_subplot_data_subsets",
    
    # Validation
    "validate_required_columns", 
    "validate_dimension_values",
    "get_available_columns_message",
    "validate_faceting_data_requirements",
    "validate_nested_list_dimensions",
    
    # Types
    "GridLayout",
    "SubplotPosition", 
    "DataSubsets",
    
    # Style coordination
    "FacetStyleCoordinator",
]
```

3. **Type Hint Verification and Enhancement**:
```python
# Comprehensive type hint verification across all files

# In src/dr_plotter/faceting_config.py - ensure all type hints are complete
from __future__ import annotations  # For forward references
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

@dataclass
class FacetingConfig:
    """Complete type annotations for all parameters."""
    
    # Core dimensions
    rows: Optional[str] = None
    cols: Optional[str] = None  
    lines: Optional[str] = None
    
    # Layout control
    ncols: Optional[int] = None
    nrows: Optional[int] = None
    
    # Ordering
    row_order: Optional[List[str]] = None
    col_order: Optional[List[str]] = None
    lines_order: Optional[List[str]] = None
    
    # Targeting  
    target_row: Optional[int] = None
    target_col: Optional[int] = None
    target_rows: Optional[List[int]] = None
    target_cols: Optional[List[int]] = None
    
    # Plot parameters
    x: Optional[str] = None
    y: Optional[str] = None
    
    # Subplot configuration - precise nested list types
    x_labels: Optional[List[List[Optional[str]]]] = None
    y_labels: Optional[List[List[Optional[str]]]] = None
    xlim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    ylim: Optional[List[List[Optional[Tuple[float, float]]]]] = None
    
    # Advanced features
    subplot_titles: Optional[Union[str, List[List[Optional[str]]]]] = None
    title_template: Optional[str] = None
    shared_x: Optional[Union[str, bool]] = None
    shared_y: Optional[Union[str, bool]] = None
    empty_subplot_strategy: str = "warn"
    color_wrap: bool = False
    
    def validate(self) -> None:
        """Type-annotated validation method."""
        # ... existing validation with type assertions ...

# In src/dr_plotter/figure.py - verify all method signatures
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig

class FigureManager:
    """All methods with complete type annotations."""
    
    def plot_faceted(
        self, 
        data: pd.DataFrame, 
        plot_type: str, 
        faceting: Optional[FacetingConfig] = None,
        **kwargs: Any
    ) -> None:
        """Fully type-annotated plot_faceted method."""
        
    def _resolve_faceting_config(
        self, 
        faceting: Optional[FacetingConfig], 
        **kwargs: Any
    ) -> FacetingConfig:
        """Type-safe configuration resolution."""
        
    def _validate_faceting_pipeline(
        self, 
        data: pd.DataFrame, 
        config: FacetingConfig
    ) -> None:
        """Type-safe validation pipeline."""
        
    def _execute_faceting_pipeline(
        self, 
        data: pd.DataFrame, 
        plot_type: str,
        config: FacetingConfig, 
        **kwargs: Any
    ) -> None:
        """Type-safe execution pipeline."""
        
    def _apply_subplot_configuration(
        self, 
        row: int, 
        col: int, 
        config: FacetingConfig
    ) -> None:
        """Type-safe subplot configuration."""
        
    def _get_or_create_style_coordinator(self) -> 'FacetStyleCoordinator':
        """Type-safe style coordinator factory."""

# All faceting module functions with complete type hints
# In src/dr_plotter/faceting/grid_computation.py
from typing import Dict, List, Tuple, Any
import pandas as pd
from dr_plotter.faceting_config import FacetingConfig

def compute_grid_dimensions(data: pd.DataFrame, config: FacetingConfig) -> Tuple[int, int]:
    """Complete type annotations for grid computation."""

def compute_grid_layout_metadata(
    data: pd.DataFrame, 
    config: FacetingConfig,
    grid_rows: int,
    grid_cols: int
) -> Dict[str, Any]:
    """Complete type annotations for layout metadata."""

def resolve_target_positions(
    config: FacetingConfig, 
    grid_rows: int, 
    grid_cols: int
) -> List[Tuple[int, int]]:
    """Complete type annotations for targeting."""
```

4. **Memory Management and Cleanup**:
```python
# In src/dr_plotter/figure.py - add proper cleanup methods
class FigureManager:
    """Enhanced with proper lifecycle management."""
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Enhanced cleanup with faceting state management."""
        
        # Clean up faceting state
        if hasattr(self, '_facet_style_coordinator'):
            self._facet_style_coordinator = None
        
        if hasattr(self, '_facet_grid_info'):
            self._facet_grid_info = None
        
        # Call parent cleanup
        super().__exit__(exc_type, exc_val, exc_tb)
    
    def clear_faceting_state(self) -> None:
        """Manually clear faceting state for memory management."""
        
        if hasattr(self, '_facet_style_coordinator'):
            self._facet_style_coordinator = None
            
        if hasattr(self, '_facet_grid_info'): 
            self._facet_grid_info = None
        
        print("Faceting state cleared.")

# In src/dr_plotter/faceting/style_coordination.py - memory management
class FacetStyleCoordinator:
    """Enhanced with proper memory management."""
    
    def clear_cache(self) -> None:
        """Clear style coordination cache to free memory."""
        self._dimension_values.clear()
        self._style_assignments.clear()
        self._cycle_positions.clear()
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics for debugging."""
        return {
            'dimensions': len(self._dimension_values),
            'style_assignments': sum(len(assignments) for assignments in self._style_assignments.values()),
            'total_cached_values': sum(len(values) for values in self._dimension_values.values())
        }
```

5. **Final Code Quality Verification**:
```python
# Code quality checklist implementation

# Remove any remaining TODO or FIXME comments
# Verify all assertions use project patterns (not exceptions)
# Ensure all print statements use consistent formatting
# Verify import organization (all imports at top)
# Check docstring consistency (remove all docstrings per project standards)
# Verify variable naming consistency 
# Check for any remaining code duplication
# Ensure error messages are helpful and consistent

# Example of final polished code style:
def validate_faceting_data_requirements(data: pd.DataFrame, config: FacetingConfig) -> None:
    assert isinstance(data, pd.DataFrame), f"data must be DataFrame, got {type(data)}"
    
    required_columns = []
    if config.rows is not None:
        required_columns.append(config.rows)
    if config.cols is not None:
        required_columns.append(config.cols)
    if config.lines is not None:
        required_columns.append(config.lines)
    if config.x is not None:
        required_columns.append(config.x)
    if config.y is not None:
        required_columns.append(config.y)
    
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        available = sorted(data.columns.tolist())
        similar_suggestions = _suggest_similar_columns(missing_columns, available)
        
        error_msg = f"Missing required columns: {missing_columns}\nAvailable columns: {available}"
        if similar_suggestions:
            error_msg += f"\nDid you mean: {similar_suggestions}?"
        
        assert False, error_msg
```

6. **Performance Benchmarking Integration**:
```python
# In src/dr_plotter/figure.py - add optional performance tracking
def plot_faceted(self, data: pd.DataFrame, plot_type: str, 
                faceting: Optional[FacetingConfig] = None, 
                _benchmark: bool = False, **kwargs) -> None:
    """Enhanced with optional performance benchmarking."""
    
    if _benchmark:
        import time
        start_time = time.time()
        
        # Execute normal faceting
        config = self._resolve_faceting_config(faceting, **kwargs)
        self._validate_faceting_pipeline(data, config)
        
        validation_time = time.time()
        
        self._execute_faceting_pipeline(data, plot_type, config, **kwargs)
        
        execution_time = time.time()
        
        # Report performance
        total_time = execution_time - start_time
        validation_duration = validation_time - start_time
        plotting_duration = execution_time - validation_time
        
        print(f"Faceting Performance:")
        print(f"• Total time: {total_time:.3f}s")
        print(f"• Validation: {validation_duration:.3f}s ({validation_duration/total_time*100:.1f}%)")
        print(f"• Plotting: {plotting_duration:.3f}s ({plotting_duration/total_time*100:.1f}%)")
        print(f"• Data size: {len(data):,} rows")
        
        # Store benchmarking info
        if not hasattr(self, '_performance_history'):
            self._performance_history = []
        
        self._performance_history.append({
            'data_size': len(data),
            'total_time': total_time,
            'validation_time': validation_duration,
            'plotting_time': plotting_duration,
            'plot_type': plot_type
        })
    else:
        # Normal execution path
        config = self._resolve_faceting_config(faceting, **kwargs)
        self._validate_faceting_pipeline(data, config)
        self._execute_faceting_pipeline(data, plot_type, config, **kwargs)

def get_performance_summary(self) -> Dict[str, Any]:
    """Get performance summary for optimization."""
    if not hasattr(self, '_performance_history') or not self._performance_history:
        return {"message": "No performance data available. Use _benchmark=True in plot_faceted()"}
    
    history = self._performance_history
    
    return {
        'total_calls': len(history),
        'avg_total_time': sum(h['total_time'] for h in history) / len(history),
        'avg_data_size': sum(h['data_size'] for h in history) // len(history),
        'slowest_call': max(history, key=lambda x: x['total_time']),
        'fastest_call': min(history, key=lambda x: x['total_time'])
    }
```

7. **Final Integration Testing Framework**:
```python
# Create tests/test_faceting_final_integration.py
"""
Final integration testing to verify all faceting components work together.
"""

import pytest
import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.faceting_config import FacetingConfig

class TestProductionReadiness:
    def test_complete_faceting_workflow(self):
        """Test complete end-to-end faceting workflow."""
        # Create comprehensive test data
        np.random.seed(42)
        data = pd.DataFrame({
            'step': list(range(100)) * 12,
            'metric': ['train_loss', 'val_loss', 'train_acc', 'val_acc'] * 300,
            'model_size': ['7B', '13B', '30B'] * 400,
            'dataset': ['squad', 'glue'] * 600,
            'value': np.random.randn(1200) * 0.1 + 0.5
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2, figsize=(12, 8))) as fm:
            # Test all major features in single workflow
            
            # Layer 1: Base faceted plot
            fm.plot_faceted(
                data=data,
                plot_type="line",
                rows="metric",
                cols="dataset", 
                lines="model_size",
                x="step",
                y="value",
                alpha=0.7
            )
            
            # Layer 2: Targeted overlay
            highlight_data = data[data['model_size'] == '30B']
            fm.plot_faceted(
                data=highlight_data,
                plot_type="scatter",
                rows="metric",
                cols="dataset",
                lines="model_size", 
                target_row=0,  # Only first row
                x="step",
                y="value",
                s=50,
                alpha=0.9
            )
            
            # Verify state management
            assert hasattr(fm, '_facet_grid_info')
            assert hasattr(fm, '_facet_style_coordinator')
            assert fm._facet_style_coordinator is not None
            
            # Verify style coordination worked
            style_coordinator = fm._facet_style_coordinator
            assert 'model_size' in style_coordinator._style_assignments
            assert len(style_coordinator._style_assignments['model_size']) == 3  # 7B, 13B, 30B
    
    def test_memory_management(self):
        """Test that memory is properly managed."""
        data = pd.DataFrame({
            'metric': ['acc', 'loss'] * 100,
            'dataset': ['d1', 'd2'] * 100, 
            'model': ['m1', 'm2'] * 100,
            'x': range(200),
            'y': np.random.randn(200)
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                          lines="model", x="x", y="y")
            
            # Check memory usage
            if hasattr(fm, '_facet_style_coordinator'):
                memory_info = fm._facet_style_coordinator.get_memory_usage()
                assert memory_info['dimensions'] <= 5  # Memory limit working
            
            # Test manual cleanup
            fm.clear_faceting_state()
            assert not hasattr(fm, '_facet_style_coordinator') or fm._facet_style_coordinator is None
    
    def test_api_consistency(self):
        """Test that faceting API is consistent with dr_plotter patterns."""
        data = pd.DataFrame({
            'metric': ['acc', 'loss'] * 10,
            'x': range(20),
            'y': range(20)
        })
        
        # Test both configuration approaches work identically
        with FigureManager(figure=FigureConfig(rows=1, cols=2)) as fm1:
            # Direct parameters
            fm1.plot_faceted(data, "line", rows="metric", x="x", y="y")
        
        with FigureManager(figure=FigureConfig(rows=1, cols=2)) as fm2:
            # Configuration object
            config = FacetingConfig(rows="metric", x="x", y="y")
            fm2.plot_faceted(data, "line", faceting=config)
        
        # Both approaches should create equivalent plots
        # (Detailed verification would require plot comparison)
    
    def test_error_handling_robustness(self):
        """Test that all error conditions are handled gracefully."""
        # Test various error conditions
        invalid_data_scenarios = [
            pd.DataFrame(),  # Empty
            pd.DataFrame({'x': [1, 2], 'y': [None, None]}),  # All null values
            pd.DataFrame({'metric': [1, '2', 3.0], 'x': [1, 2, 3], 'y': [1, 2, 3]})  # Mixed types
        ]
        
        for i, data in enumerate(invalid_data_scenarios):
            with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
                with pytest.raises(AssertionError):  # Should fail gracefully with helpful messages
                    fm.plot_faceted(data, "scatter", rows="metric", x="x", y="y")
    
    def test_performance_benchmarking(self):
        """Test optional performance benchmarking."""
        data = pd.DataFrame({
            'metric': ['acc', 'loss'] * 500,
            'dataset': ['d1', 'd2'] * 500,
            'x': range(1000),
            'y': np.random.randn(1000)
        })
        
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Test benchmarking mode
            fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                          x="x", y="y", _benchmark=True)
            
            # Verify performance data was collected
            perf_summary = fm.get_performance_summary()
            assert 'total_calls' in perf_summary
            assert perf_summary['total_calls'] == 1

class TestBackwardCompatibility:
    def test_existing_functionality_unchanged(self):
        """Ensure existing dr_plotter functionality works exactly as before."""
        data = pd.DataFrame({'x': range(10), 'y': range(10), 'category': ['A', 'B'] * 5})
        
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            # Regular plot should work exactly as before faceting implementation
            fm.plot("scatter", 0, 0, data, x="x", y="y", hue_by="category")
            
            # Should not create any faceting state
            assert not hasattr(fm, '_facet_grid_info') or fm._facet_grid_info is None
    
    def test_import_structure_backward_compatible(self):
        """Test that all existing imports still work."""
        # These imports should all work without changes
        from dr_plotter.figure import FigureManager
        from dr_plotter.figure_config import FigureConfig
        from dr_plotter.legend_manager import LegendConfig
        
        # New imports should also work
        from dr_plotter.faceting_config import FacetingConfig
        from dr_plotter import FacetingConfig as DirectFacetingConfig
        
        assert FacetingConfig is not None
        assert DirectFacetingConfig is not None
        assert FacetingConfig is DirectFacetingConfig
```

### Task 7: Quality Assurance

**Problem**: Ensure comprehensive testing and validation of all faceting functionality before final release.

**Files to test**:
- All existing faceting tests must pass
- New validation and edge case tests must pass
- Performance benchmarks must meet acceptable thresholds
- Integration with existing dr_plotter features must work flawlessly

**Implementation**:

1. **Comprehensive Test Execution and Verification**:
```bash
# Execute full test suite in specific order to catch any issues

# Step 1: Core faceting functionality tests
pytest tests/test_faceting_config.py -v
pytest tests/test_faceting_grid_computation.py -v  
pytest tests/test_faceting_integration.py -v

# Step 2: Module-level tests (from refactoring)
pytest tests/faceting/ -v

# Step 3: Style coordination tests
pytest tests/test_faceting_style_coordination.py -v

# Step 4: Edge cases and validation tests
pytest tests/test_faceting_edge_cases.py -v

# Step 5: Final integration tests
pytest tests/test_faceting_final_integration.py -v

# Step 6: Full dr_plotter test suite (backward compatibility)
pytest tests/ -x --tb=short

# Expected results:
# - All faceting tests pass (should be 100+ tests total)
# - All existing dr_plotter tests continue to pass
# - No performance regressions
# - Memory usage stays within reasonable bounds
```

2. **Performance Benchmark Validation**:
```python
# Create performance validation script
# File: scripts/validate_faceting_performance.py

import time
import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig

def run_performance_benchmarks():
    """Execute performance benchmarks and validate results."""
    
    print("=== Faceting Performance Validation ===")
    
    # Benchmark scenarios
    scenarios = {
        'small_data_small_grid': {
            'data_size': 500,
            'grid': (2, 2),
            'max_time': 1.0  # 1 second max
        },
        'medium_data_medium_grid': {
            'data_size': 2000, 
            'grid': (3, 3),
            'max_time': 3.0  # 3 seconds max
        },
        'large_data_small_grid': {
            'data_size': 10000,
            'grid': (2, 2), 
            'max_time': 5.0  # 5 seconds max
        }
    }
    
    results = {}
    
    for scenario_name, params in scenarios.items():
        print(f"\n--- {scenario_name} ---")
        
        # Create test data
        np.random.seed(42)
        data = pd.DataFrame({
            'metric': np.random.choice(['acc', 'loss'], params['data_size']),
            'dataset': np.random.choice(['d1', 'd2', 'd3'], params['data_size']),
            'model': np.random.choice(['m1', 'm2', 'm3'], params['data_size']),
            'x': range(params['data_size']),
            'y': np.random.randn(params['data_size'])
        })
        
        # Benchmark faceting
        start_time = time.time()
        
        with FigureManager(figure=FigureConfig(rows=params['grid'][0], 
                                               cols=params['grid'][1])) as fm:
            fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                          lines="model", x="x", y="y", _benchmark=True)
            
            perf_summary = fm.get_performance_summary()
        
        total_time = time.time() - start_time
        
        # Validate performance
        passed = total_time <= params['max_time']
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"Time: {total_time:.3f}s (max: {params['max_time']}s) {status}")
        print(f"Data: {params['data_size']:,} rows, Grid: {params['grid']}")
        
        if perf_summary and 'avg_total_time' in perf_summary:
            print(f"Detailed: {perf_summary['avg_total_time']:.3f}s avg")
        
        results[scenario_name] = {
            'time': total_time,
            'max_time': params['max_time'],
            'passed': passed,
            'data_size': params['data_size']
        }
    
    # Overall assessment
    all_passed = all(r['passed'] for r in results.values())
    
    print(f"\n=== Performance Summary ===")
    print(f"Scenarios tested: {len(scenarios)}")
    print(f"Passed: {sum(1 for r in results.values() if r['passed'])}")
    print(f"Failed: {sum(1 for r in results.values() if not r['passed'])}")
    print(f"Overall: {'✓ ALL BENCHMARKS PASSED' if all_passed else '✗ SOME BENCHMARKS FAILED'}")
    
    if not all_passed:
        print("Performance issues detected. Consider optimization.")
        for name, result in results.items():
            if not result['passed']:
                print(f"  - {name}: {result['time']:.3f}s > {result['max_time']:.3f}s")
    
    return all_passed

if __name__ == "__main__":
    success = run_performance_benchmarks()
    exit(0 if success else 1)
```

3. **Memory Usage Validation**:
```python
# Create memory validation script  
# File: scripts/validate_faceting_memory.py

import tracemalloc
import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig

def run_memory_validation():
    """Validate memory usage patterns for faceting."""
    
    print("=== Memory Usage Validation ===")
    
    # Start memory tracking
    tracemalloc.start()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'basic_faceting',
            'data_size': 1000,
            'expected_peak_mb': 50  # 50MB max
        },
        {
            'name': 'layered_faceting',
            'data_size': 1000, 
            'expected_peak_mb': 100  # 100MB max
        },
        {
            'name': 'style_coordination',
            'data_size': 2000,
            'expected_peak_mb': 75  # 75MB max
        }
    ]
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        # Reset memory tracking
        tracemalloc.clear_traces()
        
        # Create test data
        data = pd.DataFrame({
            'metric': np.random.choice(['acc', 'loss', 'f1'], scenario['data_size']),
            'dataset': np.random.choice(['d1', 'd2', 'd3'], scenario['data_size']),
            'model': np.random.choice(['m1', 'm2', 'm3', 'm4'], scenario['data_size']),
            'x': range(scenario['data_size']),
            'y': np.random.randn(scenario['data_size'])
        })
        
        # Execute scenario
        if scenario['name'] == 'basic_faceting':
            with FigureManager(figure=FigureConfig(rows=3, cols=3)) as fm:
                fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                              lines="model", x="x", y="y")
        
        elif scenario['name'] == 'layered_faceting':
            with FigureManager(figure=FigureConfig(rows=3, cols=3)) as fm:
                # Multiple layers
                fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                              lines="model", x="x", y="y", alpha=0.6)
                fm.plot_faceted(data, "line", rows="metric", cols="dataset", 
                              lines="model", x="x", y="y", linewidth=2)
        
        elif scenario['name'] == 'style_coordination':
            with FigureManager(figure=FigureConfig(rows=3, cols=3)) as fm:
                # Test style coordinator memory usage
                fm.plot_faceted(data, "scatter", rows="metric", cols="dataset", 
                              lines="model", x="x", y="y")
                
                # Check style coordinator memory
                if hasattr(fm, '_facet_style_coordinator'):
                    memory_info = fm._facet_style_coordinator.get_memory_usage()
                    print(f"Style coordinator: {memory_info}")
        
        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()
        peak_mb = peak / 1024 / 1024
        
        # Validate memory usage
        passed = peak_mb <= scenario['expected_peak_mb']
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"Peak memory: {peak_mb:.1f}MB (max: {scenario['expected_peak_mb']}MB) {status}")
        print(f"Current: {current / 1024 / 1024:.1f}MB")
        
        results[scenario['name']] = {
            'peak_mb': peak_mb,
            'expected_mb': scenario['expected_peak_mb'],
            'passed': passed
        }
    
    # Overall assessment
    tracemalloc.stop()
    
    all_passed = all(r['passed'] for r in results.values())
    
    print(f"\n=== Memory Summary ===")
    print(f"Scenarios tested: {len(scenarios)}")
    print(f"Passed: {sum(1 for r in results.values() if r['passed'])}")
    print(f"Failed: {sum(1 for r in results.values() if not r['passed'])}")
    print(f"Overall: {'✓ ALL MEMORY TESTS PASSED' if all_passed else '✗ SOME MEMORY TESTS FAILED'}")
    
    if not all_passed:
        print("Memory issues detected:")
        for name, result in results.items():
            if not result['passed']:
                print(f"  - {name}: {result['peak_mb']:.1f}MB > {result['expected_mb']:.1f}MB")
    
    return all_passed

if __name__ == "__main__":
    success = run_memory_validation()
    exit(0 if success else 1)
```

4. **Integration Testing with Existing Features**:
```python
# Create comprehensive integration test
# File: tests/test_complete_integration.py

import pytest
import pandas as pd
import numpy as np
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.faceting_config import FacetingConfig
from dr_plotter.legend_manager import LegendConfig, LegendStrategy

class TestCompleteIntegration:
    """Test faceting integration with all existing dr_plotter features."""
    
    def test_faceting_with_all_features(self):
        """Test faceting works with themes, legends, and all configurations."""
        
        data = pd.DataFrame({
            'step': list(range(50)) * 8,
            'metric': ['train_loss', 'val_loss'] * 200,
            'dataset': ['squad', 'glue'] * 200,
            'model': ['7B', '13B'] * 200,
            'value': np.random.randn(400) * 0.1 + 0.5
        })
        
        # Test with all possible configurations
        legend_config = LegendConfig(
            strategy=LegendStrategy.GROUPED_BY_CHANNEL,
            position='right'
        )
        
        figure_config = FigureConfig(
            rows=2, cols=2, figsize=(12, 8),
            x_labels=[['Steps', 'Steps'], ['Time', 'Time']],
            shared_x='col'
        )
        
        faceting_config = FacetingConfig(
            rows='metric',
            cols='dataset', 
            lines='model',
            x='step',
            y='value',
            empty_subplot_strategy='warn'
        )
        
        with FigureManager(
            figure=figure_config,
            legend=legend_config,
            # theme=custom_theme  # Would test if theme available
        ) as fm:
            # Test comprehensive faceting
            fm.plot_faceted(
                data=data,
                plot_type="line",
                faceting=faceting_config,
                linewidth=2,
                alpha=0.8
            )
            
            # Verify all components work
            assert hasattr(fm, '_facet_grid_info')
            assert hasattr(fm, '_facet_style_coordinator')
            assert fm.legend_manager is not None
            
            # Test layered plotting still works
            highlight_data = data[data['model'] == '13B']
            fm.plot_faceted(
                data=highlight_data,
                plot_type="scatter",
                rows='metric',
                cols='dataset',
                lines='model',
                x='step',
                y='value',
                s=50,
                alpha=0.9
            )
    
    def test_backward_compatibility_complete(self):
        """Comprehensive backward compatibility test."""
        
        data = pd.DataFrame({
            'x': range(20),
            'y': np.random.randn(20),
            'category': ['A', 'B'] * 10,
            'size': np.random.randint(10, 100, 20)
        })
        
        # Test that ALL existing functionality still works
        with FigureManager(figure=FigureConfig(rows=2, cols=2)) as fm:
            # Regular plots in specific positions
            fm.plot("scatter", 0, 0, data, x="x", y="y", hue_by="category")
            fm.plot("line", 0, 1, data, x="x", y="y", color="red")
            fm.plot("scatter", 1, 0, data, x="x", y="y", s="size", alpha=0.6)
            
            # Should not interfere with faceting state
            assert not hasattr(fm, '_facet_grid_info') or fm._facet_grid_info is None
            
            # Now add faceting - should work alongside regular plots
            facet_data = pd.DataFrame({
                'metric': ['acc'] * 10 + ['loss'] * 10,
                'x': range(20),
                'y': np.random.randn(20)
            })
            
            fm.plot_faceted(facet_data, "line", rows="metric", target_row=1, 
                          target_col=1, x="x", y="y")
            
            # Now should have faceting state
            assert hasattr(fm, '_facet_grid_info')
    
    def test_error_handling_comprehensive(self):
        """Test all error handling scenarios work properly."""
        
        # Test configuration errors
        with pytest.raises(AssertionError, match="Must specify at least one"):
            config = FacetingConfig()
            config.validate()
        
        # Test data errors
        empty_data = pd.DataFrame()
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            with pytest.raises(AssertionError, match="empty DataFrame"):
                fm.plot_faceted(empty_data, "scatter", rows="metric")
        
        # Test missing column errors
        data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            with pytest.raises(AssertionError, match="Missing"):
                fm.plot_faceted(data, "scatter", rows="missing_column", x="x", y="y")
        
        # Test grid mismatch errors  
        data = pd.DataFrame({'metric': ['a', 'b'], 'x': [1, 2], 'y': [3, 4]})
        with FigureManager(figure=FigureConfig(rows=1, cols=1)) as fm:
            with pytest.raises(AssertionError, match="grid"):
                fm.plot_faceted(data, "scatter", rows="metric", x="x", y="y")
```

5. **Final Quality Gates and Checklist**:
```python
# Create quality validation script
# File: scripts/validate_faceting_quality.py

import subprocess
import sys
from pathlib import Path

def run_quality_gates():
    """Run all quality gates for faceting implementation."""
    
    print("=== Faceting Quality Validation ===")
    
    # Quality gates to run
    gates = [
        {
            'name': 'Type Checking',
            'command': ['uv', 'run', 'mypy', 'src/dr_plotter/'],
            'required': True
        },
        {
            'name': 'Code Formatting',
            'command': ['uv', 'run', 'ruff', 'format', '--check', 'src/'],
            'required': True
        },
        {
            'name': 'Code Linting', 
            'command': ['uv', 'run', 'ruff', 'check', 'src/'],
            'required': True
        },
        {
            'name': 'Test Suite',
            'command': ['uv', 'run', 'pytest', 'tests/', '-x', '--tb=short'],
            'required': True
        },
        {
            'name': 'Performance Benchmarks',
            'command': ['uv', 'run', 'python', 'scripts/validate_faceting_performance.py'],
            'required': True
        },
        {
            'name': 'Memory Validation',
            'command': ['uv', 'run', 'python', 'scripts/validate_faceting_memory.py'],
            'required': False  # Optional - nice to have
        }
    ]
    
    results = {}
    
    for gate in gates:
        print(f"\n--- {gate['name']} ---")
        
        try:
            result = subprocess.run(
                gate['command'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            if success:
                print(f"✓ PASS")
            else:
                print(f"✗ FAIL")
                if result.stdout:
                    print(f"STDOUT:\n{result.stdout[:500]}...")
                if result.stderr:
                    print(f"STDERR:\n{result.stderr[:500]}...")
            
            results[gate['name']] = {
                'success': success,
                'required': gate['required'],
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            print(f"✗ TIMEOUT")
            results[gate['name']] = {
                'success': False,
                'required': gate['required'],
                'returncode': -1
            }
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results[gate['name']] = {
                'success': False, 
                'required': gate['required'],
                'returncode': -2
            }
    
    # Final assessment
    required_passed = sum(1 for r in results.values() if r['success'] and r['required'])
    required_total = sum(1 for r in results.values() if r['required'])
    optional_passed = sum(1 for r in results.values() if r['success'] and not r['required'])
    optional_total = sum(1 for r in results.values() if not r['required'])
    
    print(f"\n=== Quality Summary ===")
    print(f"Required gates: {required_passed}/{required_total} passed")
    print(f"Optional gates: {optional_passed}/{optional_total} passed")
    
    all_required_passed = required_passed == required_total
    
    if all_required_passed:
        print("✓ ALL REQUIRED QUALITY GATES PASSED")
        print("Faceting implementation is ready for production!")
    else:
        print("✗ SOME REQUIRED QUALITY GATES FAILED")
        print("Fix required issues before release:")
        for name, result in results.items():
            if result['required'] and not result['success']:
                print(f"  - {name} (code: {result['returncode']})")
    
    return all_required_passed

if __name__ == "__main__":
    success = run_quality_gates()
    exit(0 if success else 1)
```

6. **Final Documentation Validation**:
```python
# Validate documentation completeness
# File: scripts/validate_faceting_docs.py

from pathlib import Path
import re

def validate_documentation():
    """Validate that all documentation is complete and consistent."""
    
    print("=== Documentation Validation ===")
    
    # Required documentation files
    required_docs = [
        'docs/plans/faceted_plotting_detailed_design.md',
        'docs/plans/faceted_plotting_requirements.md', 
        'docs/plans/faceted_plotting_implementation_plan.md',
        'examples/faceted_plotting_guide.py',
        'docs/faceting_migration_guide.md'
    ]
    
    # Check file existence
    missing_docs = []
    for doc_path in required_docs:
        if not Path(doc_path).exists():
            missing_docs.append(doc_path)
    
    if missing_docs:
        print(f"✗ Missing documentation files: {missing_docs}")
        return False
    
    print("✓ All required documentation files exist")
    
    # Check for placeholder content
    placeholder_patterns = [
        r'\[TO BE FILLED IN\]',
        r'TODO:',
        r'FIXME:', 
        r'XXX:',
        r'PLACEHOLDER'
    ]
    
    issues_found = []
    
    for doc_path in required_docs:
        if Path(doc_path).suffix == '.md':  # Only check markdown files
            content = Path(doc_path).read_text()
            
            for pattern in placeholder_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues_found.append(f"{doc_path}: Found '{pattern}'")
    
    if issues_found:
        print("✗ Documentation issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
        return False
    
    print("✓ No placeholder content found in documentation")
    
    # Check example file can be executed
    example_file = Path('examples/faceted_plotting_guide.py')
    if example_file.exists():
        try:
            # Simple syntax check
            compile(example_file.read_text(), str(example_file), 'exec')
            print("✓ Example file syntax is valid")
        except SyntaxError as e:
            print(f"✗ Example file syntax error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = validate_documentation()
    exit(0 if success else 1)
```

7. **Final Test Execution Order**:
```bash
#!/bin/bash
# File: scripts/run_final_validation.sh

echo "=== Final Faceting Validation ==="
echo "Running all quality gates in order..."

# Step 1: Code quality
echo -e "\n1. Code Quality..."
python scripts/validate_faceting_quality.py
if [ $? -ne 0 ]; then
    echo "❌ Code quality issues found. Fix before proceeding."
    exit 1
fi

# Step 2: Documentation
echo -e "\n2. Documentation..."
python scripts/validate_faceting_docs.py  
if [ $? -ne 0 ]; then
    echo "❌ Documentation issues found. Fix before proceeding."
    exit 1
fi

# Step 3: Performance
echo -e "\n3. Performance..."
python scripts/validate_faceting_performance.py
if [ $? -ne 0 ]; then
    echo "❌ Performance issues found. Consider optimization."
    exit 1
fi

# Step 4: Memory (optional)
echo -e "\n4. Memory Usage..."
python scripts/validate_faceting_memory.py
if [ $? -ne 0 ]; then
    echo "⚠️ Memory usage higher than expected (non-blocking)"
fi

# Step 5: Complete integration test
echo -e "\n5. Integration Testing..."
pytest tests/test_complete_integration.py -v
if [ $? -ne 0 ]; then
    echo "❌ Integration test failures found."
    exit 1
fi

echo -e "\n✅ ALL VALIDATIONS PASSED"
echo "🚀 Faceting implementation is production-ready!"
echo ""
echo "Summary:"
echo "- Code quality: ✓ Passed"  
echo "- Documentation: ✓ Complete"
echo "- Performance: ✓ Acceptable"
echo "- Memory usage: ✓ Within bounds"
echo "- Integration: ✓ All features working"
echo ""
echo "Ready for release! 🎉"
```

## Success Criteria

Before marking Chunk 6 complete, verify ALL of these:

### Core Functionality 
- [ ] **Comprehensive error handling** - Clear, helpful error messages for all common mistakes
- [ ] **Edge case robustness** - Graceful handling of empty data, missing combinations, invalid configs
- [ ] **Performance optimized** - No significant overhead for large datasets or complex grids
- [ ] **API consistency** - All parameter naming and behavior consistent across faceting methods
- [ ] **Integration verified** - Works seamlessly with all existing dr_plotter features

### Quality and Documentation
- [ ] **All existing tests pass** - 94/94 faceting tests + all other dr_plotter tests continue working
- [ ] **Documentation comprehensive** - Clear docstrings, examples, and migration guides
- [ ] **Real-world scenarios validated** - Complex ML dashboard examples work flawlessly
- [ ] **Memory usage optimized** - No memory leaks or unbounded growth
- [ ] **Backward compatibility preserved** - All existing functionality works exactly as before

### Production Readiness
- [ ] **Error messages helpful** - Users can easily understand and fix configuration issues
- [ ] **Performance benchmarked** - Acceptable performance for reasonable dataset sizes
- [ ] **Code quality excellent** - Clean, maintainable, well-organized implementation
- [ ] **Integration seamless** - Faceting feels like natural part of dr_plotter API

## Implementation Notes

### Key Architecture Goals
- **Production-ready robustness**: Handle all edge cases gracefully with helpful error messages
- **Performance optimization**: Ensure faceting scales reasonably with data size and grid complexity
- **Developer experience**: Clear documentation and intuitive API behavior
- **Seamless integration**: Faceting should feel like a natural part of dr_plotter

### Code Quality Requirements  
- **All imports at top**: No mid-function imports anywhere
- **Complete type hints**: Every function fully typed
- **No comments**: Self-documenting code through clear names
- **Assertions for validation**: Use existing patterns, maintain consistency
- **Comprehensive error messages**: Help users understand and fix issues quickly

### Quality Assurance Strategy
- **Comprehensive testing**: Cover all edge cases and error conditions
- **Performance validation**: Ensure no significant regressions
- **Integration testing**: Verify seamless operation with existing features
- **Real-world validation**: Complex scenarios must work flawlessly

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

Add comprehensive "Chunk 6 Notes" section with:
- **Validation enhancements**: Error handling and edge case improvements implemented
- **Performance optimizations**: Speed and memory usage improvements
- **Documentation additions**: New docstrings, examples, and guides created
- **Integration validation**: How faceting integrates with existing dr_plotter features  
- **Quality assurance results**: Test coverage, performance benchmarks, real-world validation
- **Production readiness assessment**: Final evaluation of feature completeness and robustness
- **Future enhancement recommendations**: Potential improvements and extensions

## Next Steps After Completion

After successfully implementing Chunk 6:
1. **Execute comprehensive test suite** and verify no regressions
2. **Update all documentation** with final implementation insights
3. **Faceted plotting implementation COMPLETE** - all 6 chunks finished
4. **Production-ready feature** - native faceting support fully integrated into dr_plotter

This is the final chunk - the goal is to transform our working implementation into a polished, robust, production-ready feature that provides excellent developer experience and handles all edge cases gracefully.