from typing import Any, Dict, List, Set, Tuple, Union

import pandas as pd

type BasePlotterParamName = str
type SubPlotterParamName = str
type VisualChannel = str
type ColName = str
type StyleAttrName = str
type Phase = str
type ComponentSchema = Dict[str, Set[str]]
type ComponentStyles = Dict[str, Dict[str, Any]]
type GroupInfo = Tuple[Any, pd.DataFrame]
type GroupContext = Dict[str, Any]
type ColorPalette = List[str]
type SubplotCoord = Tuple[int, int]
type ChannelName = str
type ExpectedChannels = Dict[SubplotCoord, List[ChannelName]]
type VerificationParams = Dict[str, Any]
type VerificationResult = Dict[str, Any]
type RGBA = Tuple[float, float, float, float]
type RGB = Tuple[float, float, float]
type ColorTuple = Union[RGBA, RGB]
type NumericValue = Union[float, int]
type ComparisonValue = Union[NumericValue, ColorTuple, str]
type Position = Tuple[float, float]
type CollectionProperties = Dict[str, Any]
type StyleCacheKey = Tuple[VisualChannel, Any]
