/**
 * Server-side proxy for protected scheduler endpoints.
 */

export async function GET() {
  const backendUrl = process.env.NEXT_PRIVATE_API_URL || 'http://localhost:8000/api/v1'
  const adminToken = process.env.ADMIN_API_KEY

  if (!adminToken) {
    return Response.json(
      { detail: 'Admin authentication not configured on server' },
      { status: 500 }
    )
  }

  try {
    const response = await fetch(`${backendUrl}/admin/scheduler/status`, {
      headers: {
        Authorization: `Bearer ${adminToken}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return Response.json(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return Response.json(
      { detail: `Failed to fetch scheduler status: ${message}` },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  const backendUrl = process.env.NEXT_PRIVATE_API_URL || 'http://localhost:8000/api/v1'
  const adminToken = process.env.ADMIN_API_KEY

  if (!adminToken) {
    return Response.json(
      { detail: 'Admin authentication not configured on server' },
      { status: 500 }
    )
  }

  const url = new URL(request.url)
  const action = url.searchParams.get('action') || 'status'

  if (!['start', 'stop'].includes(action)) {
    return Response.json(
      { detail: 'Invalid scheduler action' },
      { status: 400 }
    )
  }

  try {
    const response = await fetch(`${backendUrl}/admin/scheduler/${action}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${adminToken}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return Response.json(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    return Response.json(
      { detail: `Failed to ${action} scheduler: ${message}` },
      { status: 500 }
    )
  }
}
