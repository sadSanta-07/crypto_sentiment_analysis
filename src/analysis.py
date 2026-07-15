import pandas as pd
import numpy as np

class TradeAnalyzer:
    def __init__(self, processed_data_path: str):
        print(f"[+] Loading processed dataset from: {processed_data_path}")
        self.df = pd.read_csv(processed_data_path)
        self.df['date_join'] = pd.to_datetime(self.df['date_join'])
        self.df['Timestamp_UTC'] = pd.to_datetime(self.df['Timestamp_UTC'])
        
    def engineer_features(self) -> pd.DataFrame:
        """Creates advanced quantitative features for pattern discovery."""
        print("[+] Engineering new Alpha features...")
        df = self.df.copy()
        
        # Whale vs Retail 
        usd_90th_percentile = df['Size USD'].quantile(0.90)
        df['trader_tier'] = np.where(df['Size USD'] >= usd_90th_percentile, 'Whale', 'Retail')
        
        # Trade Outcome Categorization
        df['is_winning_trade'] = (df['net_pnl'] > 0).astype(int)
        
        # Sentiment
        df = df.sort_values('date_join')
        daily_sentiment = df.groupby('date_join')['sentiment_score'].first().reset_index()
        daily_sentiment['sentiment_3d_change'] = daily_sentiment['sentiment_score'].diff(periods=3)
        
        df = pd.merge(df, daily_sentiment[['date_join', 'sentiment_3d_change']], on='date_join', how='left')
        
        self.df = df
        return df

    def analyze_regime_performance(self) -> pd.DataFrame:
        """Analyzes how traders perform across different market psychological regimes."""
        if 'is_winning_trade' not in self.df.columns:
            self.engineer_features()
            
        print("[+] Calculating performance by Sentiment Regime...")
        regime_stats = self.df.groupby('sentiment_regime').agg(
            total_trades=('Account', 'count'),
            win_rate=('is_winning_trade', 'mean'),
            avg_net_pnl=('net_pnl', 'mean'),
            total_volume_usd=('Size USD', 'sum')
        ).reset_index()
        
        regime_stats['win_rate'] = (regime_stats['win_rate'] * 100).round(2)
        regime_stats['avg_net_pnl'] = regime_stats['avg_net_pnl'].round(2)
        
        return regime_stats.sort_values('avg_net_pnl', ascending=False)

    def analyze_whale_behavior(self) -> pd.DataFrame:
        """Compares Smart Money (Whales) vs Retail execution success."""
        if 'trader_tier' not in self.df.columns:
            self.engineer_features()
            
        print("[+] Analyzing Whale vs Retail execution...")
        tier_stats = self.df.groupby(['trader_tier', 'sentiment_regime']).agg(
            win_rate=('is_winning_trade', 'mean'),
            avg_pnl=('net_pnl', 'mean')
        ).reset_index()
        
        tier_stats['win_rate'] = (tier_stats['win_rate'] * 100).round(2)
        return tier_stats.sort_values(['trader_tier', 'win_rate'], ascending=[True, False])

if __name__ == "__main__":

    analyzer = TradeAnalyzer("data/processed/analytics_base.csv")
    analyzer.engineer_features()
    
    print("\n--- Regime Performance ---")
    print(analyzer.analyze_regime_performance().to_string(index=False))
    
    print("\n--- Whale vs Retail Behavior ---")
    print(analyzer.analyze_whale_behavior().to_string(index=False))