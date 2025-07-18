import { useEffect, useState } from 'react'
import { getDocuments, deleteDocument, setShared } from '../api.js'

export default function Documents() {
  const [docs, setDocs] = useState([])

  useEffect(() => {
    load()
  }, [])

  async function load() {
    try {
      const res = await getDocuments()
      setDocs(res.documents)
    } catch (err) {
      console.error(err)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete document?')) return
    await deleteDocument(id)
    setDocs(docs.filter(d => d.id !== id))
  }

  async function handleToggle(id, shared) {
    const res = await setShared(id, !shared)
    setDocs(docs.map(d => (d.id === id ? { ...d, is_shared: res.is_shared } : d)))
  }

  return (
    <div>
      <h2>Documents</h2>
      <table border="1">
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Shared</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {docs.map(d => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.filename}</td>
              <td>{d.is_shared ? 'Yes' : 'No'}</td>
              <td>
                <button onClick={() => handleDelete(d.id)}>Delete</button>
                <button onClick={() => handleToggle(d.id, d.is_shared)} style={{ marginLeft: '0.5rem' }}>
                  {d.is_shared ? 'Unshare' : 'Share'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
