import streamlit as st
from Home_Page import set_streamlit_page_config_once
set_streamlit_page_config_once()
from pages.Check_In_Vehicle import check_in_time,fare_charge,check_out_time
from datetime import datetime
import time
from Home_Page import connection
engine = connection()
import secrets
from sqlalchemy import text

st.markdown("# User Registration")
st.sidebar.markdown("# User Registration")
import pandas as pd
check_in_use = check_in_time()
user_reg_data = []
charge_list = [20,40,50,100,150,180,200,220,250]
def user_reg():
        user_name_field, address_field, check_in_field, check_out_field = st.columns( [0.2, 0.3,0.3,0.2])
        with user_name_field:
            user_name = st.text_input(
                "Name",
                key="name",
            )
            if user_name:
                st.write("Your name is: ", user_name)
        
        with address_field:
            default_name = "Unknown"
            address = st.text_input(
                "Address",
                f"{default_name}",
                key="address",
            )
        with check_in_field:
            # st.write("To Be Checked In time")
            to_be_checked_in = st.text_input(
                "Checked in time (YYYY-MM-DD HH:MM:00)",
                key="checkin",
            )
            status = 0
            if to_be_checked_in:
                try: 
                    if len(to_be_checked_in) > 16:
                        to_be_checked_in=to_be_checked_in[:-3]
                    check_in = datetime.strptime(to_be_checked_in, "%Y-%m-%d %H:%M")
                    status = 1
                except ValueError:
                    st.write("dateformat not matched, please provide dateformat in this format: YYYY-MM-DD HH:MM:SS (SS second is optional)")
                st.write(to_be_checked_in)
        with check_out_field:
            if to_be_checked_in and status==1:
                checkout_s,for_time,amount = check_out_time(check_in)

                st.write(f'Checkout time selected: {checkout_s} and Amount : Rs {amount}')
                st.write(f'Total time to be parked: {for_time} hr')   
        vechile_number = 'NaN'
        if len(address) == 0:
            address = default_name

        query_r =  "SELECT * from anpr.user_registation order by user_id desc limit 1"
        if st.button('Click for parking reservation'):
            user_reg_data.append([vechile_number,user_name,to_be_checked_in,checkout_s,amount,address,check_in_use])
            print(user_reg_data)
            df_user_data = pd.DataFrame(user_reg_data,columns=["vehicle_number","vehicle_owner_name","check_in","check_out","amount","address","created_on"])
            df_user_data['user_reg_id'] = secrets.token_hex(2) +  datetime.strftime(datetime.now(),"_%Y_%m_%d_%H_%M_%S")
            df_user_data.to_sql("user_registation",schema='anpr',index=False,if_exists='append', con=engine)

            time.sleep(2)
            st.write("Entry Sucessfully created")
            time.sleep(2)

            new_user_reg = pd.DataFrame(engine.connect().execute(text(query_r)))
            
            st.dataframe(new_user_reg)

                
user_reg()
