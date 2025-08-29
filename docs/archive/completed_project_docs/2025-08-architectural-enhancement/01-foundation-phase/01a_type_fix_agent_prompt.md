# Agent Task: Quick Type Annotation Fix

## Task Overview
Fix incorrect return type annotation in `ylabel_from_metrics` function to match actual implementation behavior.

## Specific Instructions

### File to Modify
`src/dr_plotter/plotters/base.py`

### Exact Change Required
- **Location**: Line 39 (approximately)
- **Function**: `ylabel_from_metrics`
- **Current annotation**: `-> str`
- **New annotation**: `-> Optional[str]`
- **Reason**: Function returns `None` when `len(metrics) != 1`

### Implementation Steps
1. **Read the file** to understand current implementation
2. **Locate the function** `ylabel_from_metrics` 
3. **Verify the issue**: Confirm function can return `None` on line 41
4. **Add import** if needed: Add `Optional` to existing typing imports
5. **Update annotation**: Change `-> str` to `-> Optional[str]`

### Success Criteria
- Function annotation matches actual implementation behavior
- Import statement includes `Optional` if not already present
- No other changes to function logic or behavior
- Type checking validation passes

### Context
This is Phase 1 Step 1 of our systematic architectural improvement roadmap. This fix establishes type system integrity as foundation for subsequent improvements.

### Expected Outcome
Type annotation correctly reflects that function may return `None`, eliminating type system integrity violation with zero behavioral changes.