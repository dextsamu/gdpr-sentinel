import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'
import { subscribeToNewsletter } from '@/lib/newsletter'

export async function POST(req: NextRequest) {
  const body = await req.json()
  console.log('Nuova iscrizione', { email: body.email, telefono: body.telefono, nome: body.nome })
  const org = await prisma.organization.findFirstOrThrow()
  const member = await prisma.member.create({
    data: {
      nome: body.nome, cognome: body.cognome, email: body.email, telefono: body.telefono,
      passwordHash: await bcrypt.hash(body.password, 12), newsletterOptIn: body.newsletter ?? true, organizationId: org.id,
    },
  })
  if (member.newsletterOptIn) await subscribeToNewsletter(member.email, member.nome)
  return NextResponse.json({ id: member.id })
}
