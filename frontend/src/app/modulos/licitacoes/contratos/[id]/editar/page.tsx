"use client"

import { useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

/**
 * /modulos/licitacoes/contratos/:id/editar → redirect para detalhe do contrato
 * Criado: fix Skill-11 Verif.1 — rota referenciada em contratos/[id]/page.tsx
 */
export default function EditarContratoPage() {
  const router = useRouter()
  const params = useParams()
  const id = params?.id as string

  useEffect(() => {
    if (id) {
      router.replace(`/modulos/licitacoes/contratos/${id}?editar=true`)
    } else {
      router.replace("/modulos/licitacoes/contratos")
    }
  }, [id, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  )
}
