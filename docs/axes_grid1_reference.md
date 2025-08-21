# matplotlib axes_grid1 Toolkit Reference

## Overview

The `mpl_toolkits.axes_grid1` toolkit is a matplotlib extension that provides advanced layout management tools for complex subplot arrangements and precise control over colorbar placement. It's particularly useful for:

- Creating grids of images with consistent sizing
- Adding colorbars without affecting subplot proportions  
- Managing multiple subplots with shared colorbars
- Precise control over spacing and alignment

## Core Components

### 1. make_axes_locatable()

Creates a divider object that can split an axes into multiple parts.

**Basic Usage:**
```python
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create main axes
fig, ax = plt.subplots()
im = ax.imshow(data)

# Create divider and add colorbar axis
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
plt.colorbar(im, cax=cax)
```

**append_axes() Parameters:**
- `position`: "top", "right", "bottom", "left"
- `size`: Width/height as percentage string ("5%") or absolute value
- `pad`: Padding between axes (default: 0.1 inches)
- `share_x/share_y`: Whether to share axes (boolean)

### 2. ImageGrid

Creates a grid of axes optimized for displaying images with consistent aspect ratios.

**Basic Usage:**
```python
from mpl_toolkits.axes_grid1 import ImageGrid

fig = plt.figure(figsize=(10, 8))
grid = ImageGrid(
    fig, 111,                    # subplot spec
    nrows_ncols=(2, 3),         # 2x3 grid
    axes_pad=0.1,               # padding between axes
    cbar_mode="single",         # colorbar mode
    cbar_location="right",      # colorbar position
    cbar_size="5%",             # colorbar size
    cbar_pad=0.1                # colorbar padding
)

# Use like a list of axes
for i, ax in enumerate(grid):
    im = ax.imshow(data[i])
    
# Add colorbar (if cbar_mode="single")
grid.cbar_axes[0].colorbar(im)
```

**Key Parameters:**

| Parameter | Options | Description |
|-----------|---------|-------------|
| `nrows_ncols` | `(rows, cols)` | Grid dimensions |
| `axes_pad` | float or `(h_pad, v_pad)` | Padding between axes |
| `cbar_mode` | `"single"`, `"each"`, `"edge"`, `None` | Colorbar strategy |
| `cbar_location` | `"top"`, `"bottom"`, `"left"`, `"right"` | Colorbar position |
| `cbar_size` | `"5%"` or float | Colorbar size |
| `cbar_pad` | float | Space between plot and colorbar |
| `share_all` | boolean | Share x/y axes across all subplots |
| `label_mode` | `"L"`, `"1"`, `"all"` | Which axes show labels |

**Colorbar Modes:**
- `"single"`: One colorbar for entire grid
- `"each"`: Individual colorbar for each subplot  
- `"edge"`: Colorbars only on edge subplots
- `None`: No colorbars

### 3. AxesGrid

More flexible version of ImageGrid with additional customization options.

```python
from mpl_toolkits.axes_grid1 import AxesGrid

grid = AxesGrid(
    fig, 111,
    nrows_ncols=(2, 2),
    axes_pad=0.02,
    share_all=True,
    aspect=False,               # Allow non-square aspects
    cbar_mode="edge",
    cbar_location="bottom",
    cbar_pad=0.25,
    cbar_size="15%"
)
```

## Advanced Features

### Shared Axes Control

Control which axes share x/y coordinates:

```python
# Share all axes
grid = ImageGrid(fig, 111, nrows_ncols=(2,2), share_all=True)

# Share by row/column only  
grid = ImageGrid(fig, 111, nrows_ncols=(2,2), share_x=True, share_y=False)
```

### Label Management

Control tick labels display:

```python
# Label modes:
# "L" - Only leftmost/bottommost show labels
# "1" - Only first subplot shows labels  
# "all" - All subplots show labels
grid = ImageGrid(fig, 111, nrows_ncols=(2,2), label_mode="L")
```

### Aspect Ratio Control

