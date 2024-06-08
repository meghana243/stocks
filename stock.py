import streamlit as st
import yfinance as yf
from textblob import TextBlob
import plotly.graph_objs as go
import requests
from bs4 import BeautifulSoup

# List of popular Indian stock symbols
stock_symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
    "HDFC.NS", "ITC.NS", "BAJFINANCE.NS", "WIPRO.NS", "ADANIPORTS.NS",
    "MARUTI.NS", "LT.NS", "AXISBANK.NS", "TITAN.NS", "NESTLEIND.NS",
    "POWERGRID.NS", "NTPC.NS", "HCLTECH.NS", "M&M.NS", "ULTRACEMCO.NS",
    "SUNPHARMA.NS", "DRREDDY.NS", "TECHM.NS", "INDUSINDBK.NS", "TATASTEEL.NS"
]

# Function to perform sentiment analysis
def sentiment_analysis(stock_symbol):
    stock_data = yf.Ticker(stock_symbol)
    business_summary = stock_data.info.get('longBusinessSummary', None)

    if business_summary:
        blob = TextBlob(business_summary)
        sentiment = blob.sentiment
        return sentiment.polarity
    else:
        return None

# Function to plot candlestick chart and moving average
def plot_candlestick(stock_data):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x=stock_data.index,
                                 open=stock_data['Open'],
                                 high=stock_data['High'],
                                 low=stock_data['Low'],
                                 close=stock_data['Close'],
                                 name='Candlestick'))

    # Calculate and plot moving average
    fig.add_trace(go.Scatter(x=stock_data.index,
                             y=stock_data['Close'].rolling(window=20).mean(),
                             mode='lines',
                             line=dict(color='blue', width=2),
                             name='20-Day Moving Average'))

    fig.update_layout(title="Candlestick Chart with 20-Day Moving Average",
                      xaxis_title="Date",
                      yaxis_title="Price",
                      xaxis_rangeslider_visible=False)

    return fig

# Function to fetch finance-related news
def fetch_finance_news():
    url = "https://news.google.com/rss/search?q=finance&hl=en-IN&gl=IN&ceid=IN:en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("item")
    news = []
    for item in items[:5]:  # Displaying only top 5 news articles
        title = item.title.text
        link = item.link.text
        news.append({"title": title, "link": link})
    return news

# Streamlit app layout
def main():
    st.title("📈 Stock Analysis for Indian Stocks 🇮🇳")
    st.write("Get sentiment analysis, candlestick chart with moving average, and more for specific stocks.")

    # Creating tabs for Stock Analysis and Finance News
    tabs = ["Stock Analysis", "Finance News"]
    selected_tab = st.radio("Select Tab", tabs)

    if selected_tab == "Stock Analysis":
        stock_symbol = st.selectbox("Choose Stock Symbol", stock_symbols)
        stock_data = yf.download(stock_symbol, period="1y")

        sentiment_polarity = sentiment_analysis(stock_symbol)

        if sentiment_polarity is not None:
            st.write(f"Sentiment Analysis for **{stock_symbol}**: {sentiment_polarity:.2f}")

            if sentiment_polarity > 0:
                st.success("Positive sentiment detected! 😀")
                st.write("Consider investing in this stock.")
            elif sentiment_polarity < 0:
                st.error("Negative sentiment detected! 😞")
                st.write("Exercise caution before investing in this stock.")
            else:
                st.info("Neutral sentiment detected. 😐")
                st.write("No strong sentiment detected. Further analysis may be needed.")
        else:
            st.error("No business summary available for this stock.")

        st.plotly_chart(plot_candlestick(stock_data))

    elif selected_tab == "Finance News":
        news = fetch_finance_news()
        st.write("Top Finance News:")
        for item in news:
            st.markdown(f"- [{item['title']}]({item['link']})")

if __name__ == "__main__":
    main()
