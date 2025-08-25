# Agent Task: HeatmapPlotter Cell Text Component Implementation

## Task Overview
Implement proper component schema support for heatmap cell text display to eliminate the final non-legend `_get_style()` bypass call. This transforms `display_values` boolean control into a full-featured styling component with comprehensive customization options.

## Background Context
Currently, HeatmapPlotter uses `self._get_style("display_values", True)` to control whether cell values are displayed. This is actually a visual styling decision that should flow through StyleApplicator component resolution like all other visual settings. The task implements a `cell_text` component to handle this systematically.

## Implementation Requirements

### 1. Component Schema Enhancement
**File**: `src/dr_plotter/plotters/heatmap.py`

**Add cell_text component to schema**:
```python
component_schema: Dict[Phase, ComponentSchema] = {
    "plot": {
        "main": {
            "cmap", "vmin", "vmax", "aspect", "interpolation", "origin",
        },
        "text": {"color", "fontsize", "ha", "va"},
    },
    "axes": {
        "title": {"text", "fontsize", "color"},
        "xlabel": {"text", "fontsize", "color"},
        "ylabel": {"text", "fontsize", "color"},
        "grid": {"visible", "alpha", "color", "linestyle"},
        "colorbar": {"label", "fontsize", "color", "size", "pad"},
        "ticks": {
            "xticks", "yticks", "xticklabels", "yticklabels",
            "rotation", "alignment",
        },
        "cell_text": {"visible", "fontsize", "color", "ha", "va", "format"},  # NEW
    },
}
```

### 2. Post-Processor Registration
**File**: `src/dr_plotter/plotters/heatmap.py`

**Add to `__init__` method**:
```python
def __init__(self, data: pd.DataFrame, grouping_cfg: GroupingConfig, 
             theme: Optional[Theme] = None, figure_manager: Optional[Any] = None, 
             **kwargs: Any) -> None:
    super().__init__(data, grouping_cfg, theme, figure_manager, **kwargs)
    self.style_applicator.register_post_processor(
        self.plotter_name, "colorbar", self._style_colorbar
    )
    self.style_applicator.register_post_processor(
        self.plotter_name, "ticks", self._style_ticks
    )
    self.style_applicator.register_post_processor(
        self.plotter_name, "cell_text", self._style_cell_text  # NEW
    )
```

### 3. New Post-Processing Method Implementation
**File**: `src/dr_plotter/plotters/heatmap.py`

**Add new method**:
```python
def _style_cell_text(self, ax: Any, styles: Dict[str, Any]) -> None:
    """Style and render cell text values on heatmap."""
    # Check if cell text should be displayed
    if not styles.get("visible", True):
        return
    
    data = self.plot_data
    
    # Get styling attributes with sensible defaults
    fontsize = styles.get("fontsize", 8)
    color = styles.get("color", "white") 
    ha = styles.get("ha", "center")
    va = styles.get("va", "center")
    format_str = styles.get("format", ".2f")
    
    # Render text for each cell
    for i in range(len(data.index)):
        for j in range(len(data.columns)):
            cell_value = data.iloc[i, j]
            # Handle different format patterns
            if format_str.startswith(".") and format_str.endswith("f"):
                text = f"{cell_value:{format_str}}"
            elif format_str == "int":
                text = str(int(cell_value))
            else:
                text = str(cell_value)
                
            ax.text(
                j, i, text,
                ha=ha, va=va,
                color=color,
                fontsize=fontsize,
            )
```

### 4. Update _draw Method
**File**: `src/dr_plotter/plotters/heatmap.py`

**Remove direct display_values logic and add cell_text to post-processing**:
```python
def _draw(self, ax: Any, data: pd.DataFrame, **kwargs: Any) -> None:
    # Set default cmap if not provided
    if "cmap" not in kwargs:
        kwargs["cmap"] = self.style_applicator.get_style_with_fallback("cmap")

    im = ax.imshow(data, **self._filtered_plot_kwargs)

    # REMOVE this entire section:
    # if self._get_style("display_values", True):
    #     text_styles = self.style_applicator.get_single_component_styles("heatmap", "text")
    #     for i in range(len(data.index)):
    #         for j in range(len(data.columns)):
    #             ax.text(j, i, f"{data.iloc[i, j]:.2f}", ...)

    # Store artists for post-processing (including NEW cell_text)
    artists = {
        "colorbar": {
            "plot_object": im,
            "ax": ax,
            "fig": ax.get_figure(),
        },
        "ticks": ax,
        "cell_text": ax,  # NEW - enables post-processing for cell text
    }
    self.style_applicator.apply_post_processing(self.plotter_name, artists)

    # Apply base post-processing for title, xlabel, ylabel, grid
    self._apply_styling(ax)
```

## Enhanced User Experience

### **New Styling Capabilities**
With this implementation, users gain comprehensive cell text control:

