import { useEffect, useState } from 'react'
import Cookies from 'js-cookie'

export default function Dashboard() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = Cookies.get('token')
    if (!token) { window.location.href='/login'; return }
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/me`, {
      headers: {Authorization: `Bearer ${token}`}
    }).then(res=>res.json()).then(setUser)
  },[])

  if(!user) return <div>Loading...</div>

  return (
    <div className="p-4">
      <h1 className="text-xl mb-4">Hello {user.username}</h1>
      <a className="underline" href="/annotate">Annotate Audio</a>
    </div>
  )
}
