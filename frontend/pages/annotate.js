import { useEffect, useRef, useState } from 'react'
import Cookies from 'js-cookie'
import WaveSurfer from 'wavesurfer.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugin/wavesurfer.regions.min.js'

export default function Annotate() {
  const [job, setJob] = useState(null)
  const [language, setLanguage] = useState('')
  const fileRef = useRef()
  const waveformRef = useRef()
  const ws = useRef(null)
  const token = Cookies.get('token')

  const handleUpload = async (e) => {
    e.preventDefault()
    const file = fileRef.current.files[0]
    const formData = new FormData()
    formData.append('language', language)
    formData.append('file', file)
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    const data = await res.json()
    setJob(data)
    initWave(file)
  }

  const initWave = (file) => {
    ws.current = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: 'gray',
      progressColor: 'blue',
      plugins: [RegionsPlugin.create()]
    })
    ws.current.loadBlob(file)
  }

  const updateRegion = async (region) => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/segments/${job.id}/${region.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({start: region.start, end: region.end})
    })
  }

  useEffect(() => {
    if (ws.current) {
      ws.current.on('region-update-end', updateRegion)
      if (job && job.segments) {
        job.segments.forEach(seg => {
          ws.current.addRegion({ id: seg.id, start: seg.start, end: seg.end })
        })
      }
    }
  }, [job])

  const exportJob = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/export/${job.id}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'export.zip'
    a.click()
  }

  return (
    <div className="p-4 space-y-4">
      {!job && (
        <form onSubmit={handleUpload} className="space-y-2">
          <input type="file" accept="audio/wav" ref={fileRef} required />
          <select className="border p-2" value={language} onChange={e=>setLanguage(e.target.value)} required>
            <option value="">Language</option>
            <option value="lang1">Lang1</option>
            <option value="lang2">Lang2</option>
          </select>
          <button className="px-4 py-2 bg-blue-500 text-white" type="submit">Upload</button>
        </form>
      )}
      <div ref={waveformRef} />
      {job && <button className="px-4 py-2 bg-green-500 text-white" onClick={exportJob}>Export</button>}
    </div>
  )
}
