#!/usr/bin/env python
"""Quick test of new historical endpoints."""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test enriched candles
resp = client.get('/api/v1/historical/candles-with-indicators/15min?limit=5')
print(f'Enriched candles 15min: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'  Got {len(data)} candles')
    if data:
        candle = data[0]
        print(f'  First: {candle["timestamp_utc"]}, close={candle["close"]}, EMA20={candle["ema20"]}')

# Test latest analysis
resp = client.get('/api/v1/historical/latest-analysis/15min')
print(f'Latest analysis 15min: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'  Close: {data["close_price"]}, EMA20={data["indicators"]["ema20"]}, Data age: {data["data_age_hours"]} hours')

# Test signals history
resp = client.get('/api/v1/historical/signals-history?limit=5')
print(f'Signals history: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'  Total: {data["total_signals"]}, returned: {data["returned"]}')

# Test performance stats
resp = client.get('/api/v1/historical/performance-stats')
print(f'Performance stats: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    stats = data['overall_stats']
    print(f'  Total signals: {stats["total_signals"]}, wins: {stats["wins"]}, losses: {stats["losses"]}')
    print(f'  Win rate: {stats["win_rate_pct"]}%, Net expectancy: {stats["net_expectancy_r"]}R')

# Test refresh info
resp = client.get('/api/v1/historical/data-refresh-info')
print(f'Refresh info: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'  Last update: {data["last_update_utc"]}')
    print(f'  Data age: {data["data_age_hours"]} hours')
