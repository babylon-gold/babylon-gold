/**
 * Server-side proxy for protected notification endpoints.
 */

const adminToken = process.env.ADMIN_API_KEY
const backendUrl = process.env.NEXT_PRIVATE_API_URL || 'http://localhost:8000/api/v1'

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  if (!adminToken) {
    throw new Error('Admin authentication not configured on server')
  }

  const response = await fetch(`${backendUrl}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${adminToken}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`)
  }

  return response.json()
}

export async function GET() {
  try {
    const data = await fetchWithAuth('/notifications/status')
    return Response.json(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return Response.json(
      { detail: `Failed to fetch notification status: ${message}` },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  const url = new URL(request.url)
  const action = url.searchParams.get('action') || 'preferences'

  try {
    let endpoint = `/notifications/${action}`
    let body = undefined

    if (action === 'preferences' && request.method === 'POST') {
      body = JSON.stringify(await request.json())
    }

    const data = await fetchWithAuth(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body,
    })

    return Response.json(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return Response.json(
      { detail: `Failed to update notifications: ${message}` },
      { status: 500 }
    )
  }
}
