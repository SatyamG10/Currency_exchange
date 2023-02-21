import pandas as pd
import json
import warnings
warnings.filterwarnings(action="ignore")
from urllib.request import urlopen
import streamlit as st
import numpy as np
import requests
try:
    from bs4 import BeautifulSoup
except :
    from BeautifulSoup import BeautifulSoup 
    

source = requests.get("https://www.ups.com/worldshiphelp/WSA/ENG/AppHelp/mergedProjects/CORE/Codes/Country_Territory_and_Currency_Codes.htm").text
soup = BeautifulSoup(source,'html.parser')

body = soup.find('body')

country = []
currency_code = []
symbol = []

for para in body.find_all('tr')[1:]:
    columns = para.find_all('td')
    country.append(columns[0].text.strip())
    currency_code.append(columns[3].text.strip())
    symbol.append(columns[4].text.strip())


currency_df = pd.DataFrame({"Country":country,
                    "Currency_Code":currency_code,
                    "Symbol":symbol})


with urlopen("http://www.floatrates.com/daily/inr.json") as curr_data:
    data = curr_data.read()


Curr_data = json.loads(data)


exchange_rate = []
date = []
alpha_code = []
inverse_rate = []



for data in Curr_data.keys():
    exchange_rate.append(Curr_data[data]["rate"])
    date.append(Curr_data[data]["date"])
    alpha_code.append(Curr_data[data]["alphaCode"])
    inverse_rate.append(Curr_data[data]["inverseRate"])



exchange_df = pd.DataFrame({"Code":alpha_code,
                            "Date":date,
                            "Exchange_rate":exchange_rate,
                            "Inverse_rate":inverse_rate})


last_refreshed_at = exchange_df["Date"].str[5:-4].drop_duplicates()[0]


final_df = pd.merge(currency_df,exchange_df,left_on=["Currency_Code"],right_on=["Code"],how="inner").drop(columns="Date")

curr_df = final_df[['Currency_Code','Exchange_rate']]

curr_df = curr_df.drop_duplicates()

curr_df = curr_df.set_index(np.arange(len(range(0,curr_df.shape[0]))))

st.title("Currency exchange platform")

st.write("Enter the value to be converted")

val = st.number_input("Enter you value")

curr = st.selectbox('Choose your currency',curr_df["Currency_Code"].to_list())

indx = curr_df.index[curr_df["Currency_Code"]==curr].item()

st.write(f"The value in INR is : {val * curr_df.Exchange_rate[indx]}")