```python
# Boolean control (backward compatible)
heatmap(data, x='col1', y='col2', values='val', display_values=False)

# Enhanced styling options  
heatmap(data, x='col1', y='col2', values='val',
        cell_text_visible=True,          # Same as display_values=True
        cell_text_color='red',           # Custom text color
        cell_text_fontsize=12,           # Custom font size
        cell_text_format='.1f',          # Custom number format
        cell_text_ha='left')             # Custom horizontal alignment

# Theme-based configuration
CUSTOM_THEME = Theme(
    cell_text_color='blue',
    cell_text_fontsize=10,
    cell_text_format='int'
)
```

### **Backward Compatibility Mapping**
**Critical**: Ensure `display_values` parameter maps to `cell_text_visible`:

```python
# In _extract_component_kwargs or similar preprocessing
if "display_values" in self.kwargs:
    # Map legacy parameter to new component attribute
    component_kwargs["cell_text_visible"] = self.kwargs["display_values"]
```

## Validation Requirements

### 1. Functional Preservation Testing
**Verify identical behavior for existing usage patterns**:

```python
# Test backward compatibility
test_data = pd.DataFrame({
    'x': [1, 2, 3], 
    'y': [1, 2, 3],
    'values': [10, 20, 30]
})

# These should work identically to before
heatmap(test_data, 'x', 'y', 'values')  # Default: show values
heatmap(test_data, 'x', 'y', 'values', display_values=True)   # Show values
heatmap(test_data, 'x', 'y', 'values', display_values=False)  # Hide values
```

### 2. Enhanced Styling Validation
**Test new component styling capabilities**:

```python
# Test enhanced styling options
heatmap(test_data, 'x', 'y', 'values', 
        cell_text_color='red',
        cell_text_fontsize=14,
        cell_text_format='.1f')

# Test theme integration
custom_theme = Theme(cell_text_color='blue', cell_text_fontsize=8)
heatmap(test_data, 'x', 'y', 'values', theme=custom_theme)
```

### 3. Component Resolution Testing
**Verify proper component flow**:

```python
# Debug component resolution
plotter = HeatmapPlotter(test_data, GroupingConfig(), 
                        cell_text_visible=True, cell_text_color='green')

# Check component styles contain cell_text settings
axes_styles = plotter.style_applicator.get_component_styles("heatmap", phase="axes")
cell_text_styles = axes_styles.get("cell_text", {})
print("Cell text styles:", cell_text_styles)
# Should contain: {"visible": True, "color": "green", ...}
```

## Success Criteria

### **Bypass Elimination**
- ✅ Remove `self._get_style("display_values", True)` call from heatmap.py:92
- ✅ **Remaining _get_style() calls**: 1 (only legend behavioral control)  
- ✅ **Elimination rate**: **95.8% (23/24 calls)**

### **Functional Enhancement**
- ✅ All existing `display_values` usage continues working identically
- ✅ New styling options work correctly: color, fontsize, format, alignment
- ✅ Theme integration works for cell text styling
- ✅ Component resolution flows properly through StyleApplicator

### **Code Quality**
- ✅ Clean component schema integration
- ✅ Consistent post-processing patterns with other components
- ✅ Proper separation of concerns (styling through components)
- ✅ No hacks or workarounds

### **User Experience** 
- ✅ Backward compatibility: existing code continues working
- ✅ Enhanced capability: fine-grained cell text control
- ✅ Consistent API: follows same patterns as other styling options

## Error Handling Requirements

### **Backward Compatibility Edge Cases**
```python
# Handle potential conflicts
if "display_values" in kwargs and "cell_text_visible" in kwargs:
    # Priority: explicit component attribute over legacy parameter
    kwargs.pop("display_values")
    
# Handle invalid format strings gracefully
try:
    text = f"{cell_value:{format_str}}"
except (ValueError, TypeError):
    text = str(cell_value)  # Fallback to string conversion
```

### **Component Schema Validation**
- Ensure component attributes have sensible defaults
- Handle missing or invalid attribute values gracefully
- Provide clear error messages for invalid format strings

## Deliverables

### 1. **Implementation Report**
Document all changes made:
- Component schema additions
- Post-processing method implementation  
- _draw method modifications
- Any backward compatibility handling

### 2. **Validation Results**
Comprehensive testing results:
- Functional preservation confirmation
- Enhanced styling capability validation
- Component resolution verification

### 3. **Final Bypass Inventory**
Updated count of remaining `_get_style()` calls:
- Legend call (behavioral control boundary)
- Verification of 95.8% elimination achievement

## Context Integration
This task completes the systematic migration of visual styling patterns to StyleApplicator component resolution. Success enables **Phase 2**: semantic replacement of the final legend behavioral control logic for potential 100% `_get_style()` method elimination.

The implementation transforms heatmap cell text display from boolean toggle to full-featured styling component, demonstrating the value of systematic architectural enhancement over simple bypass elimination.