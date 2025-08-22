# Plan: Automatic Label Handling for Shared Axes

**Objective:** Implement intelligent axis label handling in `dr_plotter` for figures with shared axes (`sharex=True` or `sharey=True`). When axes are shared, labels should only be drawn on the outer edges of the figure grid to avoid redundancy.

**Strategy:** The `FigureManager` holds the layout information (`sharex`, `sharey`, rows, cols). It will determine if a subplot at a given `(row, col)` position should display its labels and will pass this decision down to the `BasePlotter` instance for rendering.

---

## Step 1: Update `FigureManager` to Store Layout Settings

**File:** `dr_plotter/src/dr_plotter/figure.py`

In `FigureManager.__init__`, we need to capture and store the `rows`, `cols`, and the `sharex`/`sharey` arguments passed in `**fig_kwargs`.

```python
# In FigureManager.__init__
class FigureManager:
    def __init__(
        self,
        rows=1,
        cols=1,
        # ... other args ...
        **fig_kwargs,
    ):
        # ... existing code ...
        if external_ax is not None:
            # ...
            self.external_mode = True
            # In external mode, we can't know the grid, so assume defaults
            self.rows = 1
            self.cols = 1
            self.sharex = False
            self.sharey = False
        else:
            # ...
            self.fig, self.axes = plt.subplots(
                rows, cols, constrained_layout=False, **fig_kwargs
            )
            self.external_mode = False
            # Store layout and sharing settings
            self.rows = rows
            self.cols = cols
            self.sharex = fig_kwargs.get('sharex', False)
            self.sharey = fig_kwargs.get('sharey', False)

        # Cross-subplot style coordination
        self._shared_hue_styles = {}
        self._shared_style_cycles = None
```

## Step 2: Pass Label Visibility Context to Plotters

In `FigureManager._add_plot`, calculate whether labels should be shown for the target subplot and pass these boolean flags to the plotter instance.

**File:** `dr_plotter/src/dr_plotter/figure.py`

```python
# In FigureManager._add_plot
def _add_plot(self, plotter_class, plotter_args, row, col, **kwargs):
    # ... existing code to get ax ...

    # Determine if labels should be visible based on sharing settings
    # X-labels are typically only on the bottom-most row of subplots
    show_xlabel = (not self.sharex) or (row == self.rows - 1)
    # Y-labels are typically only on the left-most column of subplots
    show_ylabel = (not self.sharey) or (col == 0)

    # Pass visibility flags to the plotter
    kwargs['_show_xlabel'] = show_xlabel
    kwargs['_show_ylabel'] = show_ylabel

    # Add shared style state for cross-subplot coordination
    kwargs["_figure_manager"] = self
    kwargs["_shared_hue_styles"] = self._shared_hue_styles

    plotter = plotter_class(*plotter_args, **kwargs)
    plotter.render(ax)
```

## Step 3: Update `BasePlotter` to Receive Visibility Flags

The `BasePlotter` must be updated to accept the new visibility flags from `kwargs` during initialization.

**File:** `dr_plotter/src/dr_plotter/plotters/base.py`

```python
# In BasePlotter.__init__
class BasePlotter:
    def __init__(self, data, **kwargs):
        # ... existing code ...
        self.alpha_by = kwargs.get("alpha_by")

        # Get label visibility flags from FigureManager, default to True
        self._show_xlabel = kwargs.get("_show_xlabel", True)
        self._show_ylabel = kwargs.get("_show_ylabel", True)

        # Set theme (can be overridden via kwargs)
        self.theme = kwargs.get(
            "theme", getattr(self.__class__, "default_theme", BASE_THEME)
        )
        # ... rest of __init__ ...
```

## Step 4: Conditionally Set Labels During Styling

Finally, use the stored flags in `BasePlotter._apply_styling` to control whether `ax.set_xlabel()` and `ax.set_ylabel()` are called.

**File:** `dr_plotter/src/dr_plotter/plotters/base.py`

```python
# In BasePlotter._apply_styling
def _apply_styling(self, ax, legend):
    """Apply high-level styling options to the axes object."""
    ax.set_title(
        self._get_style("title"), fontsize=self.theme.get("title_fontsize")
    )

    # Conditionally set axis labels based on visibility flags
    if self._show_xlabel:
        xlabel = self._get_style(
            "xlabel",
            self.x.replace("_", " ").title() if hasattr(self, "x") and self.x else None,
        )
        ax.set_xlabel(xlabel, fontsize=self.theme.get("label_fontsize"))

    if self._show_ylabel:
        ylabel = self._get_style(
            "ylabel",
            self.y.replace("_", " ").title() if hasattr(self, "y") and self.y else None,
        )
        ax.set_ylabel(ylabel, fontsize=self.theme.get("label_fontsize"))

    if self._get_style("grid", True):
        ax.grid(True, alpha=self.theme.get("grid_alpha"))
    # ... rest of the function ...
```
