# Legend Verification & Visibility Context

## Current Status & What We've Been Working On

We have successfully implemented a comprehensive legend visibility verification system for dr_plotter and identified critical bugs in the legend management system.

### Key Accomplishments

1. **Created `src/dr_plotter/verification.py`** - Contains comprehensive legend visibility checking functions:
   - `is_legend_actually_visible()` - Checks if legends are truly visible to users (not just `get_visible() == True`)
   - `verify_legend_visibility()` - Validates legend visibility across all subplots with detailed diagnostics
   - Goes beyond basic checks to verify positioning, bounds, content, and actual visual presence

2. **Enhanced `examples/05_multi_series_plotting.py`** - Now includes verification system:
   - **Always saves/shows plot first** for debugging
   - **Then runs verification** and fails with clear diagnostics if legends missing
   - **Exits with error code 1** if legends not visible
   - Currently **FAILING** because only 1/4 expected legends are visible

3. **Fixed previous legend strategy bug** - Updated `LegendManager._determine_strategy()` to use visual channel diversity detection for multi-subplot layouts

4. **Implemented axis-aware legend system** - Added `axis` field to `LegendEntry` and updated plotters to pass current axis

### Current Problem Identified

**The verification system revealed the real issue**: In example 5, only subplot 2 (line plot) has a visible legend, while subplots 0, 1, 3 (all scatter plots) show "No legend object exists" even though 132 legend entries are registered.

**Root Cause**: ScatterPlotter is registering entries with LegendManager but `_create_per_axes_legends()` isn't successfully creating legend objects on the scatter plot axes.

### Examples Analysis Completed

Analyzed all 19 examples and categorized which should/shouldn't have legends:

  Definitely Should Have Legends (Use Grouping Variables):

  - Example 05 - Multi-series plotting: Uses hue_by + marker_by/size_by/style_by/alpha_by (4/4 subplots should have legends)
  - Example 06 - Multi-metric plotting: Uses hue_by=METRICS, style_by="learning_rate" (4/4 subplots should have legends)
  - Example 07 - Grouped plotting: Uses hue_by="group" (4/4 subplots should have legends)
  - Example 08 - Color coordination: Uses hue_by="group" (4/4 subplots should have legends)
  - Example 19 - ML dashboard: Uses various grouping (hue_by=METRICS, style_by="learning_rate", etc.) (4/4 subplots should have legends)

  Partially Should Have Legends (Mixed):

  - Example 09 - Scatter showcase: 3/4 subplots use grouping (basic scatter in subplot 0,0 has no grouping)
  - Example 10 - Line showcase: 3/4 subplots use grouping (basic line in subplot 0,0 has no grouping)
  - Example 11 - Bar showcase: 1/2 subplots uses grouping (grouped bar only)
  - Example 12 - Violin showcase: 1/2 subplots uses grouping (grouped violin only)
  - Example 18 - Scientific figures: 2/6 subplots use grouping (Panel A: line with hue_by, Panel D: bar with hue_by)

  Special Case - Manual Legends:

  - Example 15 - Layering plots: Manually creates legends with label= parameters and ax.legend() calls (2/2 subplots should have legends)

  ❌ Examples that should NOT have visible legends:

  No Grouping Variables Used:

  - Example 01 - Quickstart: Simple scatter, no grouping
  - Example 02 - High-level API: All single-series plots, no grouping
  - Example 03 - Figure manager basics: All basic plots, no grouping
  - Example 04 - Plot registry: Same as example 3, no grouping
  - Example 13 - Heatmap showcase: Heatmaps don't use traditional legends
  - Example 14 - Contour showcase: Contour plots don't use discrete legends
  - Example 16 - Matplotlib integration: Shows styling but no grouping
  - Example 17 - Custom plotters: (need to check but likely no grouping)

  🔍 Key Patterns Identified:

  1. Grouping = Legends: Any plot using hue_by, style_by, size_by, marker_by, alpha_by, or METRICS should have legends
  2. Showcase Pattern: Many showcase examples follow a pattern: basic plot (no legend) + grouped variations (with legends)
  3. Single Series = No Legend: Simple plots with no visual encoding variables don't need legends
  4. Matrix Plots: Heatmaps and contours typically don't use discrete legends

  This analysis suggests that Examples 5, 6, 7, 8, 15, and 19 are the most critical ones to test with the verification system, as they should definitely
   have fully visible legends across all or most of their subplots.

**Should Have Legends (Critical to Test):**
- Example 05 (4/4 subplots) - Currently failing 
- Example 06 (4/4 subplots) - Multi-metrics
- Example 07 (4/4 subplots) - Grouped plotting  
- Example 08 (4/4 subplots) - Color coordination
- Example 15 (2/2 subplots) - Manual legends
- Example 19 (4/4 subplots) - ML dashboard

**Pattern**: Any plot using `hue_by`, `style_by`, `size_by`, `marker_by`, `alpha_by`, or `METRICS` should have legends.

### Implementation Status

**Legend Management System:**
- ✅ Visual channel diversity strategy detection working
- ✅ Axis-aware legend entries implemented
- ✅ Per-axes legend creation implemented
- ❌ **BROKEN**: ScatterPlotter legends not appearing despite entries being registered

**Verification System:**
- ✅ Comprehensive visibility checker implemented
- ✅ Integrated into example 5 with plot-first-then-fail behavior
- ✅ Detailed diagnostic output working perfectly

**Migrated Plotters Status:**
- ✅ HistogramPlotter: `use_style_applicator = True`, `use_legend_manager = True`
- ✅ ScatterPlotter: `use_style_applicator = True`, `use_legend_manager = True` (but legends broken)
- ✅ ViolinPlotter: `use_style_applicator = True`, `use_legend_manager = True`

### Next Steps After Compaction

1. **Debug ScatterPlotter legend issue** - Figure out why scatter plots aren't getting legend objects despite entries being registered
2. **Apply verification to other critical examples** (6, 7, 8, 15, 19)
3. **Continue plotter migration** - BarPlotter and LinePlotter are next priorities

### Key Technical Details

**Files Modified:**
- `src/dr_plotter/verification.py` - New verification system
- `src/dr_plotter/legend_manager.py` - Strategy detection + axis-aware legends  
- `examples/05_multi_series_plotting.py` - Integrated verification
- All migrated plotters - Pass `self.current_axis` to `create_legend_entry()`

**Current Test Command:**
```bash
uv run python examples/05_multi_series_plotting.py --save-dir .
# Shows: Only 1/4 legends visible, exits with error code 1
```

The verification system is working perfectly - it's revealing the real bugs that need fixing!
