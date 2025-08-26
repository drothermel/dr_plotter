# Migration Context & Guidance

## 🎯 Current Task
Just completed extracting duplicate group label logic in BasePlotter into `_build_group_label()` helper method. Test revealed an issue with labels not appearing - needs investigation after memory compaction.

## 📍 Where We Are

### Completed Infrastructure
1. **StyleApplicator** (`src/dr_plotter/style_applicator.py`)
   - Phased styling system (plot → post → axes → legend)
   - Component schemas now read from plotter classes
   - Post-processor registration for artist modification

2. **LegendManager** (`src/dr_plotter/legend_manager.py`)
   - LegendEntry, LegendRegistry, LegendConfig classes
   - Figure-level legend coordination
   - Automatic deduplication

3. **Migrated Plotters** (3/8 complete)
   - ✅ HistogramPlotter
   - ✅ ScatterPlotter  
   - ✅ ViolinPlotter

## 🚀 Migration Process for Remaining Plotters

### Step-by-Step Plotter Migration

#### 1. Add Class Attributes
```python
class PlotterName(BasePlotter):
    use_style_applicator: bool = True
    use_legend_manager: bool = True
    
    component_schema: Dict[Phase, ComponentSchema] = {
        "plot": {
            "main": {
                # matplotlib kwargs this plotter accepts
            }
        },
        "post": {
            # components that can be styled after creation
        }
    }
```

#### 2. Register Post-Processors (if needed)
```python
def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    if self.use_style_applicator:
        self.style_applicator.register_post_processor(
            "plotter_name", "component", self._style_component
        )
```

#### 3. Update _draw() Method
```python
def _draw(self, ax: Any, data: pd.DataFrame, legend: Legend, **kwargs: Any) -> None:
    label = kwargs.pop("label", None)  # Extract label before matplotlib
    
    # matplotlib plotting call
    artist = ax.plot_method(data, **kwargs)
    
    if self.use_style_applicator:
        artists = {"component": artist}
        self.style_applicator.apply_post_processing("plotter_name", artists)
    
    # Handle legend
    self._apply_post_processing(artist, legend, label)
```

#### 4. Implement _apply_post_processing()
```python
def _apply_post_processing(
    self, artist: Any, legend: Legend, label: Optional[str] = None
) -> None:
    if self.use_legend_manager and self.figure_manager and label:
        proxy = self._create_proxy_artist(artist)
        if proxy:
            entry = self.style_applicator.create_legend_entry(proxy, label)
            if entry:
                self.figure_manager.register_legend_entry(entry)
    elif label:
        # Fallback to old system
        legend.add_patch(label=label, ...)
```

### Migration Priority Order

#### High Priority (Simple)
1. **BarPlotter** - Similar to HistogramPlotter, returns BarContainer
2. **LinePlotter** - Returns Line2D objects, straightforward

#### Medium Priority (Complex)
3. **HeatmapPlotter** - Different pattern (image-based), may need special handling
4. **ContourPlotter** - Multi-component like ViolinPlotter

#### Low Priority
5. **BumpPlotter** - Inherits from LinePlotter, special case

## ⚠️ Key Patterns & Gotchas

### Always Remember
1. **GroupingConfig never None** - Always pass `GroupingConfig()` even if empty
2. **Pop label before matplotlib** - `label = kwargs.pop("label", None)`
3. **Check for use_style_applicator** - Maintain backward compatibility
4. **Proxy artist types**:
   - Patches/Bars → Patch
   - Lines → Line2D
   - Collections → Line2D with marker
   - Images → Special handling needed

### Common Issues
- `active_channels` is a Set, not Dict
- Some matplotlib methods don't accept 'label' kwarg (like violinplot)
- PathCollections store arrays of colors, not single values
- Post-processing happens AFTER style applicator's post phase

## 🔍 Testing Approach

For each migrated plotter, test:
1. Basic plot with label
2. Grouped plot (if supported)
3. Multi-subplot with figure legend
4. Backward compatibility (use_legend_manager=False)
5. Without FigureManager (standalone)

## 📝 Files to Reference

- **Examples**: Look at migrated plotters for patterns
  - `src/dr_plotter/plotters/histogram.py` - Simple case
  - `src/dr_plotter/plotters/scatter.py` - Collection handling
  - `src/dr_plotter/plotters/violin.py` - Multi-component

- **Documentation**:
  - `docs/plans/legend_management_implementation.md` - Full architecture
  - `docs/style_refactor_progress.md` - Current status

## 🎯 Success Criteria

Each migrated plotter should:
- ✅ Use component schemas from class attribute
- ✅ Support post-processing if needed
- ✅ Create appropriate legend entries
- ✅ Maintain backward compatibility
- ✅ Pass all test scenarios

## Next Steps After Memory Compaction

1. Fix the label issue in test (labels not appearing in legend)
2. Continue with BarPlotter migration (easiest next target)
3. Then LinePlotter
4. Document patterns for complex plotters (Heatmap, Contour)