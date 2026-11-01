import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { currentMember } from '@/lib/session'

export async function POST(req: NextRequest) {
  const me = await currentMember()
  if (!me) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  const { lat, lng, accuracy } = await req.json()
  const c = await prisma.checkin.create({ data: { memberId: me.id, lat, lng, accuracy } })
  return NextResponse.json({ id: c.id })
}
