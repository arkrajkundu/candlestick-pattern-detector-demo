import streamlit as st
import pandas as pd
import os
import mplfinance as mpf
from candlestick import candlestick
from io import BytesIO

# ----- Pattern dictionary -----
pattern_functions = {
    'BearishEngulfing (*)': candlestick.bearish_engulfing,
    'BearishHarami (*)': candlestick.bearish_harami,
    'BullishEngulfing (*)': candlestick.bullish_engulfing,
    'BullishHarami (*)': candlestick.bullish_harami,
    'DarkCloudCover (*)': candlestick.dark_cloud_cover,
    'Doji (*)': candlestick.doji,
    'DojiStar (*)': candlestick.doji_star,
    'DragonflyDoji (*)': candlestick.dragonfly_doji,
    'GravestoneDoji (*)': candlestick.gravestone_doji,
    'Hammer': candlestick.hammer,
    'HangingMan (*)': candlestick.hanging_man,
    'InvertedHammers (*)': candlestick.inverted_hammer,
    'MorningStar': candlestick.morning_star,
    'MorningStarDoji (*)': candlestick.morning_star_doji,
    'PiercingPattern (*)': candlestick.piercing_pattern,
    'RainDrop (*)': candlestick.rain_drop,
    'RainDropDoji (*)': candlestick.rain_drop_doji,
    'ShootingStar (*)': candlestick.shooting_star,
    'Star (*)': candlestick.star
}

EXAMPLE_CSV_DIR = "example_csvs"


# ----- Load CSV into DataFrame -----
def load_ohlcv_data(file_path_or_obj):
    df = pd.read_csv(file_path_or_obj)
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    df.set_index('timestamp', inplace=True)
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    return df


# ----- Detect pattern and generate chart -----
def detect_and_plot(df, pattern_name):
    func = pattern_functions.get(pattern_name)
    df = df.copy()
    df = func(df)

    if pattern_name not in df.columns or df[pattern_name].sum() == 0:
        return None, "Pattern not found in this dataset."

    pattern_points = df['close'].where(df[pattern_name] == True)
    marker_plot = mpf.make_addplot(pattern_points, type='scatter', markersize=100, marker='s', color='yellow')

    buf = BytesIO()
    mpf.plot(df, type='candle', style='charles', volume=True, title=pattern_name,
             addplot=marker_plot, figratio=(16, 9), figscale=1.2,
             savefig=dict(fname=buf, dpi=150, bbox_inches='tight', pad_inches=0.1))
    buf.seek(0)
    return buf, None


# ----- UI -----
st.title("📉 Candlestick Pattern Detector")

# Pattern Selection
pattern_name = st.selectbox("🔍 Select a Candlestick Pattern", list(pattern_functions.keys()))

# File input options
st.markdown("### 📂 Upload Your CSV or Use an Example")
uploaded_file = st.file_uploader("Upload OHLCV CSV", type=["csv"])

example_files = [f for f in os.listdir(EXAMPLE_CSV_DIR) if f.endswith(".csv")]
example_selected = st.selectbox("...or choose an example CSV", ["None"] + example_files)

df = None
source_label = ""

if uploaded_file:
    try:
        df = load_ohlcv_data(uploaded_file)
        source_label = uploaded_file.name
        st.success(f"✅ Uploaded file: {uploaded_file.name}")
    except Exception as e:
        st.error(f"❌ Failed to parse uploaded file: {e}")
elif example_selected != "None":
    try:
        example_path = os.path.join(EXAMPLE_CSV_DIR, example_selected)
        df = load_ohlcv_data(example_path)
        source_label = example_selected
        st.success(f"✅ Loaded example file: {example_selected}")
    except Exception as e:
        st.error(f"❌ Failed to load example file: {e}")

# Add Detect button
if df is not None:
    st.markdown("---")
    if st.button("🚀 Detect Pattern"):
        with st.spinner("Detecting pattern and generating chart..."):
            buf, error_msg = detect_and_plot(df, pattern_name)
        if error_msg:
            st.warning(error_msg)
        else:
            st.image(buf, caption=f"{pattern_name} Pattern Detected in: {source_label}", use_container_width=True)
            st.download_button("📥 Download Chart", data=buf, file_name=f"{pattern_name}_detected.png", mime="image/png")
else:
    st.info("Upload a CSV file or choose an example to continue.")