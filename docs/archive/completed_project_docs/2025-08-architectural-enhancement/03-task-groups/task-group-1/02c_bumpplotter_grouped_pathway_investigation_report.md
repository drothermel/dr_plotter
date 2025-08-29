# BumpPlotter Grouped Pathway Investigation

## Current Architecture Analysis

### Grouped Pathway Dependencies
BumpPlotter currently relies on grouped rendering pathways for:
- **Style Coordination**: `style_engine.get_styles_for_group()` and `_build_group_plot_kwargs()` for consistent category colors/styles
- **Label Generation**: `_build_group_label()` for legend labels formatted as "category=A", "category=B"
- **Group Iteration**: Automatic iteration through categories via `_render_with_grouped_method()`

### Data Preparation Completeness  
Current `_plot_specific_data_prep()` only handles:
- **Ranking Calculation**: `self.plot_data.groupby(self.time_col)[self.value_col].rank()`
- **Column Renaming**: `self.value_col = "rank"`

**Missing**: Category processing, style assignment, trajectory organization

### Category Processing Location
Categories are processed in **two places** (duplicate logic):
1. **BasePlotter._render_with_grouped_method()**: Groups by category_col, calls _draw_grouped() per group
2. **BumpPlotter._draw()**: Re-groups by same category_col, duplicates styling logic

## Problematic Dependencies Identified

### Dependency 1: Forced Hue Grouping
- **Location**: `bump.py:55` - `self.grouping_params.hue = self.category_col`
- **Current Behavior**: Forces `_has_groups = True`, triggers grouped rendering pathway
- **Problem**: BumpPlotter is conceptually a single-purpose visualization showing all trajectories together, not a grouped coordinate-sharing plot
- **Impact**: Unnecessary architectural complexity, duplicate processing

### Dependency 2: Duplicate Grouping Logic
- **Location**: `bump.py:65-82` - `grouped = self.plot_data.groupby(group_cols)`
- **Current Behavior**: Re-groups data that `_render_with_grouped_method()` already grouped
- **Problem**: BumpPlotter._draw() ignores the already-grouped data it receives and re-processes everything
- **Impact**: Inefficient processing, architectural inconsistency

### Dependency 3: Redundant Style Processing
- **Location**: `bump.py:75-80` - `styles = self.style_engine.get_styles_for_group()`
- **Current Behavior**: Re-calculates styles that base class already prepared
- **Problem**: Duplicates style coordination logic from `_render_with_grouped_method()`
- **Impact**: Code duplication, potential style inconsistencies

## Cleanup Strategy Recommendation

### Approach: Single-Purpose Visualization Architecture
BumpPlotter should be converted to a true single-purpose visualization that handles all trajectories in a unified manner.

### Data Preparation Changes
Enhance `_plot_specific_data_prep()` to handle complete data preparation:

```python
def _plot_specific_data_prep(self) -> None:
    # 1. Calculate rankings (existing logic)
    self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
        self.value_col
    ].rank(method="first", ascending=False)
    self.value_col = "rank"
    
    # 2. Prepare category trajectories with styles
    categories = self.plot_data[self.category_col].unique()
    trajectory_data = []
    
    for i, category in enumerate(categories):
        cat_data = self.plot_data[self.plot_data[self.category_col] == category]
        cat_data = cat_data.sort_values(by=self.time_col)
        
        # Assign consistent styling per category
        style = self._get_category_style(category, i, len(categories))
        cat_data = cat_data.copy()
        cat_data['_bump_color'] = style['color']
        cat_data['_bump_linestyle'] = style.get('linestyle', '-')
        cat_data['_bump_label'] = category
        
        trajectory_data.append(cat_data)
    
    # Store prepared trajectory data
    self.trajectory_data = trajectory_data
```

### Category Handling Changes
Remove forced grouping and move to self-contained category processing:

```python
def _initialize_subplot_specific_params(self) -> None:
    self.time_col = self.kwargs.get("time_col")
    self.value_col = self.kwargs.get("value_col")
    self.category_col = self.kwargs.get("category_col")
    # REMOVE: self.grouping_params.hue = self.category_col
```

