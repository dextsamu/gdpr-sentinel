import { cookies } from 'next/headers'
import { prisma } from './prisma'

export async function setSession(memberId: string, token: string) {
  (await cookies()).set('sid', token, { httpOnly: true, secure: true, sameSite: 'lax', path: '/', maxAge: 60 * 60 * 8 })
}

export async function currentMember() {
  const sid = (await cookies()).get('sid')?.value
  if (!sid) return null
  return prisma.member.findFirst({ where: { id: sid.split('.')[0], isActive: true } })
}
