import pandas as pd
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass, field
from ruamel.yaml import YAML
from influxdb import InfluxDBClient
    
    
@dataclass
class Trace:
    """Entity time series (xs and ys) with meta data (name, unit,...)
    """
    entity: str
    unit: str
    name: str = ""
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
            if trace.name:
                name = trace.name
            else:
                name = trace.entity
            names.append(f"{idx}. {name}")
        return names
        
    @staticmethod
    def add_trace(df: pd.DataFrame) -> None:
        if len(df):    
            trace = Trace(entity=st.session_state["selected_entity_id"], unit=selected_unit,
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
            for trace in st.session_state.traces:
                if trace.unit == unit:
                    fig.add_trace(go.Scatter(x=trace.xs, y=trace.ys, mode='lines', 
                                                showlegend=True, name=trace.entity))
            fig.update_layout(yaxis_title=unit)
            figures.append(fig)
        return figures
            
    @staticmethod
    def change_name(idx: int, name) -> None:
        """Change the name of the trace with the index idx
        """
        pass
    

traces_handler = TracesHandler()

# streamlit app start
st.header("Database explorer", divider="red")

with open("secrets.yaml", "r") as file:
    secrets = YAML().load(file)
    host = secrets["influx"]["host"]
    port = secrets["influx"]["port"]

try:
    st.subheader("Database connection", divider="blue")
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
    st.write(f"There are {len(entities)} entities available in {database}:")
    st.dataframe(entities, height=200)

    # Query
    st.subheader(f"Query", divider="blue")
    unit_col, entity_col = st.columns([1, 2])

    unit = unit_col.selectbox("unit", ["'all units'"] + list(entities["unit"].unique()))
    if unit == "'all units'":
        entity_ids = entities["entity_id"]
    else:
        entity_ids = entities[entities["unit"] == unit]["entity_id"]

    entity_col.selectbox("entity_id", entity_ids, key="selected_entity_id")      
        
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
    
    selected_unit = next(iter(entities[entities["entity_id"] == st.session_state["selected_entity_id"]]["unit"]))
    qstr = f"""SELECT mean_value FROM "{selected_unit}" WHERE entity_id = '{st.session_state["selected_entity_id"]}' 
               AND time >= '{start_string}'
               AND time < '{stop_string}'"""
    st.code(qstr, language="sql")    
    
    # query the data
    df = pd.DataFrame.from_records(client.query(qstr).get_points())
    if len(df):
        df.columns = ["time", st.session_state["selected_entity_id"]]
    
    # preview data
    list_col, plot_col = st.columns(2)
    if len(df):
        list_col.write(f"Preview {len(df)} points")
        list_col.dataframe(df.set_index("time").head())
        plot_col.scatter_chart(df.set_index("time"))
    else:
        list_col.write("Empty, nothing to preview!")

    # traces
    st.subheader("Traces", divider="blue")
        
    if st.button("add this trace"):
        traces_handler.add_trace(df)        

    if st.button("delete all traces", type="primary"):
        st.session_state["traces"] = list()
    
    selected_trace = st.selectbox("traces", traces_handler.get_traces_names())
    
    # plot
    for fig in traces_handler.get_traces_figures():
        st.plotly_chart(fig, use_container_width=True)
    
       
    st.subheader(f"Inside streamlit_db_browser", divider="blue")
    "session_state:", st.session_state




    # df = pd.read_excel("example_data.xlsx")
    # st.markdown("""
    #             # Enjoy this great dashboard
    #             showing lots of data
    #             """)
    # st.write(df)
    # 
    # fig = plt.figure(figsize=(12, 3))
    # ax = fig.add_subplot(111)
    # df["diff"] = df["mean_value"].diff()
    # ax.plot(df.index, df["diff"], ".");
    # st.write(fig)

except (Exception, KeyboardInterrupt) as error:
    print(f"{error=}")
    client.close()
