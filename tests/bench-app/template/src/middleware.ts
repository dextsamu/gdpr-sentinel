import { NextRequest, NextResponse } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const ip = req.headers.get('x-real-ip') ?? ''
  await fetch(new URL('/api/internal/access-log', req.url), {
    method: 'POST',
    body: JSON.stringify({ ip, userAgent: req.headers.get('user-agent'), path: req.nextUrl.pathname, sid: req.cookies.get('sid')?.value }),
  }).catch(() => {})
  return res
}
