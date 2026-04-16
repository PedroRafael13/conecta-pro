'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

/**
 * Precificação foi movida para o módulo CRM/Comercial.
 * Esta página faz redirect automático para manter compatibilidade.
 */
export default function PrecificacaoRedirect() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/modulos/crm/precificacao')
  }, [router])

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center text-muted-foreground">
        <p className="text-sm">Redirecionando para CRM / Comercial...</p>
      </div>
    </div>
  )
}
