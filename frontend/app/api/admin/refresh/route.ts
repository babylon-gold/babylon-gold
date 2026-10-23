/**
 * Server-side proxy for protected admin data refresh endpoint.
 */

export async function POST() {
  const backendUrl = process.env.NEXT_PRIVATE_API_URL || 'http://localhost:8000/api/v1'
  const adminToken = process.env.ADMIN_API_KEY

  if (!adminToken) {
    return Response.json(
      { detail: 'Admin authentication not configured on server' },
      { status: 500 }
    )
  }

  try {
    const response = await fetch(`${backendUrl}/admin/data/refresh`, {
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
      { detail: `Failed to trigger refresh: ${message}` },
      { status: 500 }
    )
  }
}
