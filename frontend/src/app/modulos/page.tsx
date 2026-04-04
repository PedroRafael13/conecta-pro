import { redirect } from "next/navigation"

/**
 * /modulos → redirect para /modulos/dp (dashboard principal do ERP)
 * Criado: fix Skill-11 Verif.1 — rota referenciada em reembolso, licitações
 */
export default function ModulosPage() {
  redirect("/modulos/dp")
}
