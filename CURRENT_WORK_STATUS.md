# Current Work Status - Bump Plot Development

## Context
Working on dr_plotter library with strategic/tactical collaboration approach. Read `docs/processes/strategic_collaboration_guide.md`, `docs/processes/tactical_execution_guide.md`, and `docs/processes/design_philosophy.md` first.

## What We've Built
Created `scripts/plot_bump.py` - a fully functional bump plot script that:

### ✅ Completed Features
1. **Command-line interface** like `plot_seeds.py`:
   - `--data` with named recipe groups (e.g., "core_datasets", "best_ppl", "good_ppl")  
   - `--params` for model sizes
   - `--exclude-params` / `--exclude-data` for filtering
   - `--save`, `--no-show`, `--figsize` options

2. **Named recipe groups** from `datadec_utils.py`:
   - `base`, `base_qc`, `no_ablations`
   - Custom families: `core_datasets`, `dolma17_variants`, `dclm_variants`, etc.
   - Performance-based: `best_ppl`, `good_ppl`, `medium_ppl`, `poor_ppl`
   - OLMES performance: `best_olmes`, `good_olmes`, etc.

3. **Data processing fixes**:
   - Handles different max training steps per model size
   - Uses final available step for each model size (not global max)
   - Proper numerical sorting of model sizes (4M → 6M → ... → 1B)

4. **Visual enhancements**:
   - **Left-side labels**: Show recipe names at initial rankings
   - **Value annotations**: Perplexity values floating over each point
   - **Metric label**: Top-left corner showing what values represent
   - **Fixed label alignment**: Left and right labels now match properly

### 🔄 Current Issue
**Color palette limitation**: Despite creating `create_bump_theme_with_colors()` with extended 30+ color palette, the plot still uses default 8 colors. Need to investigate:

1. **Theme passing**: Check if `style={"theme": custom_theme}` in PlotConfig actually reaches BumpPlotter
2. **BumpPlotter color source**: In `bump.py:69-74`, it uses hardcoded `base_colors` from styler, not theme
3. **Direct override**: Find way to pass colors directly without theme system

### 🎯 Next Steps
1. **Investigate theme flow**: Trace how themes reach plotters in the library code
2. **Find color override**: Look for direct way to pass color list to BumpPlotter
3. **Fix color issue**: Either fix theme passing or implement direct color override

### 📁 Key Files
- `scripts/plot_bump.py` - Main script (fully functional except colors)  
- `src/dr_plotter/plotters/bump.py:69-74` - Where colors are assigned
- `src/dr_plotter/theme.py` - Theme system with BASE_COLORS and BUMP_PLOT_THEME
- `src/dr_plotter/scripting/datadec_utils.py` - Recipe group constants

### 🧪 Test Commands
```bash
# Works great, but needs more colors:
uv run python scripts/plot_bump.py --data "best_ppl"
uv run python scripts/plot_bump.py --data "core_datasets"

# Shows 7 recipes but only 5-6 distinct colors due to cycling
```

### 💡 Debug Insight
BumpPlotter hardcodes colors in `_plot_specific_data_prep()` instead of using theme system. This is the root issue to solve.