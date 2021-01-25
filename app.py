import base64
import streamlit as st
import pandas as pd
import json
import urllib.request
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
def download_link(object_to_download, filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()
    download_filename=filename+'.csv'
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

@st.cache
def plot_snapshot_numbers(df, colors):
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df[["confirmed", "deaths", "recovered", "active"]].columns.tolist(),
                             x=df[["confirmed", "deaths", "recovered", "active"]].sum().values,
                             text=df[["confirmed", "deaths", "recovered", "active"]].sum().values,
                             orientation='h',
                             marker=dict(color=[colors[1], colors[3], colors[2], colors[0]]),
                             ),
                      )
        fig.update_traces(opacity=0.7,
                          textposition=["inside", "outside", "inside", "outside"],
                          texttemplate='%{text:.3s}',
                          hovertemplate='Status: %{y} <br>Count: %{x:,.2f}',
                          marker_line_color='rgb(255, 255, 255)',
                          marker_line_width=5.0
                          )
        fig.update_layout(
            title="Total count",
            width=800,
            legend_title_text="Status",
            xaxis=dict(title="Count"),
            yaxis=dict(showgrid=False, showticklabels=True),
        )
        return fig

def overall_insights_window():
	st.markdown("## Overall Insights")
	# st.write("Total confirmed cases : %d \n\n Total recovered cases : %d \n\n Total deaths : %d" % (current_confirmed, current_recovered, current_deceased))
	st.line_chart(chart_data)

	st.markdown("### Closed cases stats")

	fig1 = plt.figure()
	ax1 = fig1.add_axes([0,0,1,1])
	ax1.axis('equal')
	category = ['Recovered', 'Dead']
	number = [current_recovered, current_deceased]
	ax1.pie(number, labels = category, autopct='%1.2f%%', radius=0.5)
	st.pyplot()


def statewise_data_window():
	st.markdown("## Statewise Data")

	state = st.selectbox("Select state", statelist, index=0, key=None)
	info_dict = {}
	info_dict = stateinfo[state]
	st.markdown("## %s" % (state))
	st.markdown("Total Confirmed Cases : %s" % (info_dict["confirmed"]))
	st.markdown("Total Active Cases : %s" % (info_dict["active"]))
	st.markdown("Total Deaths : %s" % (info_dict["deaths"]))
	st.markdown("Total Recovered : %s" % (info_dict["recovered"]))
	state_info=pd.DataFrame(info_dict.items())
	#st.button('Download Dataframe as CSV')
	if st.button('Download state information'):
            tmp_dwnl=download_link(state_info,state,'Click here to download file')
            st.markdown(tmp_dwnl,unsafe_allow_html=True)
        #if st.button('Download Dataframe as CSV'):
            #tmp_download_link = download_link(info_dict, state'.csv', 'Click here to download your data!')
            #st.markdown(tmp_download_link, unsafe_allow_html=True)

	st.markdown("## View all states detailed information")
	state_data_active = []
	state_data_confirmed = []
	state_data_deaths = []
	state_data_recovered = []
	state_code_list = []
	for s in statelist:
		state_data_active.append(int(stateinfo[s]["active"]))
		state_data_confirmed.append(int(stateinfo[s]["confirmed"]))
		state_data_deaths.append(int(stateinfo[s]["deaths"]))
		state_data_recovered.append(int(stateinfo[s]["recovered"]))
		state_code_list.append(stateinfo[s]["statecode"])

	comparelist = ["Active Cases", "Confirmed Cases", "Deaths", "Recovered Cases"]
	compare = st.selectbox("Select an option..", comparelist, index=0, key=None)
	if compare == "Active Cases":
		plt.bar(state_code_list, state_data_active, color="blue", label=compare)
		plt.xticks(rotation=90, fontsize=7, fontweight="bold")
		st.pyplot()
	if compare == "Confirmed Cases":
		plt.bar(state_code_list, state_data_confirmed, color="blue", label=compare)
		plt.xticks(rotation=90, fontsize=7, fontweight="bold")
		st.pyplot()
	if compare == "Deaths":
		plt.bar(state_code_list, state_data_deaths, color="red", label=compare)
		plt.xticks(rotation=90, fontsize=7, fontweight="bold")
		st.pyplot()
	if compare == "Recovered Cases":
		plt.bar(state_code_list, state_data_recovered, color="green", label=compare)
		plt.xticks(rotation=90, fontsize=7, fontweight="bold")
		st.pyplot()



st.title("COVID-19 India Dashboard")
st.sidebar.title("Coronavirus India Dashboard")
st.sidebar.markdown("\
	This app aims to provide realtime analysis on the outbreak in India in the form of interactive charts.")

with urllib.request.urlopen("https://api.covid19india.org/data.json") as url:
    data = json.loads(url.read().decode())

daily_confirmed = np.zeros(np.size(data["cases_time_series"]))
daily_deceased = np.zeros(np.size(data["cases_time_series"]))
daily_recovered = np.zeros(np.size(data["cases_time_series"]))

total_confirmed = np.zeros(np.size(data["cases_time_series"]))
total_recovered = np.zeros(np.size(data["cases_time_series"]))
total_deceased = np.zeros(np.size(data["cases_time_series"]))


dates = []

i = 0
for d in data["cases_time_series"]:
	daily_confirmed[i] = d["dailyconfirmed"]
	daily_deceased[i] = d["dailydeceased"]
	daily_recovered[i] = d["dailyrecovered"]
	total_confirmed[i] = d["totalconfirmed"]
	total_recovered[i] = d["totalrecovered"]
	total_deceased[i] = d["totaldeceased"]

	dates.append(d["date"])
	i = i+1

current_confirmed = total_confirmed[np.size(total_confirmed)-1]
current_recovered = total_recovered[np.size(total_recovered)-1]
current_deceased = total_deceased[np.size(total_deceased)-1]

chart_data = np.transpose([daily_confirmed, daily_recovered, daily_deceased])
chart_data = pd.DataFrame(chart_data, columns=["Daily Confirmed Cases", "Daily Recovered Cases", "Daily Deaths"])

statelist = []
stateinfo = {}
for d in data["statewise"]:
	if(d["state"]!="Total"):
		statelist.append(d["state"])
		stateinfo[d["state"]] = d


state_data=pd.DataFrame.from_dict(stateinfo,orient='index')
state_data=state_data.set_index('state')
state_data["confirmed"]=pd.to_numeric(state_data["confirmed"])
state_data["recovered"]=pd.to_numeric(state_data["recovered"])
state_data["deaths"]=pd.to_numeric(state_data["deaths"])
state_data["active"]=pd.to_numeric(state_data["active"])
fig = plot_snapshot_numbers(state_data, px.colors.qualitative.D3)
st.plotly_chart(fig)
#st.sidebar.markdown("#### Total confirmed cases : %d " % (current_confirmed))
#st.sidebar.markdown("#### Total recovered cases : %d " % (current_recovered))
#st.sidebar.markdown("#### Total deaths : %d " % (current_deceased))

st.sidebar.markdown("\n")
window = st.sidebar.selectbox("Please select data visualisation options:", ["Overall India Data", "Statewise Data"], index=0, key=None)


if(window == "Overall Insights"):
	plot_snapshot_numbers(state_data, px.colors.qualitative.D3)
#if(window == "Detailed Charts"):
	#detailed_charts_window()
if(window == "Statewise Data"):
	statewise_data_window()
