# Faceted Plotting: Implementation Plan & Progress Tracking

## Overview

**Objective**: Implement native faceting support in dr_plotter using risk-based, incremental approach with agent-driven implementation.

**Architecture Reference**: See [`faceted_plotting_detailed_design.md`](./faceted_plotting_detailed_design.md) for complete technical specifications.

**Strategy**: 6 focused chunks building incrementally from foundation → core functionality → advanced features → polish.

## Implementation Chunks

### ✅ Chunk 1: Foundation Layer (Small - Low Risk) - COMPLETED
**Scope**: Basic infrastructure without complex logic
- [x] Create `src/dr_plotter/faceting_config.py` file  
- [x] Implement `FacetingConfig` dataclass with all parameters from design spec
- [x] Implement `FacetingConfig.validate()` method with parameter conflict detection
- [x] Remove unused `SubplotFacetingConfig` from `figure_config.py`
- [x] Update `__init__.py` imports to include `FacetingConfig`
- [x] Write unit tests for configuration creation and validation

**Dependencies**: None

**Success Criteria**: ✅ ALL MET
- ✅ `FacetingConfig` can be imported and instantiated
- ✅ Validation catches all documented parameter conflicts  
- ✅ Clear error messages for invalid configurations
- ✅ All existing functionality unchanged

**Agent Prompt**: `chunk_1_foundation_prompt.md`

---

### ☐ Chunk 2: Grid Computation Engine (Medium - Medium Risk)
**Scope**: Core grid layout logic without plotting  
- [ ] Implement `FigureManager._compute_facet_grid()` method
- [ ] Support explicit grid layout (rows + cols specified)
- [ ] Support wrapped layout (single dimension + ncols/nrows)
- [ ] Implement `FigureManager._resolve_targeting()` method  
- [ ] Add grid dimension validation against data
- [ ] Add targeting validation (indices within bounds)
- [ ] Write comprehensive unit tests for all layout modes

**Dependencies**: Chunk 1 (FacetingConfig)

**Success Criteria**:
- Correct grid dimensions computed for all configuration modes
- Targeting resolves to correct subplot position lists
- Clear errors for invalid grid/targeting combinations
- Full test coverage of edge cases

**Agent Prompt**: `chunk_2_grid_computation_prompt.md`

---

### ☐ Chunk 3: Basic Plot Integration (Medium - Medium Risk)  
**Scope**: Simple faceting without advanced features
- [ ] Implement core `FigureManager.plot_faceted()` method structure
- [ ] Implement `_resolve_faceting_config()` with parameter override logic
- [ ] Implement `_prepare_facet_data()` for basic data subsetting
- [ ] Add basic data column validation (`_validate_faceting_inputs()`)
- [ ] Integration with existing `plot()` method for actual plotting
- [ ] Support explicit grids only (no wrapping, no targeting, no advanced styling)
- [ ] Write integration tests with real data

**Dependencies**: Chunk 2 (grid computation)

**Success Criteria**:
- Simple faceted plots work end-to-end (rows + cols + lines)
- Parameter resolution works (direct params override config)
- Data validation provides helpful error messages
- Integration with existing plot types works
- Basic examples from requirements doc work

**Agent Prompt**: `chunk_3_basic_integration_prompt.md`

---

### ☐ Chunk 4: Advanced Layout Features (Medium - Higher Risk)
**Scope**: Complex layout modes and targeting
- [ ] Implement wrapped layout support in `plot_faceted()` 
- [ ] Implement targeting system (target_row, target_col, target_rows, target_cols)
- [ ] Implement per-subplot configuration (nested list parameters)
- [ ] Add `_apply_subplot_configuration()` for x_labels, xlim, ylim, etc.
- [ ] Add grid resizing logic and validation against existing plots
- [ ] Implement empty subplot handling with configurable strategy
- [ ] Write comprehensive tests for all advanced layout modes

**Dependencies**: Chunk 3 (basic integration)

**Success Criteria**:
- Wrapped layouts work correctly (proper fill order)
- Targeting applies plots to correct subplot subsets only
- Nested list parameters (x_labels, xlim) apply to individual subplots
- Empty subplot strategy works (warn/error/silent)
- All layout examples from detailed design work

**Agent Prompt**: `chunk_4_advanced_layout_prompt.md`

---

### ☐ Chunk 5: Style Coordination System (Large - Highest Risk)
**Scope**: Figure-level styling consistency  
- [ ] Implement `FacetStyleCoordinator` class
- [ ] Add figure-level style state management to `FigureManager`
- [ ] Implement `_get_or_create_style_coordinator()` method
- [ ] Add cross-subplot styling consistency (same data values → same colors/markers)
- [ ] Support style persistence across multiple `plot_faceted()` calls
- [ ] Integration with theme system and existing styling patterns
- [ ] Write tests for layered faceting scenarios

**Dependencies**: Chunk 4 (advanced layouts)

**Success Criteria**:
- Same `lines` dimension values get consistent styling across all subplots
- Multiple `plot_faceted()` calls maintain style consistency (layered faceting)
- Integration with theme system works correctly
- Style coordinator state managed properly
- All layered faceting examples from detailed design work

