const API = 'https://us21.api.mailchimp.com/3.0'

export async function subscribeToNewsletter(email: string, nome: string) {
  await fetch(`${API}/lists/${process.env.MAILCHIMP_LIST_ID}/members`, {
    method: 'POST',
    headers: { Authorization: `apikey ${process.env.MAILCHIMP_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email_address: email, status: 'subscribed', merge_fields: { FNAME: nome } }),
  })
}
