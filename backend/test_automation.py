#!/usr/bin/env python
"""Test data automation and scheduler endpoints."""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from main import app

def test_automation():
    """Test all automation endpoints."""
    client = TestClient(app)
    results = []

    print("\n📋 Testing Data Automation Setup\n")
    print("="*60)

    # Test 1: Trigger manual refresh
    print("\n1️⃣ Manual Data Refresh")
    resp = client.post('/api/v1/admin/data/refresh')
    assert resp.status_code == 200
    data = resp.json()
    print(f"  ✅ Status: {data['result']['status']}")
    print(f"  ✅ Duration: {data['result'].get('duration_seconds', 'N/A')}s")
    results.append(('Manual Refresh', True))

    # Test 2: Check refresh status
    print("\n2️⃣ Refresh Status")
    resp = client.get('/api/v1/admin/data/refresh-status')
    assert resp.status_code == 200
    status = resp.json()
    print(f"  ✅ Last status: {status['status']['status']}")
    print(f"  ✅ Last refresh: {status['status'].get('last_refresh', 'Never')}")
    results.append(('Refresh Status', True))

    # Test 3: Start scheduler
    print("\n3️⃣ Start Scheduler")
    resp = client.post('/api/v1/admin/scheduler/start')
    assert resp.status_code == 200
    data = resp.json()
    print(f"  ✅ Message: {data['message']}")
    print(f"  ✅ Jobs configured: {len(data['jobs'])}")
    for job in data['jobs']:
        print(f"     - {job['name']}: Next run at {job['next_run_time']}")
    results.append(('Start Scheduler', True))

    # Test 4: Get scheduler status
    print("\n4️⃣ Scheduler Status")
    resp = client.get('/api/v1/admin/scheduler/status')
    assert resp.status_code == 200
    status = resp.json()
    sched = status['scheduler']
    print(f"  ✅ Scheduler running: {sched['running']}")
    print(f"  ✅ Jobs: {len(sched['jobs'])}")
    for job in sched['jobs']:
        print(f"     - {job['name']}: Next run {job['next_run_time']}")
    results.append(('Scheduler Status', True))

    # Test 5: Detailed health check
    print("\n5️⃣ Detailed System Health")
    resp = client.get('/api/v1/admin/system/health-detailed')
    assert resp.status_code == 200
    health = resp.json()
    print(f"  ✅ Data loaded: {health['data']['is_loaded']}")
    print(f"  ✅ Data type: {health['data']['data_type']}")
    print(f"  ✅ Data age: {health['data']['data_age_hours']} hours")
    print(f"  ✅ Scheduler running: {health['scheduler']['running']}")
    print(f"  ✅ Next scheduled runs: {len(health['scheduler']['next_runs'])}")
    for run in health['scheduler']['next_runs']:
        print(f"     - {run['job']}: {run['next_run']}")
    results.append(('System Health', True))

    # Test 6: Stop scheduler
    print("\n6️⃣ Stop Scheduler")
    resp = client.post('/api/v1/admin/scheduler/stop')
    assert resp.status_code == 200
    data = resp.json()
    print(f"  ✅ Message: {data['message']}")
    results.append(('Stop Scheduler', True))

    # Summary
    print("\n" + "="*60)
    print("✅ AUTOMATION TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"\n📊 Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Data automation is ready.\n")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed.\n")
        return False

if __name__ == '__main__':
    try:
        success = test_automation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
