
import datetime
from typing import List
from colorhash import ColorHash
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from homeharvest import scrape_property


@st.cache_data(ttl= datetime.timedelta(days=1))
def load_data(location:str, listing_type: str, last:int):
    properties = scrape_property(
    location=location,
    listing_type=listing_type, # (sold, for_sale, for_rent, pending)
    past_days=last,  # sold in last 30 days - listed in last 30 days if (for_sale, for_rent)

    # date_from="2023-05-01", # alternative to past_days
    # date_to="2023-05-28",
    # foreclosure=True
    # mls_only=True,  # only fetch MLS listings
    )
    print(f"Number of properties: {len(properties)}")
    return properties

location = st.text_input("Location", value="Everett, WA ")
listing_type = st.selectbox("Listing type", ["for_rent", "for_sale", "sold", "pending"], index=0)
last_days = st.slider('Query data for last days', min_value=7, max_value=90, value=30)

data_load_state = st.text(f'Loading {listing_type} data for past {last_days} days... (may take awhile)')
properties = load_data(location.strip(), listing_type, last_days)
data_load_state.text("Done! (using cached data)")

st.title(f'🏠 Data analysis for {location.strip()} in the past {last_days} days')
st.caption(f'Found {len(properties)} listings')

st.bar_chart(properties['style'].value_counts())
rental_types = properties['style'].unique()
selected_rental_type = st.multiselect("Type", rental_types, default="SINGLE_FAMILY" if "SINGLE_FAMILY" in rental_types else rental_types[0])

filtered_data = properties[properties['style'].isin(selected_rental_type)]
if not len(filtered_data.index):
    st.subheader('Select a listing type above to get more insights!')

if st.checkbox("Show filtered data"):
    st.subheader("Filtered data")
    st.dataframe(filtered_data)

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(properties)

COLOR_MAP = {k: ColorHash(k).hex if k not in selected_rental_type else "#0068c9" for k in rental_types}
properties["color"] = properties['style'].map(COLOR_MAP) 
st.map(properties.dropna(subset=['latitude', 'longitude']), latitude=properties['latitude'].dropna(), longitude=properties['longitude'].dropna(), color='color')
st.caption(f'ᐧ:blue[Selected {selected_rental_type} denoted in blue.]')
# filtered_map_data = filtered_data.dropna(subset=['latitude', 'longitude'])
# st.map(filtered_map_data, latitude=filtered_map_data['latitude'].dropna(), longitude=filtered_map_data['longitude'].dropna()) #, color='color'

#  The 'x' property is an array that may be specified as a tuple, list, numpy array, or pandas Series
def grouped_bar_chart_stats(df: pd.DataFrame, x: List[str]):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=df['min'], name='Min'))
    fig.add_trace(go.Bar(x=x, y=df['mean'], name='Mean'))
    fig.add_trace(go.Bar(x=x, y=df['median'], name='Median'))
    fig.add_trace(go.Bar(x=x, y=df['max'], name='Max'))
    return fig

def groupby_aggregate(df: pd.DataFrame, groupby: List[str], index: str, aggregrate: List[str]= ['count', 'min', 'max', 'mean', 'median'], round:int = 0):
    return df.groupby(groupby, observed=True)[index].agg(aggregrate).round(round).reset_index()

st.subheader(f'Analysis using {len(filtered_data.index)} listings available on {datetime.datetime.today().strftime("%Y-%m-%d")}') #fix when cache refresh

st.title("Listing Price")
st.subheader(f'Statistics based on listed {listing_type} price')
price_bed_bath = groupby_aggregate(filtered_data, ['beds', 'full_baths'], 'list_price')
price_bed_bath_chart = grouped_bar_chart_stats(price_bed_bath, price_bed_bath['beds'].astype(str) + "x" + price_bed_bath['full_baths'].astype(str))
price_bed_bath_chart.update_layout(
    xaxis_title="Beds x Baths",
    yaxis_title="Price",
    title="Price by Bed and Bath"
)
st.dataframe(price_bed_bath)
st.plotly_chart(price_bed_bath_chart)

bin_range_step = st.slider('Categorize by Years', min_value=3, max_value=20, value=5)
year_built = filtered_data.copy()[filtered_data['year_built'].notna()]
year_built['year_bucket'] = pd.cut(year_built['year_built'], bins=range(1950, 2024, bin_range_step), include_lowest=True)
year_built_group_listprice = groupby_aggregate(year_built, ['year_bucket'], 'list_price')
year_built_chart = grouped_bar_chart_stats(year_built_group_listprice, year_built_group_listprice['year_bucket'].astype(str))
year_built_chart.update_layout(
    xaxis_title="Year built",
    yaxis_title="List Price",
    title="List Price grouped by Year built"
)
st.plotly_chart(year_built_chart)
if st.checkbox("Show table for list price by Year built"):
    st.dataframe(year_built_group_listprice)
    

st.title('Days listed on MLS')
listing_days = groupby_aggregate(filtered_data, ['beds', 'full_baths'], 'days_on_mls')
listing_days_chart = grouped_bar_chart_stats(listing_days, listing_days['beds'].astype(str) + "x" + listing_days['full_baths'].astype(str))
listing_days_chart.update_layout(
    xaxis_title="Beds x Baths",
    yaxis_title="Listing Days",
    title="Listing Days by Bed and Bath"
)
st.plotly_chart(listing_days_chart)
if st.checkbox("Show table"):
    st.dataframe(listing_days)

## Todo comparable market analysis
## Todo store for_rent into a DB and get past rent.