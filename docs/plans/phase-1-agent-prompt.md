# Phase 1 Agent Prompt: Data Exploration Script

## Your Mission
You are implementing Phase 1 of a faceted plotting system. Create a comprehensive data exploration script at `scripts/explore_mean_eval_data.py` that systematically analyzes the structure of `data/mean_eval.parquet`.

## Context
This is part of a larger project to build faceted plotting capabilities. The dataset contains training metrics that vary across multiple dimensions:
- Model sizes (params column)  
- Data recipes (data column)
- Multiple metrics (various metric columns)
- Training timesteps (steps column)

The goal is to create a 2-row × N-column grid visualization where rows represent different metrics, columns represent data recipes, and each subplot contains multiple lines (one per model size).

## Required Script Structure

Create `scripts/explore_mean_eval_data.py` with exactly these functions:

```python
def load_parquet_data() -> pd.DataFrame:
    # Load data/mean_eval.parquet and return as DataFrame
    
def validate_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
    # Validate expected columns exist, check data types
    # Return validation results including any issues found
    
def extract_available_metrics(df: pd.DataFrame) -> List[str]:
    # Extract all unique metric names from the dataset
    
def extract_data_recipes(df: pd.DataFrame) -> List[str]:
    # Extract all unique data recipe names from the dataset
    
def extract_model_sizes(df: pd.DataFrame) -> List[str]:
    # Extract all unique model parameter sizes from the dataset
    
def analyze_data_completeness(df: pd.DataFrame) -> Dict[str, Any]:
    # Analyze missing combinations across dimensions
    # Check for sparse data patterns that might affect plotting
    
def main():
    # Orchestrate all functions and print comprehensive results
```

## Code Requirements

**CRITICAL - Follow Project Standards**:
1. **No comments or docstrings anywhere** - code must be self-documenting
2. **Comprehensive type hints** on ALL functions (parameters and return values)
3. **All imports at the very top** of the file
4. **Use assertions for validation**: `assert condition, "message"` instead of exceptions
5. **Remove any existing comments** when editing files

**Import Requirements**:
```python
from typing import Any, Dict, List
import pandas as pd
# Add other imports as needed
```

**Function Signature Examples**:
```python
def load_parquet_data() -> pd.DataFrame:
def validate_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
def extract_available_metrics(df: pd.DataFrame) -> List[str]:
```

## Expected Output
When someone runs `uv run python scripts/explore_mean_eval_data.py`, they should see:

1. **Data Structure Validation Results**
   - Confirmation that expected columns exist
   - Data types and basic structure info
   - Any validation warnings or issues

2. **Available Dimensions**
   - Complete list of available metrics
   - Complete list of data recipes  
   - Complete list of model sizes
   - Counts for each dimension

3. **Data Completeness Analysis**
   - Missing combinations across dimensions
   - Sparse data patterns
   - Any gaps that might affect plotting decisions

4. **Summary**
   - Key findings that will inform Phase 2 decisions
   - Any limitations or constraints discovered

## Success Criteria
After running this script, we should have complete understanding of:
- What metrics are available for plotting
- What data recipes we can use for column faceting  
- What model sizes we can use for line styling
- Any missing data combinations that might affect plotting decisions
- Data structure validation confirming our assumptions

## File Structure
Make the script executable:
```python
if __name__ == "__main__":
    main()
```

## Testing
Before submitting, run the script to ensure:
- It loads the data successfully
- All functions execute without errors
- Output is comprehensive and well-formatted
- No syntax or import errors

## Important Notes
- Focus on systematic analysis, not visualization
- This data exploration will inform all subsequent phases
- Be thorough - missing information here will create problems later
- Use clear, descriptive variable names since no comments are allowed