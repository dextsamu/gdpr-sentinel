import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.2,
  sendDefaultPii: true,
  replaysSessionSampleRate: 0.1,
  integrations: [Sentry.replayIntegration({ maskAllText: false })],
})
