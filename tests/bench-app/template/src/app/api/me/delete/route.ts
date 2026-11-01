import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { currentMember } from '@/lib/session'

export async function POST() {
  const me = await currentMember()
  if (!me) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  await prisma.member.update({ where: { id: me.id }, data: { isActive: false } })
  return NextResponse.json({ ok: true, message: 'Account eliminato' })
}
