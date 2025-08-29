# Verification System Discovery: Complete Function Inventory

## Executive Summary

The verification system consists of 4 main files with 47+ verification and support functions spread across ~2,140 total lines of code. The system shows significant duplication and complexity that can be consolidated into a unified architecture.

**Key Finding**: Multiple verification paths exist for similar functionality (legend visibility, plot properties, color consistency) with different interfaces and scattered logic.

## File Structure Overview

| File | Lines | Primary Purpose | Key Dependencies |
|------|-------|-----------------|------------------|
| `verif_decorators.py` | 635 | Main decorator entry points | verification.py, plot_verification.py, plot_property_extraction.py |
| `verification.py` | 225 | Legend visibility logic | matplotlib |
| `plot_verification.py` | 779 | Plot property verification | plot_property_extraction.py |
| `plot_property_extraction.py` | 501 | Data extraction utilities | matplotlib |

## Comprehensive Function Inventory

### 1. Decorator Entry Points (`verif_decorators.py`)

| Function | Purpose | Parameters | Return Value | Dependencies |
|----------|---------|------------|--------------|--------------|
| `verify_plot_properties()` | Decorator for plot property validation | `expected_channels`, `min_unique_threshold`, `tolerance`, `fail_on_missing` | Decorated function | plot_verification.py |
| `verify_example()` | Main example verification decorator | `expected_legends`, `fail_on_missing`, `subplot_descriptions`, `verify_legend_consistency`, `expected_legend_entries`, `legend_tolerance`, `expected_channels` | Decorated function | verification.py, plot_verification.py |
| `verify_figure_legends()` | Figure-level legend verification | `expected_legend_count`, `legend_strategy`, `expected_total_entries`, `expected_channel_entries`, `expected_channels`, `tolerance`, `fail_on_missing` | Decorated function | plot_property_extraction.py, plot_verification.py |
| `report_subplot_line_colors()` | Debug decorator for color reporting | None | Decorated function | Internal utilities |

### 2. Legend Visibility Logic (`verification.py`)

| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `is_legend_actually_visible()` | Core legend visibility check | `ax`, `figure` (optional) | Dict with visibility details |
| `check_all_subplot_legends()` | Check all subplots in figure | `figure` | Dict mapping subplot index to results |
| `verify_legend_visibility()` | Main verification with output | `figure`, `expected_visible_count`, `fail_on_missing` | Dict with success status and issues |

### 3. Plot Property Verification (`plot_verification.py`)

#### Core Verification Functions
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `verify_channel_variation()` | Check if channel has sufficient variation | `collections`, `channel`, `min_unique_threshold` | VerificationResult dict |
| `verify_plot_properties_for_subplot()` | Main subplot property verification | `ax`, `expected_channels`, `min_unique_threshold`, `tolerance` | Dict with channel results |
| `verify_legend_plot_consistency()` | Compare plot data with legend | `ax`, `expected_varying_channels`, `expected_legend_entries`, `tolerance` | Dict with consistency checks |

#### Channel-Specific Consistency Checks
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `verify_marker_consistency()` | Compare plot vs legend markers | `plot_markers`, `legend_markers`, `expected_unique_markers` | Dict with consistency result |
| `verify_color_consistency()` | Compare plot vs legend colors | `plot_colors`, `legend_colors`, `tolerance` | Dict with consistency result |
| `verify_alpha_consistency()` | Compare plot vs legend alphas | `plot_alphas`, `legend_alphas`, `tolerance` | Dict with consistency result |
| `verify_size_consistency()` | Compare plot vs legend sizes | `plot_sizes`, `legend_sizes`, `tolerance` | Dict with consistency result |
| `verify_style_consistency()` | Compare plot vs legend styles | `plot_styles`, `legend_styles`, `expected_unique_styles` | Dict with consistency result |
| `verify_channel_uniformity()` | Check if channel values are uniform | `values`, `channel`, `tolerance` | Dict with uniformity result |

