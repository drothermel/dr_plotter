# Lab Notebook: Faceted Plotting Implementation

## Project Info
- **Date**: 2025-08-26
- **Project**: Implement systematic support for multi-dimensional faceted plotting in dr_plotter
- **Duration**: Multi-phase project - currently in Phase 1-2 planning
- **Status**: In Progress - Phase 1 complete, Phase 2 ready to execute

## Results Summary
- **Phase 1 data analysis**: Complete systematic exploration of mean_eval.parquet structure
- **Dataset validation**: 1,913 metrics × 25 data recipes × 14 model sizes with 100% data density
- **Phase 2 prompt**: Comprehensive agent instructions for example implementation created
- **Planning artifacts**: 2 systematic implementation plans, 2 agent prompts ready for execution

## Code Changes
### File: docs/plans/2025-08-26-faceted-plotting-implementation.md
- **Lines 15-28**: 4-phase systematic process (Analysis → Example → Design → Implementation)
- **Lines 42-51**: Evidence-based approach with phase-to-phase validation
- **Lines 53-62**: Key architectural questions about scope boundary and configuration patterns

### File: scripts/explore_mean_eval_data.py
- **Lines 4-5**: load_parquet_data() function with direct pandas loading
- **Lines 7-17**: validate_data_structure() with comprehensive column and type validation
- **Lines 19-22**: extract_available_metrics() filtering non-metric columns systematically
- **Lines 30-64**: analyze_data_completeness() with missing combination detection and null analysis
- **Lines 66-165**: main() function with formatted output across validation, dimensions, and completeness

### File: docs/plans/phase-1-agent-prompt.md
- **Entire file**: 85-line comprehensive prompt for data exploration with project standards
- **Lines 25-40**: Required function structure with type hints and validation approach

### File: docs/plans/phase-2-agent-prompt.md
- **Entire file**: 120-line systematic prompt for example implementation
- **Lines 20-27**: Exact target specification (2×4 grid, specific metrics and data recipes)
- **Lines 60-67**: Required dr_plotter investigation before implementation

## Bugs Encountered & Fixes
### Bug 1: Model size ordering assumption
- **Location**: Phase 1 data analysis planning
- **Issue**: Model sizes sort alphabetically (10M, 14M, 150M) not numerically (4M, 6M, 8M, 10M...)
- **Discovery**: Phase 1 agent output revealed: "Model sizes (14 total): 1. 10M, 2. 14M, 3. 150M, 4. 16M, 5. 1B..."
- **Impact**: Phase 2 must handle proper numeric ordering for logical line styling
- **Fix**: Phase 2 prompt explicitly requires create_model_size_ordering() function

### Bug 2: Metric name assumptions  
- **Location**: Initial planning discussions
- **Issue**: Assumed metrics would have hyphens (pile-valppl) but actual data uses underscores
- **Discovery**: Phase 1 output shows actual metric names: pile_valppl, mmlu_avg_correct_prob
- **Fix**: Phase 2 prompt uses correct underscore metric names

## Technical Discoveries
- **Data completeness**: Perfect 100% density across all 350 model_size × data_recipe combinations
- **Null value patterns**: 18-63% null values in metrics normal for ML evaluation data
- **Training progression**: 6-54 steps per combination, 0-69,369 step range indicates varied training lengths
- **Metric scale**: 1,913 total metrics provides rich subset selection options for faceted examples
- **Agent prompt effectiveness**: Comprehensive prompts with explicit requirements produce focused, compliant implementations

## Ideas & Notes
- **Phase boundary insight**: Natural division between dr_plotter (subplot grids, styling) and user code (data prep, metric selection)
- **Configuration complexity**: Current approach likely requires significant boilerplate for multi-subplot styling consistency
- **Reusability potential**: Faceting patterns could apply to many ML evaluation scenarios beyond this dataset
- **Performance consideration**: 14 lines per subplot × 8 subplots = 112 total line objects to manage

## Environment Notes
- **Dependencies**: Project uses uv for package management, existing dr_plotter library structure
- **Data source**: data/mean_eval.parquet confirmed accessible and well-structured
- **Agent coordination**: Two-agent approach (Phase 1 exploration, Phase 2 implementation) working effectively
- **Development tools**: All standard project commands available (lint, format, mp, pt)

## References
- **Phase 1 execution**: scripts/explore_mean_eval_data.py successfully executed with comprehensive output
- **Planning documents**: 4 total planning artifacts in docs/plans/
- **Target visualization**: 2-row × 4-column grid with pile_valppl/mmlu_avg_correct_prob metrics
- **Next execution**: Phase 2 agent ready to implement examples/06_faceted_training_curves.py