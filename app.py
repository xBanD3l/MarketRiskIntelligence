"""
Main Application: app.py
Description: Streamlit dashboard for Market Risk Intelligence. 
Integrates ingestion, analysis, and visualization modules.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from data_ingestion import fetch_news
from event_detection import classify_event
from risk_scoring import calculate_risk_score
from sentiment_analysis import process_sentiment
from explanation import generate_explanation

# --- Configuration ---
load_dotenv()
st.set_page_config(page_title="Market Risk Intelligence Dashboard", layout="wide")

# Prioritize Environment Variable, then fallback to hardcoded key for immediate UX if needed
# but ideally users should use .env
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '99bb391f582543129b44687a48665d62')
DATA_FILE = 'processed_market_data.csv'
SAMPLE_DATA_FILE = 'sample_data/market_samples.csv'


def load_and_process_data(use_samples=False):
    """
    Orchestrates the full data pipeline: Ingestion -> Detection -> Scoring -> Sentiment -> Explanation.
    
    Args:
        use_samples (bool): If True, skips live fetching and uses pre-generated sample data.

    Returns:
        pd.DataFrame: The fully processed market intelligence dataset.
    """
    if use_samples:
        if os.path.exists(SAMPLE_DATA_FILE):
            df = pd.read_csv(SAMPLE_DATA_FILE)
            df['date'] = pd.to_datetime(df['date']).dt.date
            # Ensure consistency even in sample data
            df.to_csv(DATA_FILE, index=False)
            return df
        else:
            st.error("Sample data file not found. Please run generate_samples.py.")
            return pd.DataFrame()

    with st.spinner("Analyzing live market signals..."):
        # 1. Ingestion
        # Fallback to samples if key is dummy or empty
        if not NEWS_API_KEY or NEWS_API_KEY == 'YOUR_KEY_HERE':
            st.warning("No API key provided. Falling back to sample data.")
            return load_and_process_data(use_samples=True)

        df = fetch_news(NEWS_API_KEY)
        if df.empty:
            st.warning("Live news fetch failed. Falling back to sample data.")
            return load_and_process_data(use_samples=True)

        # 2. Event Detection
        df['category'] = df['text'].apply(classify_event)

        # 3. Risk Scoring
        risk_results = df.apply(
            lambda row: calculate_risk_score(row['category'], row['text']), 
            axis=1
        )
        df['risk_score'] = [r[0] for r in risk_results]
        df['risk_reason'] = [r[1] for r in risk_results]

        # 4. Sentiment & Speculative Analysis
        df = process_sentiment(df)

        # 5. Intelligence Summary Generation
        df['intelligence_summary'] = df.apply(
            lambda row: generate_explanation(
                row['category'], 
                row['risk_score'], 
                row['sentiment'], 
                row['speculative_flag']
            ), axis=1
        )

        # Persistence
        df.to_csv(DATA_FILE, index=False)
        return df


def apply_filters(df):
    """
    Handles all sidebar filtering logic.
    
    Args:
        df (pd.DataFrame): The raw processed DataFrame.
        
    Returns:
        pd.DataFrame: The filtered subset of data.
    """
    st.sidebar.subheader("🔍 Intelligence Filters")
    
    # Date Range
    min_date, max_date = df['date'].min(), df['date'].max()
    date_range = st.sidebar.date_input(
        "Timeline", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )
    
    # Category
    cats = ["All Categories"] + sorted(df['category'].unique().tolist())
    selected_cat = st.sidebar.selectbox("Event Category", cats)
    
    # Intensity
    def map_intensity(s):
        if s > 30: return "High ⚠️"
        if s > 10: return "Medium 🔹"
        return "Low ✅"
    
    df['intensity'] = df['risk_score'].apply(map_intensity)
    selected_intensities = st.sidebar.multiselect(
        "Risk Intensity",
        options=["Low ✅", "Medium 🔹", "High ⚠️"],
        default=["Low ✅", "Medium 🔹", "High ⚠️"]
    )
    
    # Toggles & Sorting
    show_spec = st.sidebar.toggle("🚨 Speculative Risk Only", value=False)
    sort_by = st.sidebar.radio(
        "Sort Feed By", 
        ["Risk Score (High → Low)", "Date (Newest → Oldest)"]
    )

    # Filtering Logic
    f_df = df.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        f_df = f_df[(f_df['date'] >= start) & (f_df['date'] <= end)]
    
    if selected_cat != "All Categories":
        f_df = f_df[f_df['category'] == selected_cat]
        
    f_df = f_df[f_df['intensity'].isin(selected_intensities)]
    
    if show_spec:
        f_df = f_df[f_df['speculative_flag']]
        
    # Sorting
    if sort_by == "Risk Score (High → Low)":
        f_df = f_df.sort_values(by='risk_score', ascending=False)
    else:
        f_df = f_df.sort_values(by='date', ascending=False)
        
    return f_df, sort_by


# --- Main Dashboard UI ---

# Header
st.markdown(
    "<h1 style='text-align: center; color: #1f1f1f; margin-bottom: 0;'>"
    "Market Risk Intelligence</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 1.1em;'>"
    "AI-driven analysis of financial sentiment and risk magnitude.</p>", 
    unsafe_allow_html=True
)
st.divider()

# Sidebar Controls
st.sidebar.markdown("### 🕹️ Dashboard Controls")

demo_mode = st.sidebar.checkbox("🚀 Enable Demo Mode (Sample Data)", value=False)

if st.sidebar.button("🔄 Refresh Market Data", use_container_width=True):
    raw_df = load_and_process_data(use_samples=demo_mode)
else:
    if os.path.exists(DATA_FILE):
        raw_df = pd.read_csv(DATA_FILE)
        raw_df['date'] = pd.to_datetime(raw_df['date']).dt.date
    else:
        raw_df = load_and_process_data(use_samples=demo_mode)
        if not raw_df.empty:
            raw_df['date'] = pd.to_datetime(raw_df['date']).dt.date

if not raw_df.empty:
    st.sidebar.divider()
    filtered_df, current_sort = apply_filters(raw_df)

    # Sidebar Summary
    st.sidebar.divider()
    st.sidebar.subheader("📌 Quick Summary")
    sm1, sm2 = st.sidebar.columns(2)
    sm1.metric("Selected", len(filtered_df))
    sm2.metric("High Risk", len(filtered_df[filtered_df['intensity'] == "High ⚠️"]))
    st.sidebar.metric("Speculative Signals 🚨", filtered_df['speculative_flag'].sum())
    
    if not filtered_df.empty:
        st.sidebar.divider()
        st.sidebar.subheader("🔥 Top Spotlight")
        top_5 = filtered_df.sort_values(by='risk_score', ascending=False).head(5)
        for i, (idx, row) in enumerate(top_5.iterrows()):
            st.sidebar.caption(f"{i+1}. {row['text'][:60]}... ({row['risk_score']})")

    # --- Dashboard Content ---
    
    # 1. Top 3 Critical News Cards (New Feature)
    if not filtered_df.empty:
        st.header("🔥 Top 3 Critical Signals")
        top_3 = filtered_df.sort_values(by='risk_score', ascending=False).head(3)
        cols = st.columns(3)
        for i, (idx, row) in enumerate(top_3.iterrows()):
            with cols[i]:
                st.markdown(
                    f"<div style='background-color: #fff2f2; border-left: 5px solid #e74c3c; padding: 15px; border-radius: 5px; height: 180px;'>"
                    f"<h4 style='color: #e74c3c; margin: 0;'>{row['category']}</h4>"
                    f"<p style='font-size: 0.9em; color: #1f1f1f; margin: 10px 0;'><b>Score: {row['risk_score']}</b> | {row['source']}</p>"
                    f"<p style='font-size: 0.85em; color: #444;'>{row['text'][:80]}...</p>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
        st.divider()

    # Section 1: Risk Summary & Analytics
    st.header("📊 Market Risk Analytics")
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    if not filtered_df.empty:
        avg_r = filtered_df['risk_score'].mean()
        high_r = len(filtered_df[filtered_df['risk_score'] > 30])
        spec_r = filtered_df['speculative_flag'].sum()
        total_r = len(filtered_df)
    else:
        avg_r, high_r, spec_r, total_r = 0, 0, 0, 0

    m1.metric("Average Risk", f"{avg_r:.1f}")
    m2.metric("Active Signals", total_r)
    m3.metric("Critical Alerts", high_r)
    m4.metric("Speculative Hype", spec_r)

    # Charts Grid
    if not filtered_df.empty:
        col_list = st.columns(2)
        
        with col_list[0]:
            st.subheader("Risk by Category")
            chart_df = filtered_df.groupby('category')['risk_score'].mean().reset_index()
            
            # Robust Color Logic: Avoid ZeroDivisionError if all scores are identical
            if len(chart_df['risk_score'].unique()) > 1:
                color_scale = ['#2ecc71', '#f1c40f', '#e74c3c']
                color_col = 'risk_score'
            else:
                # Single value or uniform data: Use a fixed color based on the actual score
                score = chart_df['risk_score'].iloc[0]
                fixed_color = '#e74c3c' if score > 30 else ('#f1c40f' if score > 10 else '#2ecc71')
                color_scale = [fixed_color, fixed_color]
                color_col = None

            fig_bar = px.bar(
                chart_df, x='category', y='risk_score', 
                color=color_col if color_col else None,
                color_discrete_sequence=[fixed_color] if not color_col else None,
                color_continuous_scale=color_scale if color_col else None,
                template='plotly_white'
            )
            fig_bar.update_layout(coloraxis_showscale=False, height=350)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_list[1]:
            st.subheader("Event Distribution")
            fig_pie = px.pie(
                filtered_df, names='category', hole=0.4, 
                template='plotly_white', color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        # Enhanced Historical Trend
        st.subheader("Historical Risk Trend")
        trend_df = filtered_df.groupby('date')['risk_score'].mean().reset_index().sort_values('date')
        
        if len(trend_df) > 1:
            fig_line = px.line(
                trend_df, x='date', y='risk_score', markers=True, 
                template='plotly_white'
            )
            fig_line.update_traces(line_color='#e74c3c', line_width=3)
        else:
            # Handle single day of data with a scatter plot
            fig_line = px.scatter(
                trend_df, x='date', y='risk_score', size='risk_score',
                template='plotly_white', color_discrete_sequence=['#e74c3c']
            )
        
        fig_line.update_layout(hovermode="x unified", xaxis_title="Timeline", yaxis_title="Risk Magnitude")
        st.plotly_chart(fig_line, use_container_width=True)
        
        # CSV Download Button
        st.divider()
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Intelligence (CSV)",
            data=csv,
            file_name='market_risk_report.csv',
            mime='text/csv',
            use_container_width=True
        )
    else:
        st.info("No data available for the selected filters. Adjust your criteria in the sidebar.")

    st.divider()

    # --- Intelligence Feed ---
    st.header("📋 Detailed Intelligence Feed")
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            icon = "⚠️" if row['risk_score'] > 30 else ("🔹" if row['risk_score'] > 10 else "✅")
            badge = "🚨 " if row['speculative_flag'] else ""
            title = f"{icon} {badge}{row['category']} | {row['source']} | {row['date']}"
            
            with st.expander(title):
                c1, c2, c3 = st.columns([1, 1, 4])
                c1.metric("Risk Magnitude", f"{row['risk_score']}/50")
                c2.metric("Sentiment", f"{row['sentiment']:.2f}")
                with c3:
                    st.markdown("**AI Assessment**")
                    st.info(row['intelligence_summary'])
                
                st.divider()
                st.markdown(f"**Source Headline**: *{row['text']}*")
                st.caption(f"Reasoning Log: {row['risk_reason']}")
    else:
        st.warning("No intelligence signals found for current filters.")

    # Section 3: Deep Dive (Expander)
    if not filtered_df.empty:
        with st.expander("🔍 Deep Dive: Intelligence Logs"):
            st.write("Below are the component reasoning logs for the top 10 relevant events.")
            st.table(filtered_df[['text', 'risk_reason']].head(10))

else:
    st.warning("No initial market data found. Click 'Refresh Market Data' to begin.")