```python
# Fixed aspect ratio (default for ImageGrid)
grid = ImageGrid(fig, 111, nrows_ncols=(2,2), aspect=True)

# Variable aspect ratio  
grid = AxesGrid(fig, 111, nrows_ncols=(2,2), aspect=False)
```

## Common Patterns

### Single Heatmap with Colorbar
```python
from mpl_toolkits.axes_grid1 import make_axes_locatable

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(data, cmap='viridis')

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
cbar = plt.colorbar(im, cax=cax)
cbar.set_label("Values")
```

### Multiple Heatmaps with Shared Colorbar
```python
from mpl_toolkits.axes_grid1 import ImageGrid

fig = plt.figure(figsize=(12, 4))
grid = ImageGrid(
    fig, 111,
    nrows_ncols=(1, 3),
    axes_pad=0.05,
    cbar_mode="single",
    cbar_location="right",
    cbar_size="5%"
)

# Ensure consistent color scaling
vmin, vmax = np.min(all_data), np.max(all_data)

for ax, data in zip(grid, data_list):
    im = ax.imshow(data, vmin=vmin, vmax=vmax, cmap='viridis')

# Add shared colorbar
grid.cbar_axes[0].colorbar(im)
grid.cbar_axes[0].set_ylabel("Shared Values")
```

### Individual Colorbars
```python
grid = ImageGrid(
    fig, 111,
    nrows_ncols=(2, 2), 
    axes_pad=0.1,
    cbar_mode="each",
    cbar_size="7%",
    cbar_pad="2%"
)

for ax, cax, data in zip(grid, grid.cbar_axes, data_list):
    im = ax.imshow(data)
    cax.colorbar(im)
```

## Integration with dr_plotter

### Design Principles

1. **Transparent to Users**: Users shouldn't need to know about axes_grid1 unless they want advanced features
2. **Default Enhancement**: Use for single heatmaps to fix layout issues
3. **Progressive Complexity**: Expose advanced features through optional parameters

### Proposed API Extensions

```python
# Simple case - uses make_axes_locatable internally
drp.heatmap(data, x="col", y="row", values="temp")

# Advanced case - exposes ImageGrid functionality
with drp.FigureManager(layout="grid") as fm:
    fm.heatmap_grid(
        data_list, 
        nrows_ncols=(2, 2),
        cbar_mode="single",
        cbar_location="right"
    )
```

## Best Practices

### 1. Size Specifications
- Use percentage strings (`"5%"`) for responsive sizing
- Common colorbar sizes: 5-7% for single plots, 3-5% for grids
- Padding typically 0.1 inches or `"2%"`

### 2. Color Scaling
- Always use consistent `vmin`/`vmax` for shared colorbars
- Calculate global min/max across all data before plotting

### 3. Performance
- ImageGrid is more efficient for many subplots than individual `make_axes_locatable` calls
- Pre-calculate grid dimensions rather than dynamic sizing

### 4. Compatibility
- Works with all standard matplotlib colormaps and parameters
- Compatible with existing matplotlib styling
- Can be mixed with standard subplots in same figure

## Troubleshooting

### Common Issues

1. **Colorbar too wide/narrow**: Adjust `cbar_size` parameter
2. **Too much/little spacing**: Modify `axes_pad` and `cbar_pad`  
3. **Aspect ratio problems**: Use `aspect=False` in AxesGrid
4. **Label overlap**: Use appropriate `label_mode` setting
5. **Inconsistent colors**: Ensure consistent `vmin`/`vmax` across subplots

### Import Errors
```python
# Correct import
from mpl_toolkits.axes_grid1 import make_axes_locatable, ImageGrid

# Common mistake - this doesn't exist
# from matplotlib.axes_grid1 import ...  # Wrong!
```

## References

- [Official matplotlib axes_grid1 documentation](https://matplotlib.org/stable/users/explain/toolkits/axes_grid.html)
- [Colorbar with AxesDivider examples](https://matplotlib.org/stable/gallery/axes_grid1/demo_colorbar_with_axes_divider.html)
- [ImageGrid gallery examples](https://matplotlib.org/stable/gallery/axes_grid1/demo_axes_grid.html)