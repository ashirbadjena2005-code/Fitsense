import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000'

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'GET')
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'POST')
}

export async function PUT(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'PUT')
}

export async function DELETE(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'DELETE')
}

async function handleRequest(request: NextRequest, path: string[], method: string) {
  try {
    const url = new URL(`/api/${path.join('/')}`, BACKEND_URL)
    
    // Copy query parameters
    request.nextUrl.searchParams.forEach((value, key) => {
      url.searchParams.set(key, value)
    })

    // Get request body for POST/PUT requests
    let body = undefined
    if (method === 'POST' || method === 'PUT') {
      try {
        body = await request.text()
      } catch (error) {
        // Body might be empty
      }
    }

    // Forward the request to the backend
    const response = await fetch(url.toString(), {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Cookie': request.headers.get('cookie') || '',
      },
      body,
    })

    // Get response data
    const data = await response.text()
    
    // Create response with same status and headers
    const nextResponse = new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
    })

    // Copy relevant headers
    response.headers.forEach((value, key) => {
      if (key.toLowerCase() === 'set-cookie') {
        nextResponse.headers.set(key, value)
      }
    })

    return nextResponse
  } catch (error) {
    console.error('API proxy error:', error)
    return NextResponse.json(
      { success: false, message: 'Internal server error' },
      { status: 500 }
    )
  }
}
