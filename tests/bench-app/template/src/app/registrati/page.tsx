'use client'
import { useState } from 'react'

export default function Registrati() {
  const [form, setForm] = useState({ nome: '', cognome: '', email: '', telefono: '', password: '', newsletter: true })
  async function submit(e: React.FormEvent) {
    e.preventDefault()
    await fetch('/api/auth/register', { method: 'POST', body: JSON.stringify(form) })
  }
  return (
    <form onSubmit={submit}>
      <input placeholder="Nome" onChange={(e) => setForm({ ...form, nome: e.target.value })} />
      <input placeholder="Cognome" onChange={(e) => setForm({ ...form, cognome: e.target.value })} />
      <input placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Telefono" onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
      <input type="password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <label><input type="checkbox" defaultChecked onChange={(e) => setForm({ ...form, newsletter: e.target.checked })} /> Iscrivimi alla newsletter</label>
      <p>Iscrivendoti accetti l'<a href="/privacy">informativa</a>.</p>
      <button>Registrati</button>
    </form>
  )
}
