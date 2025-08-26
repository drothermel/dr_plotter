# Phase 1: Foundation Implementation Plan

## Status: Ready to Begin
**Branch**: Create new implementation branch after current PR merge

## Implementation Sequence

### 1. Quick Type Fix (5 minutes) ✅ COMPLETE
- **File**: `src/dr_plotter/plotters/base.py:39`  
- **Change**: `-> str` to `-> Optional[str]` for `ylabel_from_metrics`
- **Why**: Immediate type safety, demonstrates systematic approach
- **Status**: Completed - type annotation now matches implementation behavior

### 2. Try-Catch Elimination (1-2 days)  
- **Locations**: 12 try-catch blocks in ViolinPlotter, BasePlotter
- **Change**: Replace with assertion-based validation
- **Why**: Core DR methodology compliance, enables type work

### 3. Constructor Standardization (2-3 days)
- **Locations**: All 8 plotters with inconsistent patterns
- **Change**: Explicit signature pattern with type hints
- **Why**: Required for Phase 2 type system completion

## Success Criteria
- Zero try-catch blocks in validation contexts
- All plotters use identical constructor signature
- Type annotation matches implementation behavior
- All changes maintain existing functionality

## Next Phase Enablement
Foundation establishes fail-fast principle and systematic typing patterns required for Phase 2 Core Architecture improvements.