#### Figure-Level Strategy Verification
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `verify_figure_legend_strategy()` | Verify overall legend strategy | `figure_props`, `strategy`, `expected_count`, `expected_total_entries`, `expected_channel_entries`, `expected_channels`, `tolerance` | Dict with strategy verification |
| `verify_unified_figure_strategy()` | Check unified legend approach | `figure_props`, `expected_total_entries`, `result`, `tolerance` | Dict with unified strategy checks |
| `verify_split_figure_strategy()` | Check split legend approach | `figure_props`, `expected_channel_entries`, `expected_channels`, `result`, `tolerance` | Dict with split strategy checks |

#### Utility Functions
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `format_sample_values()` | Format values for display | `values`, `max_count` | List of formatted values |
| `_count_unique_floats()` | Count unique floats with tolerance | `values`, `tolerance` | Set of unique floats |
| `_count_unique_colors()` | Count unique colors with tolerance | `colors`, `tolerance` | Set of unique color tuples |

### 4. Data Extraction Functions (`plot_property_extraction.py`)

#### Core Collection Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_subplot_properties()` | Main extraction entry point | `ax` | Dict with all subplot properties |
| `extract_pathcollections_from_axis()` | Get PathCollection objects | `ax` | List of PathCollection |
| `extract_polycollections_from_axis()` | Get PolyCollection objects | `ax` | List of PolyCollection |
| `extract_barcontainers_from_axis()` | Get BarContainer objects | `ax` | List of BarContainer |
| `extract_lines_from_axis()` | Get Line objects | `ax` | List of Line objects |
| `extract_images_from_axis()` | Get AxesImage objects | `ax` | List of AxesImage |

#### Scatter Plot Property Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_scatter_positions()` | Get scatter point positions | `collection` | List of (x,y) tuples |
| `extract_scatter_colors()` | Get scatter point colors | `collection` | List of RGBA tuples |
| `extract_scatter_sizes()` | Get scatter point sizes | `collection` | List of floats |
| `extract_scatter_markers()` | Get scatter point markers | `collection` | List of marker strings |

#### Line Plot Property Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_line_colors()` | Get line colors | `lines` | List of RGBA tuples |
| `extract_line_styles()` | Get line styles | `lines` | List of style strings |
| `extract_line_markers()` | Get line markers | `lines` | List of marker strings |
| `extract_line_alphas()` | Get line alphas | `lines` | List of floats |

#### Violin/Polygon Property Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_violin_colors()` | Get violin plot colors | `collection` | List of RGBA tuples |
| `extract_violin_markers()` | Get violin plot markers | `collection` | List of strings ("violin") |
| `extract_violin_sizes()` | Get violin plot sizes | `collection` | List of floats (always [1.0]) |
| `extract_violin_alphas()` | Get violin plot alphas | `collection` | List of floats |
| `extract_violin_styles()` | Get violin plot styles | `collection` | List of style strings |

#### Bar Plot Property Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_bar_colors()` | Get bar colors | `container` | List of RGBA tuples |

#### Legend Property Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_legend_handles()` | Get legend handle objects | `ax` | List of Line2D |
| `extract_legend_markers()` | Get legend markers | `handles` | List of marker strings |
| `extract_legend_colors()` | Get legend colors | `handles` | List of RGBA tuples |
| `extract_legend_sizes()` | Get legend sizes | `handles` | List of floats |
| `extract_legend_labels()` | Get legend labels | `handles` | List of strings |
| `extract_legend_styles()` | Get legend styles | `handles` | List of style strings |

#### Figure-Level Legend Extractors
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `extract_figure_legend_properties()` | Get figure-level legend data | `fig` | Dict with legend properties |
| `extract_legend_colors_from_handles()` | Get colors from mixed handles | `handles` | List of RGBA tuples |
| `extract_legend_markers_from_handles()` | Get markers from mixed handles | `handles` | List of marker strings |
| `extract_legend_sizes_from_handles()` | Get sizes from mixed handles | `handles` | List of floats |

#### Utility Functions
| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `identify_marker_from_path()` | Determine marker type from path | `path` | Marker string |
| `_is_circle_approximation()` | Check if vertices form circle | `vertices` | Boolean |
| `_is_triangle_like()` | Check if vertices form triangle | `vertices` | Boolean |
| `convert_scatter_size_to_legend_size()` | Convert size units | `scatter_size` | Float |
| `convert_legend_size_to_scatter_size()` | Convert size units | `legend_size` | Float |
| `debug_legend_detection()` | Debug legend extraction | `ax` | Dict with debug info |
| `extract_image_data()` | Get image properties | `image` | Dict with image data |

