import { useState } from 'react'
import Cookies from 'js-cookie'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: new URLSearchParams({username, password})
    })
    if (res.ok) {
      const data = await res.json()
      Cookies.set('token', data.access_token)
      window.location.href = '/dashboard'
    }
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label>Username</label>
          <input className="border p-2 w-full" value={username} onChange={e=>setUsername(e.target.value)} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" className="border p-2 w-full" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button className="px-4 py-2 bg-blue-500 text-white" type="submit">Login</button>
      </form>
    </div>
  )
}
