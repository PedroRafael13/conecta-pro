"""
HERMES — Agente Documental do GEDEON
"Nenhum documento se perde, nenhum é duplicado"

Responsabilidades:
- Classificação automática de documentos uploadados
- Detecção de duplicatas por hash SHA-256
- Cache de documentos reutilizáveis entre meses
- Validação de autenticidade (chave de acesso NFS-e)
- Matching onvio_documents → colaborador → condomínio → kit (CPRO12 T4)
"""

import hashlib
import logging
import re
import unicodedata

logger = logging.getLogger(__name__)

# Tipos de documento reconhecidos automaticamente
TIPOS_DOCUMENTO = {
    # Folha de pagamento
    r"holerite|contracheque|recibo.*salario": "holerite",
    r"folha.*pagamento|payroll": "folha_pagamento",
    r"espelho.*ponto|ponto.*espelho|timesheet": "espelho_ponto",
    # Admissão/Demissão
    r"admiss[aã]o|contrato.*trabalho": "contrato_admissao",
    r"demiss[aã]o|rescis[aã]o|trct": "rescisao",
    r"seguro.*desemprego": "seguro_desemprego",
    # Saúde
    r"aso|atestado.*saude.*ocupacional": "aso",
    r"atestado.*medico|medical.*certificate": "atestado_medico",
    r"epi|equipamento.*protecao": "ficha_epi",
    # Certidões
    r"cnd|certidao.*negativa.*debito": "cnd_federal",
    r"crf.*fgts|regularidade.*fgts": "crf_fgts",
    r"certidao.*trabalhista": "certidao_trabalhista",
    r"alvara.*funcionamento": "alvara_funcionamento",
    # Fiscal
    r"nota.*fiscal|nfs?-?e|nfse": "nota_fiscal",
    r"boleto|cobranca": "boleto",
    # Treinamentos
    r"nr-?\d+|treinamento|certificado.*curso": "certificado_nr",
}

# Categorias por tipo
_CATEGORIAS: dict[str, str] = {
    "holerite": "folha_pagamento",
    "folha_pagamento": "folha_pagamento",
    "espelho_ponto": "folha_pagamento",
    "contrato_admissao": "admissao",
    "rescisao": "demissao",
    "seguro_desemprego": "demissao",
    "aso": "saude",
    "atestado_medico": "saude",
    "ficha_epi": "saude",
    "cnd_federal": "certidoes",
    "crf_fgts": "certidoes",
    "certidao_trabalhista": "certidoes",
    "alvara_funcionamento": "certidoes",
    "nota_fiscal": "fiscal",
    "boleto": "fiscal",
    "certificado_nr": "treinamento",
}

# Tipos reutilizáveis entre meses
_REUTILIZAVEIS: dict[str, bool] = {
    "cnd_federal": True,
    "crf_fgts": False,  # validade mensal
    "certidao_trabalhista": True,
    "alvara_funcionamento": True,
    "holerite": False,
    "espelho_ponto": False,
    "aso": True,  # validade anual
    "ficha_epi": False,
    "nota_fiscal": False,
    "boleto": False,
}

# Mapa Onvio categoria → ged_kit_documents document_type — docs de empresa/condomínio
MAPA_TIPOS_ONVIO_EMPRESA: dict[str, str] = {
    "folha_pagamento": "folha_pagamento",
    "dctfweb_recibo": "dctfweb_recibo",
    "dctfweb_extrato": "dctfweb_extrato",
    "dctfweb_declaracao": "dctfweb_declaracao",
    "fgts_guia": "gfd_fgts_mensal",
    "fgts_relatorio": "relatorio_gfd_fgts",
    "fgts_consignado": "comp_pag_fgts",
    "fgts_consignado_relatorio": "relatorio_gfd_fgts",
    "das_simples_nacional": "das_simples_nacional",
    "parcelamento_simples": "parcelamento_simples",
    "guia_issqn": "guia_issqn",
    "dctfweb_resumo_creditos": "dctfweb_resumo_creditos",
    "dctfweb_resumo_debitos": "dctfweb_resumo_debitos",
    "dctfweb_creditos": "dctfweb_creditos",
    "dctfweb_debitos": "dctfweb_debitos",
    "decimo_terceiro": "decimo_terceiro",
    "empresa_docs": "outro",
    "inss_guia": "gps_inss",
    "dar_sefaz": "dar_sefaz",
}

