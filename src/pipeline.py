import pandas as pd
import numpy as np
from pathlib import Path

class DataPipeline:
    def __init__(self, raw_data_dir: str, output_dir: str):
        self.raw_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_trade_data(self, filename: str) -> pd.DataFrame:
        """Loads and normalizes raw historical Hyperliquid exchange trade data."""
        path = self.raw_dir / filename
        print(f"[+] Processing raw trade data from: {path}")
        
        
        df = pd.read_csv(path)
        
        
        df.columns = df.columns.str.strip()
        
        # 1. Timezone Resolution
        df['Timestamp_IST'] = pd.to_datetime(df['Timestamp IST'], format='%d-%m-%Y %H:%M')
        df['Timestamp_UTC'] = df['Timestamp_IST'] - pd.Timedelta(hours=5, minutes=30)
        df['date_join'] = df['Timestamp_UTC'].dt.date
        
        # 2. Performance Engineering
        df['Closed PnL'] = pd.to_numeric(df['Closed PnL'], errors='coerce').fillna(0.0)
        df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0.0)
        df['net_pnl'] = df['Closed PnL'] - df['Fee']
        
        keep_cols = [
            'Account', 'Coin', 'Execution Price', 'Size Tokens', 'Size USD', 
            'Side', 'Direction', 'net_pnl', 'date_join', 'Timestamp_UTC'
        ]
        return df[keep_cols]

    def clean_sentiment_data(self, filename: str) -> pd.DataFrame:
        """Loads and transforms Bitcoin Market Sentiment Index tracking data."""
        path = self.raw_dir / filename
        print(f"[+] Processing sentiment data from: {path}")
        
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        
        df['date_join'] = pd.to_datetime(df['date']).dt.date
        
        keep_cols = ['date_join', 'value', 'classification']
        return df[keep_cols].rename(columns={'value': 'sentiment_score', 'classification': 'sentiment_regime'})

    def run(self, trade_file: str, sentiment_file: str, output_name: str = "analytics_base.csv"):
        """Executes full analytical extract, transform, load cycle."""
        trades_df = self.clean_trade_data(trade_file)
        sentiment_df = self.clean_sentiment_data(sentiment_file)
        
        merged_df = pd.merge(trades_df, sentiment_df, on='date_join', how='inner')
        
        output_path = self.output_dir / output_name
        merged_df.to_csv(output_path, index=False)
        print(f"[SUCCESS] Analytical dataset pipeline complete. Saved to: {output_path}")
        print(f"Total processed records: {len(merged_df)}")

if __name__ == "__main__":
    pipeline = DataPipeline(raw_data_dir="data/raw", output_dir="data/processed")
    pipeline.run(trade_file="historical_data.csv", sentiment_file="fear_greed_index.csv")