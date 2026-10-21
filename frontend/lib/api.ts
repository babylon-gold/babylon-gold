// Copyright Babylon Studio 2026. All Rights Reserved.

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export async function fetchAnalysis(timeframe: string) {
  try {
    const response = await fetch(`${API_URL}/analysis?timeframe=${timeframe}`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching analysis:', error)
    throw error
  }
}

export async function fetchCandlesWithIndicators(timeframe: string) {
  try {
    const response = await fetch(`${API_URL}/candlesticks?timeframe=${timeframe}&indicators=true`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching candles with indicators:', error)
    throw error
  }
}

export async function fetchSignalsHistory() {
  try {
    const response = await fetch(`${API_URL}/signals`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching signals history:', error)
    throw error
  }
}

export async function fetchPerformanceStats() {
  try {
    const response = await fetch(`${API_URL}/performance`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching performance stats:', error)
    throw error
  }
}

export async function fetchSystemHealth() {
  try {
    const response = await fetch(`${API_URL}/admin/system/health-detailed`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching system health:', error)
    throw error
  }
}

export async function triggerManualRefresh() {
  try {
    const response = await fetch(`${API_URL}/admin/refresh-data`, {
      method: 'POST',
    })
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error triggering refresh:', error)
    throw error
  }
}

export async function fetchBacktestingResults(strategy: string, timeframe: string, startDate: string, endDate: string) {
  try {
    const params = new URLSearchParams({
      strategy,
      timeframe,
      start_date: startDate,
      end_date: endDate,
    })
    const response = await fetch(`${API_URL}/backtesting/results?${params}`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error fetching backtesting results:', error)
    throw error
  }
}

export async function saveNotificationPreferences(preferences: any) {
  try {
    const response = await fetch(`${API_URL}/notifications/preferences`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(preferences),
    })
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error saving notification preferences:', error)
    throw error
  }
}

export async function getNotificationPreferences() {
  try {
    const response = await fetch(`${API_URL}/notifications/preferences`)
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('Error getting notification preferences:', error)
    throw error
  }
}