### 5. Support Functions (`verif_decorators.py`)

| Function | Purpose | Parameters | Return Value |
|----------|---------|------------|--------------|
| `filter_main_grid_axes()` | Filter out auxiliary axes | `fig_axes` | List of main axes |
| `_print_failure_message()` | Format verification failure output | `name`, `expected`, `result`, `descriptions` | None (prints) |
| `extract_basic_subplot_info()` | Get basic subplot metadata | `ax` | Dict with title, labels, lines, legend |

## Duplication Analysis

### 1. Color Processing Duplication
**Location**: Multiple files handle color conversion and comparison
- `plot_verification.py`: `_count_unique_colors()`, `verify_color_consistency()`
- `plot_property_extraction.py`: `extract_scatter_colors()`, `extract_line_colors()`, `extract_legend_colors()`, etc.
- `verif_decorators.py`: Color extraction in `extract_basic_subplot_info()`

**Pattern**: All use `mcolors.to_rgba()` for normalization but different tolerance handling

### 2. Legend Data Extraction Duplication
**Location**: Legend property extraction appears in multiple places
- `plot_property_extraction.py`: `extract_legend_*()` functions (6 functions)
- `plot_property_extraction.py`: `extract_legend_*_from_handles()` functions (3 functions)  
- `verif_decorators.py`: Duplicate logic in `extract_basic_subplot_info()`

**Pattern**: Similar handle processing with different error handling approaches

### 3. Marker Processing Duplication
**Location**: Marker identification and comparison logic
- `plot_property_extraction.py`: `identify_marker_from_path()`, `extract_scatter_markers()`, `extract_legend_markers()`
- `plot_verification.py`: `verify_marker_consistency()`
- Various collection-specific marker extractors

**Pattern**: String-based marker identification with different fallback strategies

### 4. Size Conversion Duplication  
**Location**: Size unit conversions appear twice
- `plot_property_extraction.py`: `convert_scatter_size_to_legend_size()`, `convert_legend_size_to_scatter_size()`
- `plot_verification.py`: Import and usage of conversion functions

**Pattern**: Mathematical conversion between matplotlib size units

### 5. Float Tolerance Comparison Duplication
**Location**: Tolerance-based float comparison
- `plot_verification.py`: `_count_unique_floats()`, `_count_unique_colors()`
- Similar logic implied in size and alpha comparisons throughout

**Pattern**: Distance-based uniqueness checking with configurable tolerance

## Current Data Flow Documentation

### 1. Main Verification Flow (@verify_example)
```
User Function 
   ↓ (decorated with @verify_example)
verify_example() decorator
   ↓ (calls)
verify_legend_visibility() [verification.py]
   ↓ (calls)
check_all_subplot_legends() [verification.py]
   ↓ (calls)
is_legend_actually_visible() [verification.py]
   ↓ (returns visibility results)
Back to verify_example() for output formatting
```

### 2. Plot Properties Verification Flow (@verify_plot_properties)
```
User Function
   ↓ (decorated with @verify_plot_properties) 
verify_plot_properties() decorator
   ↓ (calls)
verify_plot_properties_for_subplot() [plot_verification.py]
   ↓ (calls)
extract_subplot_properties() [plot_property_extraction.py]
   ↓ (extracts data, then calls)
verify_channel_variation() [plot_verification.py]
   ↓ (returns channel verification results)
Back through chain for output formatting
```

### 3. Figure Legend Strategy Flow (@verify_figure_legends)
```
User Function
   ↓ (decorated with @verify_figure_legends)
verify_figure_legends() decorator
   ↓ (calls)
extract_figure_legend_properties() [plot_property_extraction.py]
   ↓ (then calls)
verify_figure_legend_strategy() [plot_verification.py]
   ↓ (routes to strategy-specific functions)
verify_unified_figure_strategy() or verify_split_figure_strategy()
   ↓ (returns strategy verification results)
Back through chain for output formatting
```

