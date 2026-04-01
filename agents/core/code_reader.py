"""
CodeReader — Lê e analisa arquivos do backend/frontend
aplicando os checklists das 10 skills.
"""
import os
import re
import ast
import json
from pathlib import Path
from typing import Optional


SKILLS_DIR = Path("/opt/conecta-pro/skills/codigo")
BACKEND_DIR = Path("/app/modules")
FRONTEND_DIR = Path("/opt/conecta-pro/frontend/src")
APP_DIR = Path("/opt/conecta-pro")


class CodeReader:
    """Lê código e aplica skills de auditoria."""

    def __init__(self):
        self.skills = self._carregar_skills()

    def _carregar_skills(self) -> dict:
        """Carrega todas as 10 skills do disco."""
        skills = {}
        if not SKILLS_DIR.exists():
            return skills
        for f in sorted(SKILLS_DIR.glob("*.md")):
            num = f.stem.split("-")[0].lstrip("0") or "0"
            try:
                skills[int(num)] = f.read_text(encoding="utf-8")
            except Exception:
                pass
        return skills

    def ler_modulo_backend(self, modulo: str) -> dict:
        """
        Lê todos os .py de um módulo do backend.
        modulo: ex 'financial', 'crm', 'people_management'
        """
        arquivos = {}
        modulo_dir = BACKEND_DIR / modulo
        if not modulo_dir.exists():
            # Buscar em host path como fallback
            host_dir = Path("/opt/conecta-pro/backend/modules") / modulo
            if host_dir.exists():
                modulo_dir = host_dir
            else:
                # Buscar por nome parcial no host
                base = Path("/opt/conecta-pro/backend/modules")
                if base.exists():
                    for d in base.iterdir():
                        if modulo.lower() in d.name.lower():
                            modulo_dir = d
                            break

        if not modulo_dir.exists():
            return arquivos

        for fpath in modulo_dir.rglob("*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                arquivos[str(fpath)] = fpath.read_text(
                    encoding="utf-8", errors="ignore"
                )
            except Exception:
                pass
        return arquivos

    def ler_modulo_frontend(self, modulo: str) -> dict:
        """Lê todos os .tsx/.ts de um módulo do frontend."""
        arquivos = {}
        for fpath in FRONTEND_DIR.rglob("*.tsx"):
            if modulo.lower() in str(fpath).lower() and \
               "node_modules" not in str(fpath):
                try:
                    arquivos[str(fpath)] = fpath.read_text(
                        encoding="utf-8", errors="ignore"
                    )
                except Exception:
                    pass
        return arquivos

    # ─── SKILL 03 — API RESTful ───────────────────────────────

    def skill03_api_restful(self, arquivos: dict) -> list:
        """Detecta: POSTs sem 201, verbos em paths."""
        bugs = []
        verb_pattern = re.compile(
            r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']'
            r'(/[^"\']*(?:create|update|delete|remove|fetch|'
            r'get-|list-|add-|edit-|set-)[^"\']*)["\']',
            re.IGNORECASE,
        )
        post_sem_201 = re.compile(
            r'@router\.post\((?![^)]*status_code)[^)]+\)',
            re.MULTILINE,
        )
        for fpath, content in arquivos.items():
            if not fpath.endswith("controller.py"):
                continue
            # POSTs sem 201
            matches = post_sem_201.findall(content)
            if matches:
                bugs.append({
                    "skill": 3,
                    "tipo": "post_sem_201",
                    "arquivo": fpath,
                    "ocorrencias": len(matches),
                    "descricao": f"{len(matches)} POSTs sem status_code=201",
                    "autocorrigivel": True,
                })
            # Verbos em paths
            for m in verb_pattern.finditer(content):
                linha = content[: m.start()].count("\n") + 1
                bugs.append({
                    "skill": 3,
                    "tipo": "verbo_em_path",
                    "arquivo": fpath,
                    "linha": linha,
                    "path": m.group(2),
                    "method": m.group(1).upper(),
                    "descricao": f"Verbo no path: {m.group(1).upper()} {m.group(2)}",
                    "autocorrigivel": False,
                })
        return bugs

    # ─── SKILL 05 — Banco ─────────────────────────────────────

    def skill05_banco(self, db_session) -> list:
        """Detecta: FKs sem índice, índices duplicados."""
        bugs = []
        try:
            result = db_session.execute("""
                SELECT tc.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND NOT EXISTS (
                    SELECT 1 FROM pg_indexes pi
                    WHERE pi.tablename = tc.table_name
                    AND pi.indexdef LIKE '%' || kcu.column_name || '%'
                )
            """).fetchall()
            if result:
                bugs.append({
                    "skill": 5,
                    "tipo": "fk_sem_indice",
                    "ocorrencias": len(result),
                    "detalhes": [f"{r[0]}.{r[1]}" for r in result],
                    "descricao": f"{len(result)} FKs sem índice",
                    "autocorrigivel": True,
                })
        except Exception as e:
            bugs.append({
                "skill": 5, "tipo": "erro_diagnostico",
                "descricao": str(e), "autocorrigivel": False,
            })
        return bugs

    # ─── SKILL 06 — Auth ──────────────────────────────────────

    def skill06_auth(self, arquivos: dict) -> list:
        """Detecta: controllers sem Depends(get_current_user)."""
        bugs = []
        auth_terms = [
            "CurrentActiveUser", "get_current_user", "current_user"
        ]
        route_pattern = re.compile(
            r'@router\.(get|post|put|delete|patch)'
        )
        for fpath, content in arquivos.items():
            if not fpath.endswith("controller.py"):
                continue
            has_routes = bool(route_pattern.search(content))
            has_auth = any(t in content for t in auth_terms)
            if has_routes and not has_auth:
                n = len(route_pattern.findall(content))
                bugs.append({
                    "skill": 6,
                    "tipo": "controller_sem_auth",
                    "arquivo": fpath,
                    "endpoints": n,
                    "descricao": f"{n} endpoints sem autenticação JWT",
                    "autocorrigivel": True,
                })
        return bugs

    # ─── SKILL 09 — UX ────────────────────────────────────────

    def skill09_ux(self, arquivos: dict) -> list:
        """Detecta: inputs sem aria-label."""
        bugs = []
        input_sem_label = re.compile(
            r'<(?:input|textarea|select)'
            r'(?![^>]*(?:aria-label|aria-labelledby))[^>]*>',
            re.IGNORECASE,
        )
        for fpath, content in arquivos.items():
            matches = input_sem_label.findall(content)
            if matches:
                bugs.append({
                    "skill": 9,
                    "tipo": "input_sem_aria_label",
                    "arquivo": fpath,
                    "ocorrencias": len(matches),
                    "descricao": f"{len(matches)} inputs sem aria-label",
                    "autocorrigivel": True,
                })
        return bugs

    # ─── SKILL 10 — Docs ──────────────────────────────────────

    def skill10_docs(self) -> list:
        """Detecta: CLAUDE.md desatualizado, paths errados."""
        bugs = []
        claude_md = APP_DIR / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")
            # Verificar data
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content)
            if date_match:
                from datetime import date, datetime
                last_update = datetime.strptime(
                    date_match.group(1), "%Y-%m-%d"
                ).date()
                days_old = (date.today() - last_update).days
                if days_old > 30:
                    bugs.append({
                        "skill": 10,
                        "tipo": "claude_md_desatualizado",
                        "dias": days_old,
                        "descricao": f"CLAUDE.md {days_old} dias desatualizado",
                        "autocorrigivel": False,
                    })
            # Path errado
            if "erp-conecta-mais" in content:
                bugs.append({
                    "skill": 10,
                    "tipo": "path_errado",
                    "arquivo": str(claude_md),
                    "descricao": "Path /opt/erp-conecta-mais encontrado",
                    "autocorrigivel": True,
                })
        return bugs

    def auditar_modulo(
        self,
        modulo: str,
        skills: list = None,
        db_session=None,
    ) -> dict:
        """
        Audita um módulo com as skills especificadas.
        Retorna dict com todos os bugs encontrados.
        """
        if skills is None:
            skills = [3, 6, 9, 10]

        resultado = {
            "modulo": modulo,
            "bugs": [],
            "total": 0,
            "autocorrigiveis": 0,
        }

        arquivos_backend = self.ler_modulo_backend(modulo)
        arquivos_frontend = self.ler_modulo_frontend(modulo)

        if 3 in skills:
            resultado["bugs"].extend(
                self.skill03_api_restful(arquivos_backend)
            )
        if 5 in skills and db_session:
            resultado["bugs"].extend(
                self.skill05_banco(db_session)
            )
        if 6 in skills:
            resultado["bugs"].extend(
                self.skill06_auth(arquivos_backend)
            )
        if 9 in skills:
            resultado["bugs"].extend(
                self.skill09_ux(arquivos_frontend)
            )
        if 10 in skills:
            resultado["bugs"].extend(self.skill10_docs())

        resultado["total"] = len(resultado["bugs"])
        resultado["autocorrigiveis"] = sum(
            1 for b in resultado["bugs"] if b.get("autocorrigivel")
        )
        return resultado
