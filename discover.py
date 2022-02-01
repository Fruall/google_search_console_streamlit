import streamlit as st
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import FlowExchangeError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
st.set_page_config(layout="wide")
import datetime as DT
import pandas as pd
import json
import httplib2
import searchconsole
from pathlib import Path
from functions import gsc_data_work



########################## CONFIGURATION ##########################

client_config ='client_secret_22068898197-ekqrfbiun76idmt0qiotqqimbkq1cedg.apps.googleusercontent.com.json'

# Copy your credentials from the console
CLIENT_ID = '22068898197-ekqrfbiun76idmt0qiotqqimbkq1cedg.apps.googleusercontent.com'
CLIENT_SECRET = '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'
CREDENTIALS_FILE = 'client_secret_22068898197-ad6auvrhljrc2mngu89v5ctr5iht6o04.apps.googleusercontent.com.json'

# Check https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()

code = None
df = None
credentials = ""

stored_credentials = Path("saved_credentials.json")
#if st.button('Proceed to Oauth'):




########################## CONFIGURATION ##########################

def refresh_data(days_ago):
    with open('saved_credentials.json', 'r') as f:
        credentials = json.load(f)

        loads = json.loads(credentials)  # for Json string

        new_json = {
            'token': loads['access_token'],
            'refresh_token': loads['refresh_token'],
            'id_token': loads['id_token'],
            'token_uri': loads['token_info_uri'],
            'client_id': loads['client_id'],
            'client_secret': loads['client_secret'],
            'scopes': loads['scopes']
        }

    with open('credentials.json', 'w') as f:
        json.dump(new_json, f)

    account = searchconsole.authenticate(
        client_config='client_secret_22068898197-ad6auvrhljrc2mngu89v5ctr5iht6o04.apps.googleusercontent.com.json',
        credentials='credentials.json')

    if account:
        status_connect = st.sidebar.caption('✔️Google Account connected.')
        try:
            webproperty = account[site_url]
            df = webproperty.query.search_type('discover').range('today', days=days_ago).dimension('date',
                                                                                               'page').get().to_dataframe()
        except AttributeError:
            st.warning('Your Google Search Console account did not return any data. Please check your property URL.')
            st.stop()
        #st.dataframe(df)

    return df


def first_data(code, site_url, days):

    code = str(code).strip()
    credentials = flow.step2_exchange(code)
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    # http = credentials.authorize(http)
    http = credentials.authorize(http)

    #status_connected = st.sidebar.write ("Connected to your Google Account")

    with open('saved_credentials.json', 'w') as sc:
        json.dump(credentials.to_json(), sc)
        #status_connected = st.write('Your credentials have been saved.')
        #st.write(credentials.to_json())

    webmasters_service = build('searchconsole', 'v1', http=http)

    # Start and end date
    today = DT.date.today()
    start_date = today - DT.timedelta(days=days)

    payload = {
        'startDate': str(start_date),
        'endDate': str(today),
        'dimensions': ["date", "page"],
        'type': 'discover'
    }
    try:
        response2 = webmasters_service.searchanalytics().query(siteUrl=site_url, body=payload).execute()
    except HttpError as e:
        st.warning('Please check your property URL. It must be exactly the same as in your Google Search Console Account (https://, www, trailing slash etc. If you have a domain-level website in your Google Search Console, please add "sc-domain:" before your domain name.")')
        st.stop()
    except AttributeError as ex:
        st.warning('Your Google Search Console does not return any data. Please check your property URL.)')
        st.stop()


    results = []

    for row in response2['rows']:
        data = {}

        for i in range(len(payload['dimensions'])):
            data[payload['dimensions'][i]] = row['keys'][i]

        data['clicks'] = row['clicks']
        data['impressions'] = row['impressions']
        data['ctr'] = row['ctr']
        results.append(data)

    df = pd.DataFrame.from_dict(results)

    st.table(df.sort_values(by='date', ascending=True))

    return df





########################## HEADER ##########################

col1, col2 = st.columns([1, 30])
with col1:
    st.image('google-discover.png', width=40)
with col2:
    st.title('Google Discover from Search Console')

########################## HEADER END ##########################





########################## SIDEBAR ##########################

setup = st.sidebar.header('Setup')


sign_in = f"<a href='https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=22068898197-ekqrfbiun76idmt0qiotqqimbkq1cedg.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fwebmasters.readonly&state=xFMMQpeW7P7v2m8MwxlYBNgBibmXti&prompt=consent&access_type=offline' target='_blank'>Sign in in your Google Account</a>"
st.sidebar.markdown(sign_in, unsafe_allow_html=True)
code = st.sidebar.text_input('1. Enter verification code: ')
site_url = st.sidebar.text_input('2. Enter your property url : ')

days_selector = st.sidebar.select_slider('How many days to analyze :', options=[*range(1, 366, 1)])
days_ago = -3 - days_selector

first_data_button = st.sidebar.button('🔑 Connect', key='first_data_button', help='Please, use the button "Connect" only once to get the first data.')
refresh_data_button = st.sidebar.button('🔄 Refresh Data', key='refresh_data_button', help='Use this button for the manipulations with the date (for example by changing days count).')

########################## SIDEBAR END ##########################






########################## BODY RESULTS #####################

if code and site_url and first_data_button:
    try:
        df = first_data(code, site_url, days_selector) # Connect and get first data
        #st.table(df)
    except FlowExchangeError:
        st.error('Please, use the button "Connect" only once to get the first data. For all the other manipulations, use the button "Refresh Data".')
        st.stop()

if site_url and refresh_data_button:
    df = refresh_data(days_ago) # Reconnects
    st.table(df)

if df is not None:
    gsc_data_work(df, site_url, days_selector, days_ago)

if df is not None:

    #GROUPBY PAGES
    df_by_page = df.groupby(by='page', as_index=False).agg({'impressions': 'sum', 'clicks': 'sum', 'ctr': 'mean'})
    #GROUPBY PAGES


########################## BODY RESULTS END ######################