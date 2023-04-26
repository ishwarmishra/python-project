import streamlit as st
import streamlit

def set_streamlit_page_config_once():
    try:
        streamlit.set_page_config(layout="wide")
    except streamlit.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            # ignore this error
            return
        raise e
set_streamlit_page_config_once()
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.graph_objects as go

def connection():
    password = "ishwarmishra"
    engine = create_engine(f'mysql+pymysql://root:{password}@localhost:3306/anpr')
    return engine

engine = connection()

def plot(x,y):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y,text=y))
    return fig

st.markdown("# Dashboard")
st.sidebar.markdown("# Dashboard")



query = 'SELECT * from anpr.car_check_in order by user_id desc;'
query_user_reg = 'SELECT * from anpr.user_registation order by user_id desc;'
with engine.begin() as conn:
    df = pd.read_sql_query(sql=text(query), con=conn)  
    df_user = pd.read_sql_query(sql=text(query_user_reg), con=conn)  

df['user_id'] = df['user_id'].astype(int) 
df_user['user_id'] = df_user['user_id'].astype(int) 

daily_agg_df = df.groupby([pd.Grouper(key='check_in',freq="1D")]).agg(count=("user_id","count"),amount=("amount","sum")).reset_index()
daily_agg_df.sort_values("check_in",inplace=True,ascending=False)
daily_agg_df.reset_index(drop=True,inplace=True)

vehicle_entry_field, total_amount_field,total_user_registered = st.columns( [0.4, 0.4,0.2])
with vehicle_entry_field:
    total_count = df['user_id'].count()
    st.subheader("Total Vehicle Entry")
    st.write(total_count)


with total_amount_field:
    total_amount = df['amount'].sum()    
    st.subheader("Total Amount Earned")
    st.write(total_amount)

with total_user_registered:
    user_reg_count = df_user['user_id'].count()
    st.subheader("Total User Registration")
    st.write(user_reg_count)


total_check_in, total_user_reg = st.columns([0.5,0.5])
with total_check_in:
    df_home = df.head(20)
    st.write("Latest Vehicle Entry:")
    df_home.set_index("user_id",inplace=True)
    st.dataframe(df_home)
with total_user_reg:
    st.write("Latest User Registration:")
    df_user = df_user.head(20)
    df_user.set_index("user_id",inplace=True)
    st.dataframe(df_user)


st.subheader("Vechile Entry Distribution")
count_plot = plot(daily_agg_df['check_in'],daily_agg_df['count'])
st.plotly_chart(count_plot, theme=None, use_container_width=True)

st.subheader("Amount Distibution")
amt_plot = plot(daily_agg_df['check_in'],daily_agg_df['amount'])
st.plotly_chart(amt_plot, theme=None, use_container_width=True)
