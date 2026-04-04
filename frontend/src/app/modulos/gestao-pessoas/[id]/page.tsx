"use client"

import { useEffect } from "react"
import { useRouter, useParams } from "next/navigation"

/**
 * /modulos/gestao-pessoas/:id → redirect para gestão de pessoas
 * Criado: fix Skill-11 Verif.1 — rota referenciada em gestao-pessoas/rh/page.tsx:304
 */
export default function GestaoPessoasDetalhe() {
  const router = useRouter()
  const params = useParams()
  const id = params?.id as string

  useEffect(() => {
    if (id) {
      router.replace(`/modulos/gestao-pessoas?id=${id}`)
    } else {
      router.replace("/modulos/gestao-pessoas")
    }
  }, [id, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  )
}
