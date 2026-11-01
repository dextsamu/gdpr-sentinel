'use client'
import { useEffect, useState } from 'react'

export function CookieBanner() {
  const [visible, setVisible] = useState(false)
  useEffect(() => { setVisible(localStorage.getItem('cookie-ok') !== '1') }, [])
  if (!visible) return null
  return (
    <div className="banner">
      Questo sito usa cookie per migliorare la tua esperienza. <a href="/privacy">Informativa</a>
      <button onClick={() => { localStorage.setItem('cookie-ok', '1'); setVisible(false) }}>Accetta</button>
    </div>
  )
}
