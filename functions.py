import streamlit as st
import datetime as DT
import pandas as pd



def gsc_data_work(df, site_url, days_selector, days_ago):
    try:
        #df = webproperty.query.search_type(search_type).range('today',days=days_ago).dimension('date', 'page').get().to_dataframe()
        df['date'] = pd.to_datetime(df['date']) # Convert date format
        df['clicks'] = pd.to_numeric(df['clicks'], downcast="integer")
        df['ctr'] = pd.to_numeric(df['ctr'], downcast="float")


        ########## INTRO MESSAGE BEGIN ############
        today = DT.date.today()

        start_date = today - DT.timedelta(days=days_selector)
        st.caption(f'You selected Google Discover Data for {site_url} from {start_date} to {today}.')

        ########## INTRO MESSAGE END ############

        return df

    except AttributeError:
        st.error("Check please your property URL, don't forget https://, www, the trailing slash if necessary.")

    if not site_url and refresh_button:
        st.error('Please enter the correct property URL exactly as in your Search Console.')