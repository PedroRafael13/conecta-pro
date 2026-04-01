"""Seed data para GED: kits, itens, clientes e limpeza de pastas teste."""

import asyncio
import os
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DB_PASSWORD = os.environ.get("DB_PASSWORD", "changeme")  # pragma: allowlist secret
DB_URL = f"postgresql+asyncpg://postgres:{DB_PASSWORD}@postgres:5432/conecta_pro"


async def main() -> None:
    """Executa seed completo."""
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        # Get existing kit
        r = await conn.execute(text("SELECT id, condominio_id FROM document_kits WHERE nome ILIKE '%admiss%' LIMIT 1"))
        row = r.first()
        kit_admissao_id = str(row[0]) if row else None
        condo_id = str(row[1]) if row else str(uuid4())
        print(f"Kit Admissao: {kit_admissao_id}, condo: {condo_id}")

        # Activate kit admissao
        if kit_admissao_id:
            await conn.execute(
                text("UPDATE document_kits SET status = 'ATIVO' WHERE id = :id"), {"id": kit_admissao_id}
            )

        # Items admissao
        items_admissao = [
            ("RG", "Copia do documento de identidade", 1, "DOCUMENTO_PESSOAL"),
            ("CPF", "Copia do Cadastro de Pessoa Fisica", 2, "DOCUMENTO_PESSOAL"),
            ("CTPS", "Carteira de Trabalho e Previdencia Social", 3, "REGISTRO"),
            ("Comprovante de Residencia", "Conta de agua, luz ou telefone recente", 4, "COMPROVANTE"),
            ("Foto 3x4", "2 fotos recentes fundo branco", 5, "FOTO"),
            ("PIS/PASEP", "Numero de inscricao PIS/PASEP", 6, "REGISTRO"),
            ("Dados Bancarios", "Agencia e conta para pagamento", 7, "COMPROVANTE"),
            ("ASO Admissional", "Atestado de Saude Ocupacional NR-7", 8, "ATESTADO"),
            ("Contrato de Trabalho", "Contrato CLT assinado pelas partes", 9, "CONTRATO"),
            ("Recibo de Uniforme", "Recibo entrega 2 uniformes CCT Cl. 11", 10, "TERMO"),
            ("Recibo de Cracha", "Recibo entrega cracha CCT Cl. 11 par 3", 11, "TERMO"),
            ("Ciencia CCT 2026", "Recibo ciencia Convencao Coletiva", 12, "DECLARACAO"),
        ]
        if kit_admissao_id:
            for nome, desc, ordem, tipo in items_admissao:
                await conn.execute(
                    text(
                        "INSERT INTO document_kit_items "
                        "(id, kit_id, condominio_id, codigo, nome, descricao, tipo, prioridade, ordem, created_at) "
                        "VALUES (:id, :kid, :cid, :cod, :nome, :desc, :tipo, :prio, :ord, NOW()) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {
                        "id": str(uuid4()),
                        "kid": kit_admissao_id,
                        "cid": condo_id,
                        "cod": f"ADM-{ordem:03d}",
                        "nome": nome,
                        "desc": desc,
                        "tipo": tipo,
                        "prio": "OBRIGATORIO",
                        "ord": ordem,
                    },
                )
            print(f"  Admissao: {len(items_admissao)} itens")

        # Kit Demissao
        kit_dem_id = str(uuid4())
        await conn.execute(
            text(
                "INSERT INTO document_kits "
                "(id, condominio_id, codigo, nome, descricao, tipo, status, is_template, created_at, updated_at) "
                "VALUES (:id, :cid, 'KIT-DEM', 'Kit de Demissao', "
                "'Documentos obrigatorios para rescisao contratual CLT e CCT 2026', "
                "'DEMISSAO', 'ATIVO', true, NOW(), NOW()) "
                "ON CONFLICT DO NOTHING"
            ),
            {"id": kit_dem_id, "cid": condo_id},
        )
        items_dem = [
            ("Aviso Previo", "Aviso previo indenizado ou trabalhado", 1, "TERMO"),
            ("Termo de Rescisao", "TRCT assinado pelas partes", 2, "TERMO"),
            ("Recibo Devolucao Uniforme", "CCT Clausula 11 par. 2", 3, "TERMO"),
            ("Comprovante Pagamento Rescisao", "Verbas rescisorias", 4, "COMPROVANTE"),
            ("Guia FGTS Rescisorio", "Guia recolhimento FGTS", 5, "COMPROVANTE"),
            ("Homologacao SINDECOMPRESTS", "Contratos +1 ano CCT Cl. 21", 6, "DECLARACAO"),
            ("ASO Demissional", "Atestado Saude Ocupacional NR-7", 7, "ATESTADO"),
        ]
        for nome, desc, ordem, tipo in items_dem:
            await conn.execute(
                text(
                    "INSERT INTO document_kit_items "
                    "(id, kit_id, condominio_id, codigo, nome, descricao, tipo, prioridade, ordem, created_at) "
                    "VALUES (:id, :kid, :cid, :cod, :nome, :desc, :tipo, :prio, :ord, NOW()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(uuid4()),
                    "kid": kit_dem_id,
                    "cid": condo_id,
                    "cod": f"DEM-{ordem:03d}",
                    "nome": nome,
                    "desc": desc,
                    "tipo": tipo,
                    "prio": "OBRIGATORIO",
                    "ord": ordem,
                },
            )
        print(f"  Demissao: {len(items_dem)} itens")

        # Kit Afastamento
        kit_afast_id = str(uuid4())
        await conn.execute(
            text(
                "INSERT INTO document_kits "
                "(id, condominio_id, codigo, nome, descricao, tipo, status, is_template, created_at, updated_at) "
                "VALUES (:id, :cid, 'KIT-AFT', 'Kit de Afastamento Medico', "
                "'Documentos para registro de afastamentos por saude ou acidente', "
                "'AFASTAMENTO', 'ATIVO', true, NOW(), NOW()) "
                "ON CONFLICT DO NOTHING"
            ),
            {"id": kit_afast_id, "cid": condo_id},
        )
        items_afast = [
            ("Atestado Medico", "Atestado medico original", 1, "ATESTADO"),
            ("CAT", "Comunicacao de Acidente de Trabalho", 2, "FORMULARIO"),
            ("Requerimento INSS", "Solicitacao auxilio-doenca", 3, "FORMULARIO"),
            ("Comprovante INSS", "Comprovante encaminhamento INSS", 4, "COMPROVANTE"),
            ("Laudo Medico", "Laudo medico detalhado", 5, "LAUDO"),
        ]
        for nome, desc, ordem, tipo in items_afast:
            await conn.execute(
                text(
                    "INSERT INTO document_kit_items "
                    "(id, kit_id, condominio_id, codigo, nome, descricao, tipo, prioridade, ordem, created_at) "
                    "VALUES (:id, :kid, :cid, :cod, :nome, :desc, :tipo, :prio, :ord, NOW()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(uuid4()),
                    "kid": kit_afast_id,
                    "cid": condo_id,
                    "cod": f"AFT-{ordem:03d}",
                    "nome": nome,
                    "desc": desc,
                    "tipo": tipo,
                    "prio": "OBRIGATORIO",
                    "ord": ordem,
                },
            )
        print(f"  Afastamento: {len(items_afast)} itens")

        # Kit Mensal
        kit_mensal_id = str(uuid4())
        await conn.execute(
            text(
                "INSERT INTO document_kits "
                "(id, condominio_id, codigo, nome, descricao, tipo, status, is_template, created_at, updated_at) "
                "VALUES (:id, :cid, 'KIT-MEN', 'Kit Mensal - Folha de Pagamento', "
                "'Documentos mensais pagamento e beneficios CCT 2026', "
                "'OUTRO', 'ATIVO', true, NOW(), NOW()) "
                "ON CONFLICT DO NOTHING"
            ),
            {"id": kit_mensal_id, "cid": condo_id},
        )
        items_mensal = [
            ("Contracheque", "Contracheque assinado", 1, "COMPROVANTE"),
            ("Folha de Ponto", "Folha de ponto assinada", 2, "REGISTRO"),
            ("Comprovante VT", "Pagamento vale-transporte", 3, "COMPROVANTE"),
            ("Comprovante VR", "Pagamento vale-refeicao", 4, "COMPROVANTE"),
            ("Comprovante Plano Odonto", "CCT Clausula 30", 5, "COMPROVANTE"),
        ]
        for nome, desc, ordem, tipo in items_mensal:
            await conn.execute(
                text(
                    "INSERT INTO document_kit_items "
                    "(id, kit_id, condominio_id, codigo, nome, descricao, tipo, prioridade, ordem, created_at) "
                    "VALUES (:id, :kid, :cid, :cod, :nome, :desc, :tipo, :prio, :ord, NOW()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(uuid4()),
                    "kid": kit_mensal_id,
                    "cid": condo_id,
                    "cod": f"MEN-{ordem:03d}",
                    "nome": nome,
                    "desc": desc,
                    "tipo": tipo,
                    "prio": "OBRIGATORIO",
                    "ord": ordem,
                },
            )
        print(f"  Mensal: {len(items_mensal)} itens")

        # GED Clients
        clients = [
            ("River Park Residencial Clube", "CONDOMINIO", None, "Manaus, AM", "Sindico", None, "(92) 99999-0001"),
            ("Condominio Residencial Bellavile", "CONDOMINIO", None, "Manaus, AM", "Sindico", None, "(92) 99999-0002"),
            (
                "Conecta Mais - Seguranca e Tecnologia",
                "EMPRESA",
                "35.710.481/0001-03",
                "Manaus, AM",
                "Jordan Santos",
                "administracao@conectamaistech.com.br",
                "(92) 9 9348-5518",
            ),
        ]
        for name, tipo, cnpj, addr, contact, email, phone in clients:
            await conn.execute(
                text(
                    "INSERT INTO ged_clients "
                    "(id, name, type, cnpj, address, contact_name, contact_email, contact_phone, "
                    "portal_access_enabled, is_active, created_at, updated_at) "
                    "VALUES (:id, :name, :tipo, :cnpj, :addr, :contact, :email, :phone, "
                    "false, true, NOW(), NOW()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(uuid4()),
                    "name": name,
                    "tipo": tipo,
                    "cnpj": cnpj,
                    "addr": addr,
                    "contact": contact,
                    "email": email,
                    "phone": phone,
                },
            )
        print(f"Clientes GED: {len(clients)} criados")

        # Clean test folders
        r = await conn.execute(
            text(
                "DELETE FROM ged_folders WHERE code LIKE 'FLD-%' "
                "AND id NOT IN (SELECT DISTINCT folder_id FROM ged_documents WHERE folder_id IS NOT NULL) "
                "RETURNING name"
            )
        )
        deleted = r.fetchall()
        print(f"Pastas teste removidas: {len(deleted)}")

        # Final counts
        for tbl, label in [
            ("ged_folders", "Pastas"),
            ("document_kits", "Kits"),
            ("document_kit_items", "Itens"),
            ("ged_clients", "Clientes"),
        ]:
            r = await conn.execute(text(f"SELECT COUNT(*) FROM {tbl}"))
            print(f"  {label}: {r.scalar()}")

    await engine.dispose()
    print("Seed completo!")


asyncio.run(main())
