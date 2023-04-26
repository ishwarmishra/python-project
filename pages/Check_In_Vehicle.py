import streamlit as st
from Home_Page import set_streamlit_page_config_once
set_streamlit_page_config_once()
# from User_Registration import user_reg
import pandas as pd
import time
st.markdown("# Add New Car")
st.sidebar.markdown("# Add New Car")
from  PIL import Image
from time import localtime, strftime
from datetime import datetime,timedelta
from algo import calulate_number_plate
from Home_Page import connection

from sqlalchemy import create_engine, text

engine = connection()

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    st.session_statelabel_visibility='collapse'

def check_in_time():
    checkin_time = datetime.now()
    date_format_i = '%Y-%m-%d, %H:%M'
    check_in_i = checkin_time.strftime("%Y-%m-%d, %H:%M")
    check_in_use = datetime.strptime(check_in_i, "%Y-%m-%d, %H:%M") #datetime datatype
    return check_in_use

charge_list = [20,40,50,100,150,180,200,220,250]
def fare_charge(time_s):
    if time_s <= 0.5:
        charge = charge_list[0]
    elif time_s > 0.5 and time_s <= 1:
        charge = charge_list[1]
    elif time_s > 1 and time_s <= 2:
        charge = charge_list[2]
    elif time_s > 2 and time_s <= 4:
        charge = charge_list[3]
    elif time_s > 4 and time_s <= 6:
        charge = charge_list[4]
    elif time_s > 6 and time_s <= 8:
        charge = charge_list[5]
    elif time_s > 8 and time_s <= 10:
        charge = charge_list[6]  
    elif time_s > 10 and time_s <= 12:
        charge = charge_list[7]  
    elif time_s > 12:
        charge = charge_list[8]    
    return charge

def check_out_time(check_in_use):
    diff_time = [0.5,1,2,4,6,8,10,12]
    amount = []
    check_out_time_list = []
    check_out_time_only = []
    for time_s in diff_time:
        checkout_time = check_in_use + timedelta(hours=time_s)
        time_s = (((checkout_time-check_in_use).seconds)/60)/60
        amount = fare_charge(time_s)
        co_t = str(checkout_time)
        show_in_checkout = (time_s,amount,co_t)
        check_out_time_list.append(show_in_checkout)
        check_out_time_only.append(co_t)

    checkout_s = st.selectbox(
    'When would you like to Checkout?',check_out_time_only)
    position_checkout = check_out_time_only.index(checkout_s)
    for_time = check_out_time_list[position_checkout][0]
    amount = check_out_time_list[position_checkout][1]

    return checkout_s,for_time,amount



def upload_image_file():
    uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'])
    return uploaded_file


uploaded_file = upload_image_file()
number_plate,accuracy = calulate_number_plate(uploaded_file)
##algorithm  call
check_in_use = check_in_time()

if uploaded_file is not None:
    if len(number_plate) == 0:
        st.write("Algo didn't detect number plate, please enter manually number plate")

    elif accuracy<50 and len(number_plate) !=0 :
        st.write(f"Algorithm accuracy is low: {accuracy}%, Algo might not had performed well so might need to change number plate manually")

    else:
        st.write(f"Algorithm accuracy : {accuracy}%")
    number_plates = st.text_input("Algorithm output(number plate)",number_plate)

    # user = user_reg()
    is_registered = st.selectbox("Is registered Already?",("No","Yes"))
    if is_registered == 'No':
        col1, address_field,col2, col3 = st.columns( [0.3,0.2, 0.2,0.3])
        
        with col1:
            default_name = "Unknown"
            car_owner_name = st.text_input(
                "Car Owner Name",
                f"{default_name}",
                key="placeholder",
            )
            if car_owner_name:
                st.write("Your name is: ", car_owner_name)
        with address_field:
            default_name = "Unknown"
            address = st.text_input(
                "Address",
                f"{default_name}",
                key="address",
            )
        with col2:
            st.write("Checkin time")
            st.write(check_in_use)

        with col3:
            diff_time = [0.5,1,2,4,6,8,10,12]
            charge_list = [20,40,50,100,150,180,200,220,250]
            amount = []
            check_out_time_list = []
            check_out_time_only = []
            for time_s in diff_time:
                checkout_time = check_in_use + timedelta(hours=time_s)
                time_s = (((checkout_time-check_in_use).seconds)/60)/60
                amount = fare_charge(time_s)
                co_t = str(checkout_time)
                show_in_checkout = (time_s,amount,co_t)
                check_out_time_list.append(show_in_checkout)
                check_out_time_only.append(co_t)

            checkout_s = st.selectbox(
            'When would you like to Checkout?',check_out_time_only)
            position_checkout = check_out_time_only.index(checkout_s)
            for_time = check_out_time_list[position_checkout][0]
            amount = check_out_time_list[position_checkout][1]

            st.write(f'Checkout time selected: {checkout_s} and Amount : Rs {amount}')
            st.write(f'Total time to be parked: {for_time} hr')

        result = []

        if len(number_plate) == 0:
            st.write("Please Enter number plate and process further")
        if len(car_owner_name) == 0:
            car_owner_name = default_name

        car_owner_name = str(car_owner_name)
        number_plate_s = str(number_plates)
        result.append([number_plate_s,check_in_use,checkout_s,amount,car_owner_name,address])

        query_r = "SELECT * from anpr.car_check_in order by user_id desc limit 1"
        if st.button('Create Entry'):
            df = pd.DataFrame(result,columns=["vehicle_number","check_in","check_out","amount","vehicle_owner_name","address"])
            df.to_sql("car_check_in",schema='anpr',index=False,if_exists='append', con=engine)
            time.sleep(2)
            st.write("Entry Sucessfully created")
            time.sleep(2)

            entered_df = pd.DataFrame(engine.connect().execute(text(query_r)))
            st.dataframe(entered_df)

    else:
        provided_user_id = st.text_input("Please enter user id")
        print(provided_user_id)
        if provided_user_id:
            query = f'SELECT * from anpr.user_registation where user_id = {int(provided_user_id)};'
            with engine.begin() as conn:
                df = pd.read_sql_query(sql=text(query), con=conn)  
            if len(df.dropna()) == 0:
                st.write(f"User id : {provided_user_id} doesn't found.")
            else:
                st.write("User registration found, changing parking status to 1")
                df['vehicle_number'] = str(number_plates)
                st.dataframe(df)
                df.drop(columns=['user_id','created_on'],inplace=True)

                df.to_sql("car_check_in",schema='anpr',index=False,if_exists='append', con=engine)

                new_user_reg = pd.DataFrame(engine.connect().execute(text(f"SELECT * FROM anpr.car_check_in where user_reg_id = '{df['user_reg_id'].iloc[0]}'")))
                
                st.dataframe(new_user_reg)
                st.write("Successfully checked in")


