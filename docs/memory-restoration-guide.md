# Memory Restoration Guide: Faceted Plotting Project

## Project Overview
We are implementing **Phase 2 of a faceted plotting system** for dr_plotter using ML training data (`data/mean_eval.parquet`). This is part of a multi-phase project to build comprehensive faceted plotting capabilities.

## What We've Accomplished ✅

### Phase 1 Complete
- Created `scripts/explore_mean_eval_data.py` - comprehensive data exploration script
- **Key finding**: 1,913 metrics, 25 data recipes, 14 model sizes, 100% data density
- Data structure validated for faceted plotting

### Phase 2 Complete  
- **Two working examples created**:
  1. `examples/06_faceted_training_curves.py` - Regular implementation
  2. `examples/06b_faceted_training_curves_themed.py` - Themed implementation

### Key Implementations
- **2×4 grid visualization**: 2 metrics (`pile-valppl`, `mmlu_average_correct_prob`) × 4 data recipes
- **14 model sizes as different colored lines** in each subplot
- **Shared legends** using `legend_strategy="figure_below"` 
- **Shared Y-axes within rows** using `sharey="row"`
- **Professional spacing** with proper margins and layout

### Recent Data Processing Fix 🎯
**CRITICAL**: Fixed major data loss issue by removing global `dropna()` and using per-metric filtering only:
- **Before**: 1,081 rows (lost 315 rows unnecessarily)
- **After**: 1,396 rows (29% more data!)
- **Key insight**: Each metric plots independently, so don't drop rows where other metrics have NaN

### Documentation Created
- `docs/phase-2-friction-analysis.md` - Complete friction point analysis
- `docs/theme-system-analysis.md` - Theme system deep dive

## Current Work In Progress 🚧

### Adding Advanced Controls
**Currently implementing** filtering, ordering, and axis limiting for both examples:

1. **Model size filtering/ordering**: `--model-sizes 4M 6M 150M 1B` 
2. **Recipe filtering/ordering**: `--recipes C4 Dolma1.7`
3. **Log scaling**: `--x-log --y-log`
4. **Axis limits**: `--xlim 1000 50000 --ylim 0.1 10`

### Status
- ✅ Regular version (`06_faceted_training_curves.py`) - **COMPLETE WITH ADVANCED CONTROLS**
- ✅ Themed version (`06b_faceted_training_curves_themed.py`) - **COMPLETE WITH ADVANCED CONTROLS**

## Key Technical Discoveries

### Legend System ✅ 
- `legend_strategy="figure_below"` works perfectly for unified legends
- Multiple options: "figure_below", "split", "per_axes", "none"

### Theme System ⚠️
- **Can store** axis scaling (`xscale="log"`, `yscale="log"`) in themes
- **Cannot automatically apply** - requires manual `ax.set_xscale()` calls
- **Theme stores intent but requires manual execution**

### Data Processing Pattern
```python
# GOOD - Per-metric filtering only
for metric in metrics:
    metric_data = data[["params", "step", metric]].dropna()

# BAD - Global filtering (loses data)
df.dropna()  # Don't do this!
```

## Phase 2 Status: COMPLETE ✅

**All Phase 2 objectives achieved:**
1. ✅ **Both examples fully functional** with comprehensive advanced controls
2. ✅ **All filtering/ordering combinations tested** and working correctly
3. ✅ **Documentation updated** with detailed friction analysis including advanced controls
4. ✅ **Comprehensive friction assessment** documented for Phase 3 planning

**Advanced controls successfully implemented:**
- Model size filtering and ordering
- Data recipe filtering and ordering  
- Independent axis log scaling (--x-log, --y-log)
- Axis range limiting (--xlim, --ylim)
- Dynamic grid sizing based on filtered data
- Full CLI interface with help documentation

## Key Files Created/Updated
- `examples/06_faceted_training_curves.py` - Main example ✅ **COMPLETE**
- `examples/06b_faceted_training_curves_themed.py` - Themed example ✅ **COMPLETE**
- `docs/phase-2-friction-analysis.md` - Main analysis document ✅ **UPDATED WITH ADVANCED CONTROLS**
- `docs/theme-system-analysis.md` - Theme deep dive ✅ **COMPLETE**
- Data file: `data/mean_eval.parquet`

## Current Command Pattern Examples
```bash
# Basic usage
uv run python examples/06_faceted_training_curves.py

# With filtering and options
uv run python examples/06_faceted_training_curves.py \
  --model-sizes 150M 300M 1B \
  --recipes C4 Dolma1.7 \
  --y-log \
  --xlim 5000 50000

# Help
uv run python examples/06_faceted_training_curves.py --help
```

## Critical Context
This is **research/exploration work** to identify friction points in dr_plotter for Phase 3 improvements. We're not just building examples - we're **systematically documenting every friction point** to guide library enhancements.

The goal is understanding what works well vs. what needs abstraction for better faceted plotting in Phase 3.