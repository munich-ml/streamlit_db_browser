import numpy as np
import pandas as pd
import datetime as dt
import json


class JsonEnc(json.JSONEncoder):
    """
    Extends the standard JSONEncoder to support additional datatypes.
    
    Keywords strings as dict keys are used to identify instances of the 
    additional types.
    
    Additional datatype  | keyword
    ---------------------|------------
    pandas DataFrame     | @DataFrame
    pandas Series        | @Series
    numpy array          | @np.array
    datetime.datetime    | @datetime
    datetime.timedelta   | @timedelta
    
    Of course, the regular JSON datatypes are supported, too:
        int, float, str, bool, None, list, (tuple), dict
        
    Example usage:
        # Encode data object to json_str
        json_str = json.dumps(data, cls=JsonEnc)
        
        # Decode json_str to a data object
        data_copy = json.loads(json_str, cls=JsonDec)
        
    """
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return {"@DataFrame": {"columns": list(obj.columns),
                                   "index": list(obj.index),
                                   "data": obj.values.tolist()}}
        
        if isinstance(obj, pd.Series):
            return {"@Series": {"name": obj.name,
                                "index": list(obj.index),
                                "data": obj.values.tolist()}}
        
        if isinstance(obj, np.ndarray):
            return {"@np.array": obj.tolist()}
        
        if isinstance(obj, dt.datetime):
            return {"@datetime": obj.isoformat()}

        if isinstance(obj, dt.timedelta):
            return {"@timedelta": obj.total_seconds()}

        return json.JSONEncoder.default(self, obj)
    
    
class JsonDec(json.JSONDecoder):
    """
    Extends the standard JSONDecoder to support additional datatypes.
    
    Additional types are recognized by dict key keywords, which are injected 
    by the JsonEnc.
    
    Additional datatype  | keyword
    ---------------------|------------
    pandas DataFrame     | @DataFrame
    pandas Series        | @Series
    numpy array          | @np.array
    datetime.datetime    | @datetime
    datetime.timedelta   | @timedelta
    
    Of course, the regular JSON datatypes are supported, too:
        int, float, str, bool, None, list, (tuple), dict
        
    Example usage:
        # Encode data object to json_str
        json_str = json.dumps(data, cls=JsonEnc)
        
        # Decode json_str to a data object
        data_copy = json.loads(json_str, cls=JsonDec)
        
    """
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=JsonDec.custom_hook, *args, **kwargs)
    
    @staticmethod
    def custom_hook(dct):
        if len(dct) == 1:  # add. datatypes are coded in dict of len=1
            if "@np.array" in dct:
                return np.array(dct["@np.array"])
            
            if "@DataFrame" in dct:
                return pd.DataFrame(data=dct["@DataFrame"]["data"],
                                    columns=dct["@DataFrame"]["columns"],
                                    index=dct["@DataFrame"]["index"])
            
            if "@Series" in dct:
                return pd.Series(data=dct["@Series"]["data"],
                                 name=dct["@Series"]["name"],
                                 index=dct["@Series"]["index"])
            
            if "@datetime" in dct:
                return dt.datetime.fromisoformat(dct["@datetime"])
            
            if "@timedelta" in dct:
                return dt.timedelta(seconds=dct["@timedelta"])
            
        return dct    