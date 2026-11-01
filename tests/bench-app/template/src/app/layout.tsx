import Script from 'next/script'
import localFont from 'next/font/local'
import { CookieBanner } from '@/components/CookieBanner'

const titoli = localFont({ src: '../../public/fonts/Titoli.woff2' })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet" />
        <Script src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX" strategy="afterInteractive" />
        <Script id="ga" strategy="afterInteractive">{`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-XXXXXXX');`}</Script>
      </head>
      <body className={titoli.className}>
        {children}
        <CookieBanner />
      </body>
    </html>
  )
}
