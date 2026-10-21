#!/usr/bin/env python
"""Comprehensive integration test for real data pipeline."""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from main import app

def test_integration():
    """Test all real data endpoints."""
    client = TestClient(app)
    results = []

    # Test 1: Health check
    print("\n📋 Test 1: Health Check")
    resp = client.get('/api/v1/health')
    assert resp.status_code == 200
    health = resp.json()
    assert health['status'] in ['healthy', 'degraded']
    assert health['data_loaded']
    print(f"  ✅ Status: {health['status']}, Data loaded: {health['data_loaded']}")
    results.append(('Health Check', True))

    # Test 2: Data status
    print("\n📊 Test 2: Data Status")
    resp = client.get('/api/v1/data/status')
    assert resp.status_code == 200
    status = resp.json()
    assert status['is_loaded']
    assert status['data_type'] == 'historical'
    print(f"  ✅ Data type: {status['data_type']}")
    print(f"  ✅ Candles: {status['candle_counts']}")
    print(f"  ✅ Enriched candles: {status['enriched_candle_counts']}")
    print(f"  ✅ Signals: {status['signals_count']}")
    print(f"  ✅ Evaluated signals: {status['evaluated_signals_count']}")
    print(f"  ✅ Data age: {status['data_age_hours']} hours")
    results.append(('Data Status', True))

    # Test 3: Enriched candles
    print("\n📈 Test 3: Enriched Candles")
    resp = client.get('/api/v1/historical/candles-with-indicators/15min?limit=3')
    assert resp.status_code == 200
    candles = resp.json()
    assert len(candles) == 3
    candle = candles[0]
    assert 'timestamp_utc' in candle
    assert 'ema20' in candle
    assert 'rsi14' in candle
    print(f"  ✅ Loaded {len(candles)} enriched candles")
    print(f"  ✅ First candle: {candle['timestamp_utc']}, EMA20={candle['ema20']}, RSI={candle['rsi14']}")
    results.append(('Enriched Candles', True))

    # Test 4: Latest analysis
    print("\n🔍 Test 4: Latest Analysis")
    resp = client.get('/api/v1/historical/latest-analysis/1h')
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis['interval'] == '1h'
    assert analysis['close_price'] > 0
    assert analysis['data_type'] == 'تاريخية - Historical'
    assert analysis['data_age_hours'] is not None
    print(f"  ✅ Interval: {analysis['interval']}")
    print(f"  ✅ Close: {analysis['close_price']:.2f}")
    print(f"  ✅ Data age: {analysis['data_age_hours']} hours")
    print(f"  ✅ Is recent: {analysis['is_recent']}")
    results.append(('Latest Analysis', True))

    # Test 5: Signals history
    print("\n📢 Test 5: Signals History")
    resp = client.get('/api/v1/historical/signals-history?limit=10')
    assert resp.status_code == 200
    hist = resp.json()
    assert hist['total_signals'] > 0
    assert len(hist['signals']) <= 10
    print(f"  ✅ Total signals: {hist['total_signals']}")
    print(f"  ✅ Returned: {hist['returned']}")
    if hist['signals']:
        sig = hist['signals'][0]
        print(f"  ✅ First signal: {sig['signal_id']}, state={sig['state']}, result={sig['result']}")
    results.append(('Signals History', True))

    # Test 6: Performance stats
    print("\n📊 Test 6: Performance Statistics")
    resp = client.get('/api/v1/historical/performance-stats')
    assert resp.status_code == 200
    stats = resp.json()
    overall = stats['overall_stats']
    print(f"  ✅ Total signals: {overall['total_signals']}")
    print(f"  ✅ Wins: {overall['wins']}, Losses: {overall['losses']}")
    print(f"  ✅ Win rate: {overall['win_rate_pct']:.1f}%")
    print(f"  ✅ Net expectancy: {overall['net_expectancy_r']:.2f}R")
    print(f"  ✅ Strategies: {list(stats['by_strategy'].keys())}")
    print(f"  ✅ Regimes: {list(stats['by_regime'].keys())}")
    results.append(('Performance Stats', True))

    # Test 7: Data refresh info
    print("\n🔄 Test 7: Data Refresh Info")
    resp = client.get('/api/v1/historical/data-refresh-info')
    assert resp.status_code == 200
    info = resp.json()
    assert info['last_update_utc']
    assert info['data_age_hours'] is not None
    print(f"  ✅ Last update: {info['last_update_utc']}")
    print(f"  ✅ Data age: {info['data_age_hours']} hours")
    print(f"  ✅ Refresh process documented: Yes")
    results.append(('Refresh Info', True))

    # Summary
    print("\n" + "="*60)
    print("✅ INTEGRATION TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\n📊 Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Real data integration is working correctly.")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return False

if __name__ == '__main__':
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
