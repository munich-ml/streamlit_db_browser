"""Module providing transformer function for time series data (pandas.Series with datetime index)
"""

import pandas as pd
import datetime as dt
import inspect
from typing import Callable

class SignalTransformers():
    """
    Namespace of the transformer functions with a common interface:
    input_series and output series of type pandas.Series with datetime index
    """
    @staticmethod
    def diff(input_series: pd.Series) -> pd.Series:
        """Differentiate
        """
        output_series = input_series.diff()
        output_series.name += ".diff"
        return output_series
    
    @staticmethod
    def cumsum(input_series: pd.Series) -> pd.Series:
        """Cumulative sum
        """
        output_series = input_series.cumsum()
        output_series.name += ".cumsum"
        return output_series
    
    @staticmethod
    def resample(input_series: pd.Series, interval_days: float = 1.0, agg_sum: bool = False, fill_na: bool = False) -> pd.Series:
        """Resample to a given interval
        """
        resampler = input_series.resample(dt.timedelta(days=interval_days))
        if interval_days.is_integer():
            name_adder = f".res{int(interval_days)}d_"
        else:
            interval_hours = interval_days * 24
            if interval_hours.is_integer():
                name_adder = f".res{int(interval_hours)}h_"
            else:
                name_adder = f".res{interval_hours}h_"   
                
        if agg_sum:
            output_series = resampler.sum()
            output_series.name += name_adder + "sum"
        if fill_na:
            output_series =  resampler.mean().ffill()
            output_series.name += name_adder + "mean_fill"
        else:
            output_series =  resampler.mean()
            output_series.name += name_adder + "mean"
        return output_series
    
    
class SignalTransformersInterface():
    """Interface to the SignalTransformers
    """
    def __init__(self) -> None:
        self._transformers = SignalTransformers()
        
    def get_transformers_names(self) -> list:
        return [name for name in dir(self._transformers) if not name.startswith("_")]
    
    def get_transformer(self, transformer_name: str) -> Callable:
        return getattr(self._transformers, transformer_name)
    
    def get_transformer_parameters(self, transformer_name: str) -> list[tuple[str, type]]:
        transformer = self.get_transformer(transformer_name)
        params = list()
        for param in inspect.signature(transformer).parameters.values():
            if param.name != "input_series":
                default = None
                empty = param.default == param.empty
                if not empty:
                    default = param.default 
                params.append((param.name, param.annotation, default))
        return params
    
    
if __name__ == "__main__":  
    tfi = SignalTransformersInterface()
    print("Available transformers in SignalTransformer:")
    for transformer_name in tfi.get_transformers_names():
        print(f"{transformer_name=}")
        for param in tfi.get_transformer_parameters(transformer_name):
            print("-", param)