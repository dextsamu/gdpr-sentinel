import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { currentMember } from '@/lib/session'

export async function POST(req: NextRequest) {
  const me = await currentMember()
  if (!me) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  const { dal, al, motivo, diagnosi, certificatoMedico } = await req.json()
  const a = await prisma.assenza.create({ data: { memberId: me.id, dal: new Date(dal), al: new Date(al), motivo, diagnosi, certificatoMedico } })
  return NextResponse.json({ id: a.id })
}
