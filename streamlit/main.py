from datetime import date, datetime
import pandas as pd
import requests
import streamlit as st
import altair as alt


def get_assets_symbol():
    response = requests.get('https://api.coincap.io/v2/assets')
    body = response.json()
    return body['data']


def get_asset_history(asset_id: str, d_from: date, d_to: date):
    dt_from = datetime.combine(d_from, datetime.min.time())
    dt_to = datetime.combine(d_to, datetime.max.time())
    response = requests.get(
        f'https://api.coincap.io/v2/assets/{asset_id}/history'
        f'?interval=d1&start={dt_from.timestamp() * 1000}&end={dt_to.timestamp() * 1000}'
    )
    body = response.json()
    return body['data']


if __name__ == '__main__':

    assets_symbol = get_assets_symbol()

    asset = st.sidebar.selectbox(
        'Select an asset', assets_symbol, format_func=lambda x: x['symbol']
    )

    date_from = st.sidebar.date_input(
        "Date from")

    date_to = st.sidebar.date_input(
        "Date to")

    if date_to < date_from:
        st.error('This is an error', icon="🚨")
        st.stop()

    history = get_asset_history(asset['id'], date_from, date_to)

    if not history:
        st.warning('No data for selected dates')
        st.stop()

    chart_data = pd.DataFrame(history)
    chart_data['time'] = pd.to_datetime(chart_data['time'], unit='ms')
    chart_data['time'] = chart_data['time'].dt.date
    chart_data['priceUsd'] = chart_data['priceUsd'].astype(float)
    chart_data = chart_data.rename(columns={'priceUsd': 'PRICE', 'time': 'TIME'})

    chart = alt.Chart(chart_data).mark_bar().encode(
        x='TIME', y='PRICE')

    st.altair_chart(chart, use_container_width=True)
