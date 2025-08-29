# Agent Task: Grouped Drawing Capability Implementation and BumpPlotter Cleanup

## Task Overview
Implement the `supports_grouped` flag system to establish explicit grouped drawing capability declarations and clean up BumpPlotter's inappropriate grouped pathway usage, converting it to a proper single-purpose visualization.

## Implementation Requirements

### 1. Add Grouped Capability Flag System
**File**: `src/dr_plotter/plotters/base.py`

**Changes Required**:
```python
# Add class attribute to BasePlotter (should already have supports_legend)
class BasePlotter:
    supports_legend: bool = True     # Already implemented
    supports_grouped: bool = True    # NEW: Default plotters support grouped drawing
    
    # Enhanced _draw_grouped() method to handle single-purpose plotters
    def _draw_grouped(
        self,
        ax: Any,
        data: pd.DataFrame,
        group_position: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        if not self.supports_grouped:
            # Single-purpose plotters ignore group_position and process all data
            self._draw(ax, self.plot_data, **kwargs)
        else:
            # Default behavior for coordinate-sharing plotters (Line, Scatter)
            self._draw(ax, data, **kwargs)
```

**Validation**: Preserve existing behavior - LinePlotter and ScatterPlotter should continue working identically.

### 2. Declare Single-Purpose Plotters
**Files**: `src/dr_plotter/plotters/contour.py`, `src/dr_plotter/plotters/heatmap.py`, `src/dr_plotter/plotters/histogram.py`

**Changes Required**:
```python
# ContourPlotter class
class ContourPlotter(BasePlotter):
    supports_legend: bool = False    # Already implemented
    supports_grouped: bool = False   # NEW: Single density surface visualization
    # ... existing class content unchanged ...

# HeatmapPlotter class  
class HeatmapPlotter(BasePlotter):
    supports_legend: bool = False    # Already implemented  
    supports_grouped: bool = False   # NEW: Single matrix visualization
    # ... existing class content unchanged ...

# HistogramPlotter class
class HistogramPlotter(BasePlotter):
    supports_grouped: bool = False   # NEW: Single distribution visualization
    # ... existing class content unchanged ...
```

**Critical**: No other changes to these classes - they should continue current behavior.

### 3. BumpPlotter Architectural Cleanup
**File**: `src/dr_plotter/plotters/bump.py`

**Major Changes Required**:

#### **3a. Add Capability Declaration**
```python
class BumpPlotter(BasePlotter):
    # ... existing attributes ...
    supports_grouped: bool = False   # NEW: Single-purpose trajectory visualization
```

#### **3b. Remove Forced Grouping Setup**
```python
def _initialize_subplot_specific_params(self) -> None:
    self.time_col = self.kwargs.get("time_col")
    self.value_col = self.kwargs.get("value_col")
    self.category_col = self.kwargs.get("category_col")
    # REMOVE THIS LINE: self.grouping_params.hue = self.category_col
```

#### **3c. Enhanced Data Preparation**
```python
def _plot_specific_data_prep(self) -> None:
    # 1. Calculate rankings (existing logic)
    self.plot_data["rank"] = self.plot_data.groupby(self.time_col)[
        self.value_col
    ].rank(method="first", ascending=False)
    self.value_col = "rank"
    
    # 2. Prepare category trajectories with styles
    categories = self.plot_data[self.category_col].unique()
    self.trajectory_data = []
    
    for i, category in enumerate(categories):
        cat_data = self.plot_data[self.plot_data[self.category_col] == category]
        cat_data = cat_data.sort_values(by=self.time_col).copy()
        
        # Assign consistent styling per category
        style = self._get_category_style(category, i, len(categories))
        cat_data['_bump_color'] = style['color']
        cat_data['_bump_linestyle'] = style.get('linestyle', '-')
        cat_data['_bump_label'] = str(category)
        
        self.trajectory_data.append(cat_data)

def _get_category_style(self, category: Any, index: int, total_categories: int) -> Dict[str, Any]:
    # Create consistent category styling using theme colors
    base_colors = self.theme.get('base_colors', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    color = base_colors[index % len(base_colors)]
    return {
        'color': color,
        'linestyle': '-'
    }
```

