import cron from 'node-cron'
import { prisma } from '@/lib/prisma'

cron.schedule('0 3 * * *', async () => {
  const cutoff = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  await prisma.loginAttempt.deleteMany({ where: { createdAt: { lt: cutoff } } })
})