### 4. Consistency Verification Flow (when enabled)
```
verify_example() decorator
   ↓ (when verify_legend_consistency=True)
verify_legend_plot_consistency() [plot_verification.py]
   ↓ (calls)
extract_subplot_properties() [plot_property_extraction.py]
   ↓ (then calls multiple)
verify_*_consistency() functions [plot_verification.py]
   ↓ (each calls specific extraction functions)
Channel-specific extractors [plot_property_extraction.py]
   ↓ (returns consistency check results)
Back through chain for output formatting
```

## Interface Patterns and Inconsistencies

### 1. Parameter Patterns
**Consistent**: Most verification functions accept `tolerance` parameter
**Inconsistent**: 
- Some use `min_unique_threshold`, others use `expected_unique_*`
- `fail_on_missing` appears in decorators but not all verification functions
- Optional parameters handled inconsistently (some use None, others use defaults)

### 2. Return Value Patterns
**Consistent**: Most verification functions return Dict with `passed` boolean and `message` string
**Inconsistent**:
- Some include `details` key, others don't
- Error information structure varies (`issues`, `suggestions`, `checks`)
- Success/failure messaging format inconsistent

### 3. Error Handling Patterns  
**Inconsistent**:
- `verification.py`: Uses try/catch with fallback messages
- `plot_verification.py`: Assumes data availability, minimal error handling
- `plot_property_extraction.py`: Extensive try/catch in extraction functions
- `verif_decorators.py`: Mix of assertions and exception handling

### 4. Output Formatting Patterns
**Inconsistent**:
- Print statements scattered across verification functions
- Different emoji/symbol usage (✅❌🔴 vs checkmarks)
- Inconsistent indentation and formatting in messages
- Some functions print, others only return structured data

## Integration Points with Matplotlib

### 1. Direct Matplotlib Dependencies
- **Figure/Axes Objects**: All verification functions work with `plt.Figure` and `plt.Axes`
- **Collection Objects**: Extensive use of `PathCollection`, `PolyCollection`, `BarContainer`
- **Legend Objects**: Direct manipulation of `matplotlib.legend.Legend`
- **Artist Objects**: Working with `Line2D`, `AxesImage` objects

### 2. Color System Integration
- **Color Normalization**: Heavy use of `matplotlib.colors.to_rgba()`
- **Color Space Handling**: Assumes RGBA format throughout
- **Colormap Integration**: Basic colormap extraction for images

### 3. Size System Integration
- **Size Unit Conversion**: Complex conversion between scatter sizes and legend sizes
- **DPI Awareness**: Functions assume standard DPI settings
- **Canvas Interaction**: Legend visibility checking requires canvas.draw()

## Quality Issues Identified

### 1. Code Duplication (High Priority)
- **Legend extraction logic repeated 3+ times**
- **Color processing scattered across files**  
- **Similar verification patterns with different interfaces**

### 2. Inconsistent Error Handling (Medium Priority)
- **Mix of exceptions, assertions, and graceful degradation**
- **Inconsistent fallback strategies**
- **Some functions fail silently, others exit(1)**

### 3. Interface Complexity (Medium Priority)  
- **Too many optional parameters in decorators**
- **Inconsistent return value structures**
- **Mixed responsibilities (verification + formatting + output)**

### 4. Testing/Debug Support (Low Priority)
- **Debug functions scattered across files** 
- **Inconsistent debug output formats**
- **Limited introspection capabilities**

## Recommendations for Consolidation

### 1. Unified Architecture Approach
Create a single verification engine with:
- **Common data extraction layer**
- **Pluggable verification rules**
- **Consistent output formatting**
- **Centralized error handling**

### 2. Eliminate Duplication
- **Consolidate legend extraction to single implementation**
- **Create unified color/marker/size processing utilities**
- **Standardize tolerance-based comparison functions**

### 3. Simplify Interfaces
- **Reduce decorator parameter complexity**
- **Standardize return value structures**
- **Separate verification logic from output formatting**

### 4. Improve Maintainability
- **Clear separation of concerns between files**
- **Consistent error handling strategy**
- **Better debug/introspection support**

This discovery reveals a system ripe for consolidation with clear opportunities to reduce complexity while maintaining comprehensive verification capabilities.