#### **3d. Simplified Unified Rendering**
```python
def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
    # Process all trajectories in single unified method
    for traj_data in self.trajectory_data:
        if not traj_data.empty:
            lines = ax.plot(
                traj_data[self.time_col], 
                traj_data[self.value_col],
                color=traj_data['_bump_color'].iloc[0],
                linestyle=traj_data['_bump_linestyle'].iloc[0],
                **self._filtered_plot_kwargs
            )
            
            # Add category labels at end of trajectories
            last_point = traj_data.iloc[-1]
            category_name = traj_data['_bump_label'].iloc[0]
            text = ax.text(
                last_point[self.time_col],
                last_point[self.value_col],
                f" {category_name}",
                va="center",
                color=self._get_style("text_color", "black"),
                fontweight=self._get_style("fontweight", "bold"),
            )
            text.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground="white"),
                path_effects.Normal(),
            ])
            
            # Register legend entries
            self._register_legend_entry_if_valid(lines[0], category_name)
    
    # Configure bump plot specific axes (only set once)
    if not hasattr(ax, "_bump_configured"):
        ax.invert_yaxis()
        max_rank = int(self.plot_data["rank"].max())
        ax.set_yticks(range(1, max_rank + 1))
        ax.margins(x=0.15)
        ax.set_ylabel(self._get_style("ylabel", "Rank"))
        ax._bump_configured = True
```

#### **3e. Remove Obsolete Methods**
```python
# REMOVE ENTIRELY: _draw_simple method (no longer needed)
# REMOVE ENTIRELY: _apply_post_processing method (handled by unified _draw)
```

## Implementation Steps

### Step 1: Add Grouped Capability Flag System
1. Add `supports_grouped: bool = True` to BasePlotter class
2. Enhance `_draw_grouped()` method with single-purpose plotter handling
3. Verify no changes to existing coordinate-sharing plotter behavior

### Step 2: Declare Single-Purpose Plotters  
1. Add `supports_grouped: bool = False` to ContourPlotter class
2. Add `supports_grouped: bool = False` to HeatmapPlotter class
3. Add `supports_grouped: bool = False` to HistogramPlotter class
4. Verify no behavioral changes for these plotters

### Step 3: BumpPlotter Architectural Cleanup
1. **Add capability declaration**: `supports_grouped: bool = False`
2. **Remove forced grouping**: Delete `self.grouping_params.hue = self.category_col` line
3. **Enhance data preparation**: Implement complete trajectory preparation with styling
4. **Implement unified rendering**: Replace complex _draw() with trajectory-based approach
5. **Add category styling helper**: Implement `_get_category_style()` method
6. **Remove obsolete methods**: Delete `_draw_simple()` and `_apply_post_processing()`

### Step 4: Comprehensive Testing
1. **Functionality test**: All single-purpose plotters work identically  
2. **Coordinate-sharing test**: LinePlotter and ScatterPlotter continue working
3. **BumpPlotter validation**: Identical visual output with improved performance
4. **Import test**: All plotter files import successfully

## Special Requirements for BumpPlotter

### Preserve All Current Functionality
**Critical Requirements**:
- Identical visual output (trajectories, colors, labels, axes configuration)
- All legend functionality preserved
- Category text labels at trajectory endpoints
- Inverted y-axis and proper tick configuration
- Path effects (white stroke) on category labels

### Performance Improvement Expected
**Benefits from Cleanup**:
- Eliminate duplicate grouping operations
- Remove redundant style processing  
- Cleaner data preparation flow
- Single unified rendering pass

### Import Requirements
**Add Required Import**:
```python
# BumpPlotter will need path_effects for text styling
import matplotlib.patheffects as path_effects  # Should already exist
```

## Validation Requirements

### Must Preserve
- **All existing functionality**: Zero behavioral changes for all plotters except BumpPlotter performance improvement
- **BumpPlotter output**: Identical visual appearance with cleaner architecture
- **Legend integration**: All plotters continue proper legend behavior
- **Coordinate-sharing plotters**: LinePlotter and ScatterPlotter work identically through base fallback

### Must Verify
- **Flag system functionality**: `supports_grouped` flags work correctly
- **Single-purpose plotters**: ContourPlotter, HeatmapPlotter, HistogramPlotter continue current behavior
- **BumpPlotter cleanup**: No duplicate processing, improved performance, identical output
- **Base class enhancement**: `_draw_grouped()` properly handles single-purpose plotters

## Success Criteria
- ✅ `supports_grouped: bool` flag system implemented consistently
- ✅ ContourPlotter, HeatmapPlotter, HistogramPlotter explicitly marked as single-purpose
- ✅ BumpPlotter converted to proper single-purpose architecture with performance improvement
- ✅ Enhanced base `_draw_grouped()` handles single-purpose plotters appropriately
- ✅ Zero breaking changes for all existing functionality
- ✅ LinePlotter and ScatterPlotter continue working through coordinate-sharing base fallback
- ✅ Comprehensive testing validates all behavioral preservation

## Context
This implements Decision 2 resolution for Phase 2 Task Group 1, completing the explicit capability declaration pattern established in Decision 1 and cleaning up architectural inconsistencies identified in the BumpPlotter investigation.

## Expected Outcome
- Clear architectural separation between positioned-layout vs coordinate-sharing vs single-purpose plotters
- BumpPlotter performance improvement through elimination of duplicate processing
- Foundation established for remaining Phase 2 decisions (StyleApplicator enforcement, API type coverage)
- Zero user-visible changes while improving internal architecture consistency and performance