# Mapa Onvio categoria → ged_kit_documents document_type — docs per-funcionário
MAPA_TIPOS_ONVIO_FUNCIONARIO: dict[str, str] = {
    "recibo_folha": "contracheque",
    "ficha_registro": "ficha_empregado",
    "contrato_trabalho": "contrato_trabalho",
    "atestado": "aso",
    "folha_ponto": "folha_ponto",
    "escala_mes": "escala_mes",
}

# Stop words ignoradas no matching de nomes (espelho de kit_builder_service)
_STOP_WORDS_MATCH = {
    "CONDOMINIO",
    "CONDOMINIUM",
    "RESIDENCIAL",
    "EDIFICIO",
    "PREDIAL",
    "VILLAGE",
    "DO",
    "DA",
    "DE",
    "DOS",
    "DAS",
    "E",
    "O",
    "A",
    "EM",
}


class Hermes:
    """
    Agente Documental — classificação e gestão inteligente
    de documentos do GEDEON.
    """

    def classificar_documento(
        self,
        nome_arquivo: str,
        conteudo_preview: str = "",
    ) -> dict:
        """
        Classificar documento automaticamente.
        Retorna tipo, categoria e metadados detectados.
        """
        texto = (nome_arquivo + " " + conteudo_preview).lower()
        texto = re.sub(r"[_\-.]", " ", texto)

        for pattern, tipo in TIPOS_DOCUMENTO.items():
            if re.search(pattern, texto, re.IGNORECASE):
                return {
                    "tipo": tipo,
                    "categoria": _CATEGORIAS.get(tipo, "outros"),
                    "confianca": "alta",
                    "auto": True,
                }

        return {
            "tipo": "outros",
            "categoria": "outros",
            "confianca": "baixa",
            "auto": False,
        }

    def detectar_duplicata(
        self,
        arquivo_hash: str,
        documentos_existentes: list[dict],
    ) -> dict | None:
        """Detectar se documento já existe pelo hash."""
        for doc in documentos_existentes:
            if doc.get("hash") == arquivo_hash:
                return doc
        return None

    def calcular_hash(self, conteudo: bytes) -> str:
        """Calcular hash SHA-256 do documento."""
        return hashlib.sha256(conteudo).hexdigest()

    def pode_reutilizar(
        self,
        tipo: str,
        competencia_anterior: str,
        competencia_atual: str,
    ) -> bool:
        """
        Verificar se documento pode ser reutilizado do mês anterior.
        Certidões de longa validade: podem reutilizar.
        Holerites e espelhos de ponto: sempre novo.
        """
        return _REUTILIZAVEIS.get(tipo, False)

    async def processar_upload(
        self,
        nome_arquivo: str,
        conteudo: bytes,
        cliente_id: str,
        competencia: str,
        funcionario_id: str | None = None,
    ) -> dict:
        """
        Processar upload completo:
        1. Classificar automaticamente
        2. Calcular hash (detecção de duplicata)
        3. Retornar metadados para salvar
        """
        classificacao = self.classificar_documento(nome_arquivo)
        arquivo_hash = self.calcular_hash(conteudo)

        resultado = {
            "nome_original": nome_arquivo,
            "tipo": classificacao["tipo"],
            "categoria": classificacao["categoria"],
            "auto_classificado": classificacao["auto"],
            "hash": arquivo_hash,
            "cliente_id": cliente_id,
            "competencia": competencia,
            "funcionario_id": funcionario_id,
            "tamanho_bytes": len(conteudo),
        }

        logger.info(
            "HERMES: documento classificado — %s → %s [%s]",
            nome_arquivo,
            classificacao["tipo"],
            "auto" if classificacao["auto"] else "manual",
        )
        return resultado

    # ── Matching: onvio_documents → colaborador → condomínio → kit ──────────

    def _normalize(self, s: str) -> str:
        nfkd = unicodedata.normalize("NFKD", (s or "").upper())
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def _sig(self, s: str) -> set[str]:
        return {w for w in self._normalize(s).split() if w not in _STOP_WORDS_MATCH and len(w) >= 3}

    def _build_cond_to_ged_map(self, db) -> dict[str, str]:
        """Build condominios.id → ged_clients.id via word-set intersection."""
        from sqlalchemy import text

        condominios = db.execute(text("SELECT id::text, nome FROM condominios WHERE ativo = true")).fetchall()
        ged_clients = db.execute(text("SELECT id::text, name FROM ged_clients WHERE is_active = true")).fetchall()

        mapping: dict[str, str] = {}
        for cond_id, cond_nome in condominios:
            cond_sig = self._sig(cond_nome)
            if not cond_sig:
                continue
            for ged_id, ged_name in ged_clients:
                ged_sig = self._sig(ged_name)
                if cond_sig <= ged_sig or ged_sig <= cond_sig:
                    mapping[cond_id] = ged_id
                    break
        return mapping

    def _mes_ref_to_date(self, mes_ref: str) -> str:
        """'04.2026' → '2026-04-01'"""
        parts = mes_ref.split(".")
        return f"{parts[1]}-{parts[0]}-01"

    def _vincular_empresa(
        self,
        db,
        cond_to_ged: dict[str, str],
        categoria: str,
        caminho_local: str,
        cond_id: str,
        ref_date: str,
    ) -> bool:
        """Vincular doc empresa-level ao slot correspondente no kit."""
        from sqlalchemy import text

        kit_doc_type = MAPA_TIPOS_ONVIO_EMPRESA.get(categoria)
        if not kit_doc_type:
            return False

        ged_client_id = cond_to_ged.get(cond_id)
        if not ged_client_id:
            return False

        kit_row = db.execute(
            text("""
                SELECT id::text FROM ged_document_kits
                WHERE client_id = CAST(:client_id AS uuid)
                  AND reference_month = CAST(:ref_date AS date)
            """),
            {"client_id": ged_client_id, "ref_date": ref_date},
        ).fetchone()
        if not kit_row:
            return False
        kit_id = kit_row[0]

        # INV-5: só preenche slots vazios
        slot = db.execute(
            text("""
                SELECT id::text FROM ged_kit_documents
                WHERE kit_id = CAST(:kit_id AS uuid)
                  AND document_type = :doc_type
                  AND (file_path IS NULL OR file_path = '')
                  AND employee_id IS NULL
                LIMIT 1
            """),
            {"kit_id": kit_id, "doc_type": kit_doc_type},
        ).fetchone()
        if not slot:
            return False

        db.execute(
            text("""
                UPDATE ged_kit_documents
                SET file_path = :caminho, source_module = 'hermes', updated_at = NOW()
                WHERE id = CAST(:slot_id AS uuid)
            """),
            {"caminho": caminho_local, "slot_id": slot[0]},
        )
        return True

    def _vincular_funcionario(
        self,
        db,
        cond_to_ged: dict[str, str],
        categoria: str,
        caminho_local: str,
        employee_id: str,
        ref_date: str,
    ) -> bool:
        """Vincular doc per-employee ao slot correspondente no kit."""
        from sqlalchemy import text

        kit_doc_type = MAPA_TIPOS_ONVIO_FUNCIONARIO.get(categoria)
        if not kit_doc_type:
            return False

        # Resolve condomínio do funcionário via alocações ativas
        aloc = db.execute(
            text("""
                SELECT condominio_id::text FROM employee_alocacoes
                WHERE employee_id = CAST(:emp_id AS uuid) AND ativo = true
                ORDER BY data_inicio DESC LIMIT 1
            """),
            {"emp_id": employee_id},
        ).fetchone()
        if not aloc:
            return False

        ged_client_id = cond_to_ged.get(aloc[0])
        if not ged_client_id:
            return False

        kit_row = db.execute(
            text("""
                SELECT id::text FROM ged_document_kits
                WHERE client_id = CAST(:client_id AS uuid)
                  AND reference_month = CAST(:ref_date AS date)
            """),
            {"client_id": ged_client_id, "ref_date": ref_date},
        ).fetchone()
        if not kit_row:
            return False
        kit_id = kit_row[0]

        # INV-5: só preenche slots vazios do mesmo funcionário
        slot = db.execute(
            text("""
                SELECT id::text FROM ged_kit_documents
                WHERE kit_id = CAST(:kit_id AS uuid)
                  AND document_type = :doc_type
                  AND employee_id = CAST(:emp_id AS uuid)
                  AND (file_path IS NULL OR file_path = '')
                LIMIT 1
            """),
            {"kit_id": kit_id, "doc_type": kit_doc_type, "emp_id": employee_id},
        ).fetchone()
        if not slot:
            return False

        db.execute(
            text("""
                UPDATE ged_kit_documents
                SET file_path = :caminho, source_module = 'hermes', updated_at = NOW()
                WHERE id = CAST(:slot_id AS uuid)
            """),
            {"caminho": caminho_local, "slot_id": slot[0]},
        )
        return True

    def _recalcular_completude_mes(self, db, ref_date: str) -> int:
        """Recalcular completion_percentage para todos os kits do mês (INV-12)."""
        from sqlalchemy import text

        kits = db.execute(
            text("""
                SELECT id::text, total_documents FROM ged_document_kits
                WHERE reference_month = CAST(:ref_date AS date)
            """),
            {"ref_date": ref_date},
        ).fetchall()

        for kit_id, total_docs in kits:
            if not total_docs:
                continue
            filled = (
                db.execute(
                    text("""
                    SELECT COUNT(*) FROM ged_kit_documents
                    WHERE kit_id = CAST(:kit_id AS uuid)
                      AND file_path IS NOT NULL
                      AND file_path != ''
                """),
                    {"kit_id": kit_id},
                ).scalar()
                or 0
            )

            pct = round((filled / total_docs) * 100, 2)
            db.execute(
                text("""
                    UPDATE ged_document_kits
                    SET completion_percentage = :pct, updated_at = NOW()
                    WHERE id = CAST(:kit_id AS uuid)
                """),
                {"pct": pct, "kit_id": kit_id},
            )

        return len(kits)

    def processar_mes(self, mes_ref: str | None = None) -> dict:
        """
        Vincular todos os onvio_documents do mês aos slots ged_kit_documents.
        Idempotente: pula slots já preenchidos (INV-5).
        Recalcula completion_percentage após vincular (INV-12).
        """
        from datetime import date

        from sqlalchemy import text

        from core.database.session import get_sync_db

        if mes_ref is None:
            today = date.today()
            mes_ref = f"{today.month:02d}.{today.year}"

        ref_date = self._mes_ref_to_date(mes_ref)

        vinculados = 0
        ignorados = 0
        erros = 0

        with get_sync_db() as db:
            cond_to_ged = self._build_cond_to_ged_map(db)

            docs = db.execute(
                text("""
                    SELECT id::text, nome_arquivo, categoria, caminho_local,
                           doc_scope, condominio_id::text,
                           referente_a_employee_id::text
                    FROM onvio_documents
                    WHERE mes_ref = :mes_ref
                      AND caminho_local IS NOT NULL
                """),
                {"mes_ref": mes_ref},
            ).fetchall()

            for doc in docs:
                doc_id, nome_arquivo, categoria, caminho_local, doc_scope, cond_id, employee_id = doc
                try:
                    ok = False
                    if doc_scope == "funcionario" and employee_id:
                        ok = self._vincular_funcionario(
                            db,
                            cond_to_ged,
                            categoria,
                            caminho_local,
                            employee_id,
                            ref_date,
                        )
                    elif cond_id:
                        ok = self._vincular_empresa(
                            db,
                            cond_to_ged,
                            categoria,
                            caminho_local,
                            cond_id,
                            ref_date,
                        )
                    else:
                        ignorados += 1
                        continue

                    if ok:
                        vinculados += 1
                    else:
                        ignorados += 1

                except Exception as exc:
                    logger.error("HERMES: erro doc %s (%s): %s", doc_id, nome_arquivo, exc)
                    erros += 1

            db.commit()

            kits_atualizados = self._recalcular_completude_mes(db, ref_date)
            db.commit()

        logger.info(
            "HERMES %s: %d vinculados, %d ignorados, %d erros, %d kits atualizados",
            mes_ref,
            vinculados,
            ignorados,
            erros,
            kits_atualizados,
        )
        return {
            "mes_ref": mes_ref,
            "vinculados": vinculados,
            "ignorados": ignorados,
            "erros": erros,
            "kits_atualizados": kits_atualizados,
        }


# Singleton global
hermes = Hermes()
