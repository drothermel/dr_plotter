# Faceted Plotting Implementation: Chunk 1 - Foundation Layer

## Project Context

You are implementing **Chunk 1 of 6** for native faceting support in dr_plotter. This is the foundation layer that creates the basic infrastructure needed by all subsequent chunks.

**Your role**: Implement the core `FacetingConfig` class and file structure changes with no complex logic - just solid, testable foundation code.

## Key References

**MANDATORY**: Before starting, read these docs to understand the project:
- `docs/DESIGN_PHILOSOPHY.md` - Core principles and coding standards
- `docs/plans/faceted_plotting_detailed_design.md` - Complete technical architecture 
- `docs/plans/faceted_plotting_implementation_plan.md` - Your place in the overall plan

## Your Tasks

### Task 1: Create FacetingConfig File Structure

**File**: `src/dr_plotter/faceting_config.py`

Create new file with complete `FacetingConfig` dataclass based on detailed design specification. Include ALL parameters from the design doc:

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class FacetingConfig:
    # Core dimensions
    rows: Optional[str] = None
    cols: Optional[str] = None  
    lines: Optional[str] = None
    
    # Layout control
    ncols: Optional[int] = None
    nrows: Optional[int] = None
    
    # [Include ALL other parameters from detailed design]
    
    def validate(self) -> None:
        """Validate configuration consistency."""
        # Implement ALL validation rules from detailed design
```

**Requirements**:
- Follow dr_plotter coding standards (no comments, complete type hints, assertions over exceptions)
- Include every parameter specified in the detailed design document
- All type hints must be comprehensive and correct

### Task 2: Implement Comprehensive Validation

**Method**: `FacetingConfig.validate()`

Implement validation for ALL configuration conflicts identified in the design:

**Required Validations**:
1. **Layout conflicts**: Cannot specify both explicit grid (rows+cols) and wrap layout (ncols/nrows)
2. **Dimension requirements**: Must specify at least one of rows or cols
3. **Targeting conflicts**: Cannot specify both target_row and target_rows (same for cols)
4. **Parameter type validation**: ncols/nrows must be positive integers if specified
5. **Shared axis validation**: shared_x/shared_y must be valid values if specified
6. **Empty subplot strategy**: Must be one of "warn", "error", "silent"

**Error Message Standards**:
- Use `assert` statements with descriptive messages (not exceptions)
- Include current values in error messages for debugging
- Provide specific guidance about valid alternatives

### Task 3: Clean Up Figure Config

**File**: `src/dr_plotter/figure_config.py`

Remove the unused `SubplotFacetingConfig` class and all references to it:
- Delete the entire class definition
- Remove any imports related to it
- Update any docstrings or comments that reference it

**Validation**: Ensure all existing `FigureConfig` functionality remains unchanged.

### Task 4: Update Import Structure  

**File**: `src/dr_plotter/__init__.py`

Add `FacetingConfig` to the public API:
- Import `FacetingConfig` from `faceting_config`
- Ensure it's accessible as `from dr_plotter import FacetingConfig`
- Maintain all existing imports unchanged

### Task 5: Write Comprehensive Tests

**File**: `tests/test_faceting_config.py` (create new file)

Write unit tests covering:

**Basic Functionality Tests**:
- Configuration creation with default values
- Configuration creation with all parameters specified
- Parameter access and modification

**Validation Tests** (test every validation rule):
- Valid configurations pass validation
- Invalid configurations fail with correct error messages
- Edge cases (empty values, boundary conditions)

**Integration Tests**:
- Import works correctly from main package
- Type hints work with IDE/mypy
- Configuration serialization (if applicable)

**Testing Standards**:
- Use pytest format
- Follow existing dr_plotter test patterns
- 100% coverage of validation logic
- Clear test names describing what's being tested

## Success Criteria

Before marking this chunk complete, verify:

- [ ] `FacetingConfig` can be imported: `from dr_plotter import FacetingConfig`
- [ ] All parameters from detailed design are included with correct types
- [ ] Configuration validation catches all documented conflicts with clear error messages
- [ ] `SubplotFacetingConfig` completely removed with no references remaining
- [ ] All existing dr_plotter functionality works unchanged (run existing tests)
- [ ] New tests achieve 100% coverage of validation logic
- [ ] Code follows dr_plotter standards (no comments, assertions over exceptions, complete type hints)

## Implementation Notes

### Code Quality Requirements
- **No comments anywhere** - code must be self-documenting through clear naming
- **Complete type hints** - every parameter and return value must be typed
- **Assertions not exceptions** - use `assert condition, "message"` for validation
- **Zero backward compatibility breaks** - all existing code must continue working

### Testing Approach
- Test happy path configurations first
- Test each validation rule in isolation  
- Test combinations of validation failures
- Include edge cases (None values, empty lists, boundary integers)

### Common Pitfalls to Avoid
- Don't implement any plotting logic (that's for later chunks)
- Don't add features beyond what's specified in the detailed design
- Don't use try/catch blocks - let errors bubble up or use assertions
- Don't break existing functionality (run full test suite)

## Documentation Requirements

When you complete this chunk, update the implementation plan:

**File**: `docs/plans/faceted_plotting_implementation_plan.md`

In the "Notes & Learnings" section, add your observations under "Chunk 1 Notes":
- Any issues encountered during implementation
- Decisions made about ambiguous requirements
- Testing insights or patterns that worked well
- Recommendations for subsequent chunks
- Performance or architectural observations

## Next Steps

After completing this chunk successfully:
1. Update progress checkboxes in implementation plan
2. Ensure all success criteria are met
3. Document learnings and observations
4. Ready for code review before proceeding to Chunk 2

Your foundation work here is critical for all subsequent chunks. Focus on solid, well-tested infrastructure that subsequent chunks can build on confidently.