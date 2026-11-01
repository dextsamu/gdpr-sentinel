import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { currentMember } from '@/lib/session'

export async function GET() {
  const me = await currentMember()
  if (!me) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  const data = await prisma.member.findUnique({
    where: { id: me.id },
    select: { nome: true, cognome: true, email: true, telefono: true, newsletterOptIn: true, createdAt: true, checkins: true, assenze: true },
  })
  return new NextResponse(JSON.stringify(data, null, 2), { headers: { 'Content-Disposition': 'attachment; filename="miei-dati.json"' } })
}
