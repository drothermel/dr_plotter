from typing import Dict, List, Tuple, Any, NamedTuple
import pandas as pd


class GridLayout(NamedTuple):
    rows: int
    cols: int
    row_values: List[str]
    col_values: List[str]
    grid_type: str
    metadata: Dict[str, Any]


type SubplotPosition = Tuple[int, int]
type DataSubsets = Dict[SubplotPosition, pd.DataFrame]
