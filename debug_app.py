
import pandas as pd
import datetime as dt
from streamlit_app import JsonDec, JsonEnc
import json, os
import pandas as pd
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass, field, asdict


@dataclass
class TimeSignal:
    entity: str
    unit: str
    line_mode: str = "lines"
    series: pd.Series = field(default_factory=pd.Series, compare=False, hash=False, repr=False)
    
with open("ts1.json", "r") as file:
    ts_dict = json.load(file, cls=JsonDec)
    
ts = TimeSignal(**ts_dict)

st.write("debug app")
st.dataframe(ts.series)
fig = go.Figure()
fig.add_trace(go.Scatter(x=ts.series.index, y=ts.series.values, mode=ts.line_mode, 
                            showlegend=True, name=ts.series.name))
fig.update_layout(yaxis_title=ts.unit)
st.plotly_chart(fig, use_container_width=True)