**Agent Prompt**: `chunk_5_style_coordination_prompt.md`

---

### ☐ Chunk 6: Validation & Polish (Medium - Low Risk)
**Scope**: Comprehensive error handling and edge cases
- [ ] Enhance data validation system with comprehensive column checking
- [ ] Improve error messages with helpful suggestions (available columns, etc.)
- [ ] Add performance optimizations for large datasets
- [ ] Add debug/inspection tools (`debug=True`, `get_facet_info()`)
- [ ] Comprehensive edge case testing (missing data, malformed inputs, etc.)
- [ ] Documentation string updates for all new methods
- [ ] Final integration testing with existing dr_plotter functionality

**Dependencies**: Chunk 5 (style coordination)

**Success Criteria**:
- All edge cases handled gracefully
- Error messages provide actionable guidance
- Performance acceptable for large datasets and complex grids
- Debug tools help with troubleshooting
- Full backward compatibility maintained
- All requirements from spec satisfied

**Agent Prompt**: `chunk_6_validation_polish_prompt.md`

## Progress Overview

**Completed**: 1/6 chunks
**In Progress**: None  
**Remaining**: 5 chunks

**Current Status**: Chunk 1 (Foundation Layer) completed successfully. Ready to begin Chunk 2 (Grid Computation Engine).

## Notes & Learnings

*This section will be updated by implementation agents as they work through each chunk. Each agent should document their observations, learnings, and any issues encountered.*

### Implementation Agent Notes
*Agents: Please add your observations here as you complete each chunk*

#### Chunk 1 Notes:
**Implementation completed successfully with no major issues encountered.**

**Key Decisions Made:**
- Used union type `str | List[List[Optional[str]]]` for `subplot_titles` parameter to support both automatic and explicit title configurations
- Included comprehensive type hints following dr_plotter standards (no comments, complete typing)
- Implemented validation using assertions rather than exceptions, following the design philosophy
- Error messages include current parameter values to aid debugging
- Created comprehensive test coverage (6 test classes, 25+ test methods) covering all validation rules and edge cases

**Code Quality Observations:**
- All validation logic implemented with clear assertion messages
- Followed dr_plotter's "no comments" policy - code is self-documenting through clear naming
- Type hints are comprehensive and support both IDE completion and mypy checking
- Tests follow pytest conventions and cover 100% of validation logic

**Integration Points:**
- Successfully removed `SubplotFacetingConfig` from `figure_config.py` and all references in `FigureManager`
- Updated import structure in `__init__.py` to make `FacetingConfig` available from main package
- All existing functionality preserved - no breaking changes introduced

**Testing Insights:**
- Test structure separates basic functionality, validation rules, edge cases, and integration
- Validation tests check both that valid configurations pass and invalid ones fail with correct messages  
- Edge case testing covers None values, empty lists, boundary conditions
- Integration tests verify import paths and dataclass serialization compatibility

**Recommendations for Next Chunks:**
- Chunk 2 can proceed as planned - foundation is solid and well-tested
- Grid computation logic will build naturally on the validation rules established here
- Style coordination (Chunk 5) should leverage the existing parameter structure without modification
- Testing patterns established here should be replicated in subsequent chunks

#### Chunk 2 Notes:  
*To be filled by implementation agent*

#### Chunk 3 Notes:
*To be filled by implementation agent*

#### Chunk 4 Notes:
*To be filled by implementation agent*

#### Chunk 5 Notes:
*To be filled by implementation agent*

#### Chunk 6 Notes:
*To be filled by implementation agent*

### Architecture Evolution
*Document any changes to the original design discovered during implementation*

### Testing Insights
*Document testing patterns that work well or reveal issues*

### Performance Observations  
*Document any performance considerations discovered during implementation*

### Integration Discoveries
*Document any unexpected interactions with existing dr_plotter systems*

## Review Checkpoints

After each chunk completion:
1. **✅ Functionality Test**: Verify all success criteria met
2. **✅ Architecture Review**: Confirm design assumptions still valid  
3. **✅ Integration Check**: Ensure no regressions in existing functionality
4. **✅ Plan Assessment**: Determine if subsequent chunks need adjustment

## Risk Mitigation

**High Risk Areas**:
- Chunk 5 (Style Coordination): Most complex, novel functionality
- Integration points with existing FigureManager functionality
- Performance with large datasets and complex grids

**Mitigation Strategies**:
- Incremental testing at each step
- Early integration testing with existing examples
- Performance testing with realistic data sizes
- Architecture review after each major chunk

## Success Metrics

**Functional Goals**:
- [ ] All core requirements from spec implemented
- [ ] All extended requirements from spec implemented  
- [ ] 95+ line examples reduced to <20 lines with new API
- [ ] All existing dr_plotter functionality preserved

**Quality Goals**:  
- [ ] Comprehensive test coverage (>90%)
- [ ] Clear, helpful error messages
- [ ] Performance comparable to manual subplot management
- [ ] Publication-ready output quality maintained