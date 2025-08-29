# Agent Task: Try-Catch Block Elimination (Phase 1 Step 2)

## Task Overview
Eliminate all try-catch blocks in parameter validation contexts to establish fail-fast principle compliance with DR methodology. Replace defensive programming patterns with assertion-based validation.

## Specific Locations to Fix

### File 1: `src/dr_plotter/plotters/violin.py`
- **Lines 133-147**: Try-catch block for facecolor validation
- **Lines 152-166**: Try-catch block for edgecolor validation  
- **Issue**: Bare except clauses that silence all exceptions
- **Replace with**: Assertions or specific exception handling

### File 2: `src/dr_plotter/plotters/base.py`
- **Lines 158-165**: Try-catch block in parameter validation
- **Issue**: Empty pass statement after successful execution
- **Replace with**: Assertion-based validation or remove defensive pattern

## Implementation Guidelines

### DR Methodology Requirements
- **Fail Fast, Fail Loud**: Let errors surface immediately rather than masking them
- **Assertions Over Exceptions**: Use `assert condition, "clear message"` for validation
- **No Defensive Programming**: Eliminate patterns that hide bugs or reduce clarity

### Conversion Pattern
```python
# BEFORE (Anti-pattern):
try:
    facecolor = some_operation()
except:
    facecolor = default_value

# AFTER (DR Methodology):
assert condition_is_valid, f"Clear error message: {context}"
facecolor = some_operation()
```

### Success Criteria
- **Zero try-catch blocks** in parameter validation contexts
- **Clear error messages** when validation fails
- **Preserved functionality** - same behavior for valid inputs
- **Improved error detection** - invalid inputs fail fast with clear messages

## Specific Instructions
1. **Read both files** to understand current try-catch usage
2. **Identify validation context** for each try-catch block
3. **Determine appropriate assertion** or validation approach
4. **Replace try-catch** with fail-fast validation
5. **Test edge cases** to ensure proper error handling
6. **Verify no bare except clauses** remain in validation code

## Context
This is Phase 1 Step 2 of systematic architectural improvement. Try-catch elimination establishes the fail-fast principle that enables confident type system work in subsequent phases.

## Expected Outcome
- All parameter validation uses assertion-based patterns
- Errors surface immediately with clear context
- Foundation established for Phase 2 type system completion
- DR methodology principle compliance achieved