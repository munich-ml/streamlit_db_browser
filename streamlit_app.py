import json, os
import pandas as pd
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from json_encoder_decoder import JsonEnc, JsonDec
from dataclasses import dataclass, field, asdict
from ruamel.yaml import YAML
from influxdb import InfluxDBClient
    
    
@dataclass
class Trace:
    """Entity time series (xs and ys) with meta data (name, unit,...)
    """
    entity: str
    unit: str
    name: str = ""
    line_mode: str = "lines"
    is_cumsum: bool = False
    is_diff: bool = False
    xs: list = field(default_factory=list, compare=False, hash=False, repr=False)
    ys: list = field(default_factory=list, compare=False, hash=False, repr=False)
    
    def get_label(self) -> str:
        """Returns a trace label like 'garden temperature (°C)'
        """
        label = self.name if self.name else self.entity
        
        if self.is_cumsum:
            label += ".cumsum"
        if self.is_diff:
            label += ".diff"

        return label + f" ({self.unit})"
    

class TracesHandler():
    def __init__(self) -> None:
        if "traces" not in st.session_state:
            st.session_state["traces"] = list()
    
    @staticmethod
    def json_dumps() -> str:
        pass
    
    @staticmethod
    def json_loads(json_str) -> None:
        pass
    
    @staticmethod
    def get_traces_names() -> list:
        names = list()
        for idx, trace in enumerate(st.session_state.traces):
            names.append(f"{idx}. {trace.get_label()}")
        return names
        
    @staticmethod
    def add_trace(df: pd.DataFrame) -> None:
        if len(df):    
            trace = Trace(entity=st.session_state["sel_entity_id"], unit=selected_unit,
                          xs=df.values[:, 0], ys=df.values[:, 1])
            st.session_state.traces.append(trace)
    
    @staticmethod
    def get_traces_figures() -> list:
        """Returns a list of plotly figures sorted by the traces unit
        """
        units = set()
        for trace in st.session_state.traces:
            units.add(trace.unit)
        
        figures = list()
        for unit in sorted(units):
            fig = go.Figure()
            for idx, trace in enumerate(st.session_state.traces):
                if trace.unit == unit:
                    name = f"{idx}. {trace.get_label()}"
                    fig.add_trace(go.Scatter(x=trace.xs, y=trace.ys, mode=trace.line_mode, 
                                                showlegend=True, name=name))
            fig.update_layout(yaxis_title=unit)
            figures.append(fig)
        return figures
            
    @staticmethod
    def del_trace(idx: int) -> None:
        """Change the name of the trace with the index idx
        """
        try:
            st.session_state.traces.pop(idx)
        except IndexError:
            pass
        
        
    @staticmethod
    def load_traces_from_json() -> None:
        pass
    
    
    @staticmethod
    def get_traces_as_json() -> str:
        traces = [asdict(trace) for trace in st.session_state.traces]
        obj = {"type": "Streamlit database browser traces file",
               "version": 1,
               "content": traces}
        
        return json.dumps(obj, cls=JsonEnc)    
    

