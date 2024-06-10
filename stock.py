import streamlit as st
import yfinance as yf
from textblob import TextBlob
import plotly.graph_objs as go
import requests
from bs4 import BeautifulSoup
import time

# List of stock symbols for NSE and BOM
nse_symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
    "HDFC.NS", "ITC.NS", "BAJFINANCE.NS", "WIPRO.NS", "ADANIPORTS.NS",
    "MARUTI.NS", "LT.NS", "AXISBANK.NS", "TITAN.NS", "NESTLEIND.NS",
    "POWERGRID.NS", "NTPC.NS", "HCLTECH.NS", "M&M.NS", "ULTRACEMCO.NS",
    "SUNPHARMA.NS", "DRREDDY.NS", "TECHM.NS", "INDUSINDBK.NS", "TATASTEEL.NS"
]

bom_symbols = [
    "500209.BOM", "500325.BOM", "532540.BOM", "500696.BOM", "500010.BOM",
    "532174.BOM", "500247.BOM", "532215.BOM", "532454.BOM", "500180.BOM",
    "500182.BOM", "532500.BOM", "532555.BOM", "500104.BOM", "532663.BOM",
    "532281.BOM", "500312.BOM", "500112.BOM", "500410.BOM", "500790.BOM"
]

def sentiment_analysis(stock_symbol):
    stock_data = yf.Ticker(stock_symbol)
    business_summary = stock_data.info.get('longBusinessSummary', None)

    if business_summary:
        blob = TextBlob(business_summary)
        sentiment = blob.sentiment
        return sentiment.polarity
    else:
        return None

def plot_candlestick(stock_data):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x=stock_data.index,
                                 open=stock_data['Open'],
                                 high=stock_data['High'],
                                 low=stock_data['Low'],
                                 close=stock_data['Close'],
                                 name='Candlestick'))

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

def fetch_finance_news(stock_symbol):
    query = stock_symbol.split('.')[0]  # Extract company name from symbol
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    news = []
    for item in items[:5]:  # Displaying only top 5 news articles
        title = item.title.text
        link = item.link.text
        news.append({"title": title, "link": link})
    return news

def fetch_trending_finance_news():
    url = "https://news.google.com/rss/search?q=finance&hl=en-IN&gl=IN&ceid=IN:en"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    news = []
    for item in items[:5]:  # Displaying only top 5 news articles
        title = item.title.text
        link = item.link.text
        news.append({"title": title, "link": link})
    return news

def live_price_tracking(ticker, exchange):
    url = f'https://www.google.com/finance/quote/{ticker}:{exchange}'
    previous_price = None
    price_trend = []

    # Streamlit placeholders
    price_placeholder = st.empty()
    sentiment_placeholder = st.empty()

    for _ in range(10000000):  # Large loop count for continuous tracking
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        class1 = "YMlKec fxKbKc"

        try:
            price = float(soup.find(class_=class1).text.strip()[1:].replace(",", ""))
            price_placeholder.text(f"Current price of {ticker} on {exchange}: ₹{price}")

            # Determine sentiment based on price trend
            if previous_price is not None:
                if price > previous_price:
                    price_trend.append(1)
                elif price < previous_price:
                    price_trend.append(-1)
                else:
                    price_trend.append(0)

                if len(price_trend) > 3:
                    price_trend.pop(0)

                if sum(price_trend) > 1:
                    sentiment_message = "The stock price is going up. It might be a good time to buy!"
                elif sum(price_trend) < -1:
                    sentiment_message = "The stock price is going down. It might be a good time to sell."
                else:
                    sentiment_message = "The stock price is stable. It might be best to hold onto your stocks for now."

                sentiment_placeholder.text(f"Sentiment: {sentiment_message}")

            previous_price = price

        except Exception as e:
            price_placeholder.text(f"Error fetching price: {e}")

        time.sleep(10)  # Adjust the sleep time as needed

def main():
    st.title("📈 Stock Analysis for Indian Stocks 🇮🇳")
    st.write("Get sentiment analysis, candlestick chart with moving average, and more for specific stocks.")

    tabs = ["Stock Analysis", "Finance News", "Live Price Tracking"]
    selected_tab = st.radio("Select Tab", tabs)

    if selected_tab == "Stock Analysis":
        stock_symbol = st.selectbox("Choose Stock Symbol", nse_symbols + bom_symbols)
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
        st.write("Sentiment analysis, coupled with candlestick chart patterns, offers investors a comprehensive view of market dynamics. While sentiment analysis delves into the emotional tone of news articles and social media discussions surrounding a stock, candlestick charts visually depict price movements over time. By combining these two analytical approaches, investors can gain deeper insights into market sentiment shifts and their impact on price action. For instance, a positive sentiment alongside bullish candlestick patterns, such as long white candles or bullish engulfing patterns, may signal potential upward price momentum. Conversely, negative sentiment coupled with bearish candlestick patterns, like long black candles or bearish engulfing patterns, could indicate impending downward pressure on stock prices. Thus, integrating sentiment analysis with candlestick chart analysis empowers investors to make more informed trading decisions in the dynamic stock market environment.")

        st.subheader("Related News")
        st.write("Keeping abreast of trending finance news is essential for investors as it provides valuable insights into market trends, economic indicators, and corporate developments. News articles can significantly influence stock prices by shaping market sentiment and investor perception. Positive news such as strong earnings reports or favorable economic data can lead to bullish market sentiment and drive stock prices higher, while negative news like regulatory issues or geopolitical tensions may trigger selling pressure and cause stock prices to decline. By staying informed about the latest financial news from diverse sources, investors can gain a holistic understanding of market dynamics and make informed investment decisions. Exploring various news sources allows investors to cross-reference information, validate trends, and identify emerging opportunities or risks in the market landscape.")
        news = fetch_finance_news(stock_symbol)
        for article in news:
            st.markdown(f"### {article['title']}")
            st.markdown(f"[Read more]({article['link']})")

    elif selected_tab == "Finance News":
        st.subheader("Trending Finance News")
        
        news = fetch_trending_finance_news()
        for article in news:
            st.markdown(f"### {article['title']}")
            st.markdown(f"[Read more]({article['link']})")

    elif selected_tab == "Live Price Tracking":
        st.write("Real-time price monitoring is a crucial tool for investors, providing them with up-to-the-minute information on stock prices and market movements. Fluctuations in stock prices offer valuable insights into market dynamics and investor sentiment, allowing investors to gauge market volatility, identify emerging trends, and assess the impact of news events or economic indicators on stock prices. By closely tracking price movements over time, investors can observe patterns, detect potential opportunities or risks, and make timely and informed investment decisions. Whether it's identifying entry or exit points, managing risk, or adjusting investment strategies, real-time price tracking empowers investors to stay ahead in the dynamic and ever-changing stock market environment.")
        exchange = st.selectbox("Select Exchange", ["NSE", "BOM"])
        if exchange == "NSE":
            ticker = st.selectbox("Choose Ticker", nse_symbols)
        else:
            ticker = st.selectbox("Choose Ticker", bom_symbols)

        if st.button("Start Tracking"):
            live_price_tracking(ticker.split('.')[0], exchange)

if __name__ == "__main__":
    main()