### Rendering Simplification  
Replace complex `_draw()` with unified trajectory rendering:

```python
def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
    # Process all trajectories in single method
    for traj_data in self.trajectory_data:
        lines = ax.plot(
            traj_data[self.time_col], 
            traj_data[self.value_col],
            color=traj_data['_bump_color'].iloc[0],
            linestyle=traj_data['_bump_linestyle'].iloc[0],
            label=traj_data['_bump_label'].iloc[0],
            **self._filtered_plot_kwargs
        )
        
        # Add category labels
        if not traj_data.empty:
            last_point = traj_data.iloc[-1]
            ax.text(
                last_point[self.time_col],
                last_point[self.value_col], 
                f" {traj_data['_bump_label'].iloc[0]}",
                va="center",
                color=self._get_style("text_color", "black"),
                fontweight=self._get_style("fontweight", "bold")
            )
        
        # Register legends for each trajectory
        self._register_legend_entry_if_valid(lines[0], traj_data['_bump_label'].iloc[0])
    
    # Configure bump-specific axes
    ax.invert_yaxis()
    max_rank = int(self.plot_data["rank"].max())
    ax.set_yticks(range(1, max_rank + 1))
    ax.margins(x=0.15)
    ax.set_ylabel(self._get_style("ylabel", "Rank"))
```

### Implementation Steps

1. **Add supports_grouped flag**: `supports_grouped: bool = False` to BumpPlotter class
2. **Remove forced hue grouping**: Delete `self.grouping_params.hue = self.category_col` from `_initialize_subplot_specific_params()`
3. **Enhance data preparation**: Move all category processing, styling, and trajectory organization to `_plot_specific_data_prep()`
4. **Simplify rendering**: Replace current `_draw()` with unified trajectory rendering that processes `self.trajectory_data`
5. **Add category styling helper**: Implement `_get_category_style()` method for consistent category colors/styles
6. **Remove _draw_simple**: No longer needed with unified approach

## Risk Assessment

### Behavioral Changes
- **Low Risk**: Output should be identical with better performance
- **Style Consistency**: May improve style consistency by eliminating duplicate style processing
- **Legend Behavior**: Should preserve all current legend functionality

### Breaking Changes  
- **Zero Breaking Changes**: External API remains identical
- **Internal Architecture**: Cleaner separation between data prep and rendering
- **Performance**: Should improve by eliminating duplicate grouping/styling

### Testing Requirements
- **Visual Output**: Verify identical bump plot appearance
- **Legend Functionality**: Ensure all category legends appear correctly  
- **Style Coordination**: Confirm consistent category colors/styles
- **Edge Cases**: Test with varying numbers of categories and time points

## Integration with supports_grouped Flag

### Flag Value
`BumpPlotter.supports_grouped = False`

### Justification
BumpPlotter represents a **single-purpose visualization** showing ranking trajectories over time. While it displays multiple categories, these are best thought of as multiple trajectories within a single comprehensive visualization, not as separate grouped plots that need coordinate sharing.

The trajectories are:
- **Inherently Related**: All show rankings in same space (rank vs time)
- **Visually Unified**: Single plot with shared axes and coordinate system
- **Conceptually Single**: One "story" about ranking changes, not separate category stories

### Enhanced _draw_grouped()
Base class should handle no-grouped plotters by calling `_draw()` directly:

```python
def _draw_grouped(self, ax: Any, data: pd.DataFrame, group_position: Dict[str, Any], **kwargs: Any) -> None:
    if not getattr(self.__class__, 'supports_grouped', True):
        # Single-purpose plotters ignore group_position and process all data
        self._draw(ax, self.plot_data, **kwargs)
    else:
        # Default behavior for grouped plotters
        self._draw(ax, data, **kwargs)
```

This ensures that single-purpose plotters like BumpPlotter can work within any rendering pathway while maintaining their unified approach to data visualization.