if __name__ == "__main__":
    
    traces_handler = TracesHandler()

    # streamlit app start
    st.header("Database explorer", divider="red")

    with open("secrets.yaml", "r") as file:
        secrets = YAML().load(file)
        host = secrets["influx"]["host"]
        port = secrets["influx"]["port"]

    try:
        ############################################################################################
        st.subheader("Select a database", divider="blue")
        st.write(f"Connecting to InfluxDB at {host}, {port=}")
        client = InfluxDBClient(host=host, port=port, 
                                username=secrets["influx"]["username"], 
                                password=secrets["influx"]["password"])

        databases = sorted([item["name"] for item in client.get_list_database()], reverse=True)

        database = st.selectbox('database', databases)

        client.switch_database(database)

        # create dataframe of entities
        records = list()
        for point in ["unit=" + p["key"].replace("\\", "") for p in client.query("show series").get_points()]:
            # point example: unit=kWh,domain=sensor,entity_id=sma_battery_charge_total
            record = dict()
            for item in point.split(","):
                key, value = item.split("=")
                record[key] = value
            records.append(record)
        entities = pd.DataFrame.from_records(records)

        st.subheader(f"Available entities", divider="blue")
        with st.expander(f"There are {len(entities)} entities available in {database}"):
            st.dataframe(entities, height=200)

        ############################################################################################
        # Query entities
        st.subheader(f"Query entities", divider="blue")
        unit_col, entity_col = st.columns([1, 2])

        unit = unit_col.selectbox("unit", ["'all units'"] + list(entities["unit"].unique()))
        if unit == "'all units'":
            entity_ids = entities["entity_id"]
        else:
            entity_ids = entities[entities["unit"] == unit]["entity_id"]

        entity_col.selectbox("entity_id", entity_ids, key="sel_entity_id")      
            
        if "start_date" not in st.session_state:
            st.session_state["start_date"] = dt.datetime.now().date() - dt.timedelta(days=365)
        
        if "stop_date" not in st.session_state:
            st.session_state["stop_date"] = dt.datetime.now().date() + dt.timedelta(days=1)
            
        for key in ("start_time", "stop_time"):
            if key not in st.session_state:
                st.session_state[key] = dt.time(0)
        
        def set_one_year():
            st.session_state.start_date = st.session_state.stop_date - dt.timedelta(days=365)
            
        def set_one_month():
            st.session_state.start_date = st.session_state.stop_date - dt.timedelta(days=30)
            
        def set_one_week():
            st.session_state.start_date = st.session_state.stop_date - dt.timedelta(days=7)
            
        def set_one_day():
            st.session_state.start_date = st.session_state.stop_date - dt.timedelta(days=1)
                
        cols = st.columns([3, 3, 1, 1, 1, 1, 3, 3])
        cols[0].date_input("start date", key="start_date")
        cols[1].time_input("start time", key="start_time")
        cols[2].button("1Y", on_click=set_one_year, help="set start date one year before stop date")
        cols[3].button("1M", on_click=set_one_month, help="set start date one month before stop date")
        cols[4].button("1W", on_click=set_one_week, help="set start date one week before stop date")
        cols[5].button("1D", on_click=set_one_day, help="set start date one day before stop date")
        cols[6].date_input("stop date", key="stop_date")
        cols[7].time_input("stop time", key="stop_time")    
        
        # build query string
        RFC3339_FORMAT = '%Y-%m-%dT%H:%M:%S.00000000Z'
        start_string = dt.datetime.combine(st.session_state["start_date"], st.session_state["start_time"]).strftime(RFC3339_FORMAT)
        stop_string = dt.datetime.combine(st.session_state["stop_date"], st.session_state["stop_time"]).strftime(RFC3339_FORMAT)
        
        selected_unit = next(iter(entities[entities["entity_id"] == st.session_state["sel_entity_id"]]["unit"]))
        qstr = f"""SELECT mean_value FROM "{selected_unit}" WHERE entity_id = '{st.session_state["sel_entity_id"]}' 
                AND time >= '{start_string}'
                AND time < '{stop_string}'"""
        st.code(qstr, language="sql")    
        
        # query the data
        df = pd.DataFrame.from_records(client.query(qstr).get_points())
        if len(df):
            df.columns = ["time", st.session_state["sel_entity_id"]]
            if st.button("add to traces"):
                    traces_handler.add_trace(df)        
            
        ############################################################################################
        # Preview data
        if len(df):
            with st.expander(f"Preview {len(df)} points of data"):
                list_col, plot_col = st.columns(2)
                list_col.dataframe(df.set_index("time").head(8))
                plot_col.scatter_chart(df.set_index("time"))

        ############################################################################################
        # Edit traces
        st.subheader("Edit traces", divider="blue")        
        
        ecol1, ecol2 = st.columns(2)
        
        sel_trace_str = ecol1.selectbox("select trace for editing", 
                                            traces_handler.get_traces_names())
        if sel_trace_str is not None:
            sel_trace_idx = int(sel_trace_str.split(".")[0])
            sel_trace = st.session_state.traces[sel_trace_idx]
            st.session_state.sel_trace_name = sel_trace.name
            def edit_trace_name():
                sel_trace.name = st.session_state.sel_trace_name
            
            ecol2.text_input("edit trace name", key="sel_trace_name", on_change=edit_trace_name)
            
            st.session_state.line_mode = sel_trace.line_mode
            def edit_line_mode():
                sel_trace.line_mode = st.session_state.line_mode
            
            line_modes = {'lines': 0, 'markers': 1, 'lines+markers': 2}
            ecol2.selectbox("line mode", options=line_modes.keys(), key="line_mode", 
                            index=line_modes[sel_trace.line_mode],
                            on_change=edit_line_mode)
            
            dcol1, dcol2 = ecol2.columns(2)
            if dcol1.button("delete selected trace", type="primary"):
                traces_handler.del_trace(sel_trace_idx)
                st.rerun()
            if dcol2.button("delete all traces", type="primary"):
                st.session_state["traces"] = list()

        ############################################################################################
        # View traces plots
        st.subheader("View traces plots", divider="blue")
        
        if upload_obj := st.file_uploader(label="upload traces", type="json", accept_multiple_files=False):
            trace_dict_list = json.load(upload_obj, cls=JsonDec)["content"]
            try:
                for trace_dict in trace_dict_list:
                    trace = Trace(**trace_dict)
                    st.session_state.traces.append(trace)
            except Exception as e:
                st.error(f"Exception {e} while appending {trace=}!")
                
        for fig in traces_handler.get_traces_figures():
            st.plotly_chart(fig, use_container_width=True)
        
        st.download_button("download traces", data=traces_handler.get_traces_as_json(), 
                        file_name="traces.json")
        
        ############################################################################################
        # Inside streamlit_db_browser
        st.subheader(f"Inside streamlit_db_browser", divider="blue")
        "session_state:", st.session_state


    except (Exception, KeyboardInterrupt) as error:
        print(f"{error=}")
        client.close()
