import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(
    page_title="Hyperliquid Quant Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main layout colors */
    .stApp {
        background-color: #0d0e12;
        color: #e0e6ed;
    }
    /* Sleek metric cards customization */
    [data-testid="stMetricValue"] {
        color: #00ff9d !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.2rem !important;
        text-shadow: 0 0 10px rgba(0, 255, 157, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #8b9bb4 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem !important;
    }
    /* Custom container boxes */
    .quant-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #161922;
        border: 1px solid #262c3d;
        margin-bottom: 20px;
    }
    .neon-text-pink { color: #ff007a; font-weight: bold; }
    .neon-text-green { color: #00ff9d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

plt.style.use('dark_background')
plt.rcParams.update({
    "axes.facecolor": "#161922",
    "figure.facecolor": "#0d0e12",
    "grid.color": "#262c3d",
    "text.color": "#e0e6ed",
    "axes.labelcolor": "#8b9bb4"
})


@st.cache_data
def load_analytical_data():
    path = Path("data/processed/analytics_base.csv")
    if not path.exists():
        return None
    data = pd.read_csv(path)

    usd_90th = data['Size USD'].quantile(0.90)
    data['trader_tier'] = np.where(data['Size USD'] >= usd_90th, 'Whale', 'Retail')
    data['is_winning_trade'] = (data['net_pnl'] > 0).astype(int)
    return data

df = load_analytical_data()

if df is None:
    st.error("Processing Error: 'data/processed/analytics_base.csv' not detected. Please execute 'python src/pipeline.py' locally first.")
    st.stop()

st.title(" Hyperliquid Trade & Sentiment Analytics Engine")
st.markdown("### `Production-Grade Quantitative Research Framework // Primetrade.ai Hiring Review`")
st.markdown("---")


st.markdown("<div class='quant-box'><h4>🚀 Macro Alpha Indicators</h4></div>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

total_trades = len(df)
overall_win_rate = (df['is_winning_trade'].mean() * 100)
extreme_greed_pnl = df[df['sentiment_regime'] == 'Extreme Greed']['net_pnl'].mean()
whale_pnl_multiplier = df[df['trader_tier'] == 'Whale']['net_pnl'].mean() / df[df['trader_tier'] == 'Retail']['net_pnl'].mean()

m1.metric("Total Executed Lines", f"{total_trades:,}")
m2.metric("Baseline Ecosystem Win Rate", f"{overall_win_rate:.2f}%")
m3.metric("Extreme Greed Avg PnL", f"${extreme_greed_pnl:.2f}")
m4.metric("Whale vs Retail Alpha Factor", f"{whale_pnl_multiplier:.1f}x")


st.sidebar.header(" Quant Strategy Filters")
selected_tier = st.sidebar.multiselect("Select Trader Cohorts", options=['Retail', 'Whale'], default=['Retail', 'Whale'])
sentiment_filter = st.sidebar.multiselect("Select Sentiment Regimes", options=list(df['sentiment_regime'].unique()), default=list(df['sentiment_regime'].unique()))


filtered_df = df[(df['trader_tier'].isin(selected_tier)) & (df['sentiment_regime'].isin(sentiment_filter))]

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("####  Regime Performance Mapping")
    
    regime_stats = filtered_df.groupby('sentiment_regime').agg(
        win_rate=('is_winning_trade', 'mean'),
        avg_net_pnl=('net_pnl', 'mean')
    ).reset_index()
    regime_stats['win_rate'] = regime_stats['win_rate'] * 100
    
    order_list = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    regime_stats['sentiment_regime'] = pd.Categorical(regime_stats['sentiment_regime'], categories=order_list, ordered=True)
    regime_stats = regime_stats.sort_values('sentiment_regime')

    fig, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=regime_stats, x='sentiment_regime', y='win_rate', color='#00ff9d', alpha=0.8, ax=ax1)
    ax1.set_ylabel('Win Rate (%)', color='#00ff9d', fontweight='bold')
    ax1.set_xlabel('Market Sentiment')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=regime_stats, x='sentiment_regime', y='avg_net_pnl', color='#ff007a', marker='o', markersize=8, linewidth=2.5, ax=ax2)
    ax2.set_ylabel('Average Net PnL ($)', color='#ff007a', fontweight='bold')
    ax2.grid(False)
    
    st.pyplot(fig)

with col2:
    st.markdown("#### ⚔️ Strategic Quantitative Findings")
    st.markdown(f"""
    <div class='quant-box'>
        <p><span class='neon-text-pink'>1. The Neutral Chop Warning:</span> Segmented calculations show that operating inside neutral environments offers an average win probability floor near <b>36.10%</b>. Capital friction dominates this zone.</p>
        <p><span class='neon-text-green'>2. Expansion Capture:</span> The structural edge inside crypto assets concentrates heavily during momentum bursts (<span class='neon-text-green'>Extreme Greed</span>), pushing local sample win metrics to <b>46.74%</b>.</p>
        <p><span class='neon-text-pink'>3. Capital Scale Advantage:</span> Whales exhibit heavily asymmetric return curves, securing significantly higher absolute net capture margins compared to high-frequency retail allocations.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("#### Filtered Structural Data Ledger")
st.dataframe(filtered_df.head(100), use_container_width=True)