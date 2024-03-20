import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
import streamlit.components.v1 as components
import yfinance as yf
import time
from pytrends.request import TrendReq
import requests
from bs4 import BeautifulSoup

def fetch_google_trends(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe='today 5-y', geo='', gprop='')
    data = pytrends.interest_over_time()
    return data

def fetch_stock_data(stocks):
    data = yf.download(stocks, start="2020-01-01", end="2024-01-01")['Adj Close']
    return data

def fetch_seo_data(url):
    # Send a GET request to the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract SEO-related data
        # Example: Extract meta tags, keywords, title, etc.
        seo_data = {
            'Title': soup.title.string,
            'Meta Description': soup.find('meta', attrs={'name': 'description'})['content'],
            # Add more SEO data extraction logic as needed
        }
        # Extract keywords
        keywords = []
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords['content'].split(',')
        seo_data['Keywords'] = keywords

        # Fetch SEO ranks or search volume for keywords (You may need to use an external API for this)
        # Here, I'm just adding placeholder values
        keyword_ranks = {}
        for keyword in keywords:
            # Placeholder values for demonstration
            keyword_ranks[keyword] = {
                'Rank': 1,  # Placeholder for rank
                'Search Volume': 1000  # Placeholder for search volume
            }
        seo_data['Keyword Ranks'] = keyword_ranks

        return seo_data
    else:
        st.error("Failed to fetch SEO data. Please check the URL and try again.")
        return None

def main():
    """A Simple EDA App with Streamlit Components"""
    st.set_page_config(layout="wide")  # Set wide layout for better visualization

    # Set light mode theme
    st.markdown("""
        <style>
        .css-1aumxhk {
            color: black;
            background-color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    menu = ["Exploratory Data Analysis", "SEO Analyzer"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Exploratory Data Analysis":
        st.header("📊 Automated EDA | Business")
        data_file = st.file_uploader("Upload File", type=['csv', 'xlsx', 'xls', 'db'])
        if data_file is not None:
            if data_file.name.endswith('.csv'):
                df = pd.read_csv(data_file)
            elif data_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(data_file)
            elif data_file.name.endswith('.db'):
                # Assuming the data is stored in a SQLite database
                df = pd.read_sql_query('SELECT * FROM table_name', 'sqlite:///{}'.format(data_file.name))
            else:
                st.error("Unsupported file format. Please upload a CSV, Excel, or database file.")
                return
            
            st.dataframe(df.head())
            
            # Add EDA functionalities using pandas
            st.subheader("📈 Exploratory Data Analysis (EDA)")
            if st.checkbox("Show Summary Statistics"):
                st.write(df.describe())
                
            if st.checkbox("Show Missing Values"):
                st.write(df.isnull().sum())
                
            if st.checkbox("Show Data Types"):
                st.write(df.dtypes)
                
            if st.checkbox("Show Correlation Heatmap"):
                st.write(df.corr())
            
            # Visualizations
            st.subheader("📊 Data Visualization")
            if st.checkbox("Line Chart"):
                st.line_chart(df)
                
            if st.checkbox("Area Chart"):
                st.area_chart(df)
                
            if st.checkbox("Bar Chart"):
                st.bar_chart(df)
            
        
            
            if st.button("Generate Report"):
                profile = ProfileReport(df)
                profile.to_file("Pandas_Profile_Report.html")
                st.success("Report generated successfully!")
                with open("Pandas_Profile_Report.html", "r") as file:
                    html_content = file.read()
                # Set CSS styling for responsiveness and centering
                css = "<style> .responsive { max-width: 100%; height: auto; margin: 0 auto; } </style>"
                components.html(css + html_content, width=900, height=600, scrolling=True)

    elif choice == "SEO Analyzer":
        st.header("🔍 SEO Analyzer")
        website_url = st.text_input("Enter the URL of the website:")
        if st.button("Analyze SEO"):
            if website_url:
                seo_data = fetch_seo_data(website_url)
                if seo_data:
                    st.subheader("SEO Data:")
                    st.write(seo_data)
            else:
                st.error("Please enter the URL of the website.")
                
if __name__ == '__main__':
    main()
