'use client'

import { useState, useEffect } from 'react'
import { GraduationCap, Award, Clock, CheckCircle, AlertTriangle } from 'lucide-react'

const API_BASE = '/api/v1/people-management/portal'

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

export default function TreinamentosPortalPage() {
  const [enrollments, setEnrollments] = useState<any[]>([])
  const [certificates, setCertificates] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [enrRes, certRes] = await Promise.all([
          fetch(`${API_BASE}/my-trainings/enrollments`, { headers: getAuthHeaders() }),
          fetch(`${API_BASE}/my-trainings/certificates`, { headers: getAuthHeaders() }),
        ])
        if (enrRes.ok) { const d = await enrRes.json(); setEnrollments(d.items || d || []) }
        if (certRes.ok) { const d = await certRes.json(); setCertificates(d.items || d || []) }
      } catch { /* fallback */ } finally { setLoading(false) }
    }
    load()
  }, [])

  if (loading) {
    return <div className="bg-white rounded-xl p-6 shadow-sm animate-pulse"><div className="h-40 bg-gray-100 rounded" /></div>
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-purple-600" />
          Meus Treinamentos
        </h2>
        {enrollments.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Nenhum treinamento matriculado</p>
        ) : (
          <div className="space-y-3">
            {enrollments.map((e: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{e.training_title || e.title}</p>
                  <p className="text-sm text-gray-500">{e.course_name}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  e.status === 'attended' ? 'bg-green-100 text-green-700' :
                  e.status === 'enrolled' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-700'
                }`}>{e.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-yellow-600" />
          Meus Certificados
        </h2>
        {certificates.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Nenhum certificado emitido</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {certificates.map((c: any, i: number) => (
              <div key={i} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium">{c.course_name || c.certificate_number}</p>
                    <p className="text-sm text-gray-500">N {c.certificate_number}</p>
                    <p className="text-xs text-gray-400 mt-1">Emitido: {c.issued_at}</p>
                  </div>
                  {c.status === 'valid' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  )}
                </div>
                {c.expires_at && (
                  <p className="text-xs text-orange-600 mt-2 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Validade: {c.expires_at}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
