import pandas as pd
import datetime as dt
import streamlit as st
from ruamel.yaml import YAML
from influxdb import InfluxDBClient
    

st.header("Database explorer", divider="green")

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
    for point in ["unit=" + p["key"] for p in client.query("show series").get_points()]:
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
    
    cols = st.columns([3, 2, 3, 2])
    cols[0].date_input("start date", key="start_date")
    cols[1].time_input("start time", key="start_time")
    cols[2].date_input("stop date", key="stop_date")
    cols[3].time_input("stop time", key="stop_time")
    
    # build query string
    RFC3339_FORMAT = '%Y-%m-%dT%H:%M:%S.00000000Z'
    start_string = dt.datetime.combine(st.session_state["start_date"], st.session_state["start_time"]).strftime(RFC3339_FORMAT)
    stop_string = dt.datetime.combine(st.session_state["stop_date"], st.session_state["stop_time"]).strftime(RFC3339_FORMAT)
    
    selected_unit = next(iter(entities[entities["entity_id"] == st.session_state["selected_entity_id"]]["unit"]))
    qstr = f"""SELECT mean_value FROM "{selected_unit}" WHERE entity_id = '{st.session_state["selected_entity_id"]}' 
               AND time >= '{start_string}'
               AND time < '{stop_string}'"""
    st.code(qstr, language="sql")    
    st.divider()

    # query the data
    df = pd.DataFrame.from_records(client.query(qstr).get_points()).set_index("time")
    df.columns = [st.session_state["selected_entity_id"]]
    
    # preview data
    st.scatter_chart(df)
    
    st.dataframe(df.tail(5))
    
    st.divider()

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
