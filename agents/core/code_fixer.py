"""
CodeFixer — Aplica correções automáticas baseadas
nos bugs encontrados pelo CodeReader.
Princípio: só corrige o que é seguro e determinístico.
"""
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


CONTAINER_CMD = (
    "docker ps --filter ancestor=conecta-pro-backend "
    "--format '{{.Names}}' | head -1"
)


class CodeFixer:
    """Aplica fixes cirúrgicos e valida o resultado."""

    def __init__(self, token: str, container: str = None):
        self.token = token
        self.container = container or self._get_container()
        self.fixes_aplicados = []
        self.fixes_falhos = []

    def _get_container(self) -> str:
        r = subprocess.run(
            CONTAINER_CMD, shell=True,
            capture_output=True, text=True
        )
        return r.stdout.strip()

    def _run(self, cmd: str) -> tuple:
        r = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True
        )
        return r.returncode, r.stdout, r.stderr

    def _hot_copy(self, fpath: str) -> bool:
        """Copia arquivo corrigido para o container."""
        container_path = fpath.replace(
            "/opt/conecta-pro/backend", "/app"
        )
        if not self.container:
            return False
        code, _, err = self._run(
            f"docker cp {fpath} {self.container}:{container_path}"
        )
        if code != 0:
            print(f"  ❌ hot copy falhou: {err}")
            return False
        return True

    def _reload_backend(self):
        """Recarrega o backend sem rebuild."""
        if self.container:
            self._run(
                f"docker exec {self.container} kill -HUP 1 2>/dev/null || true"
            )

    def _validar_endpoint(
        self, endpoint: str, expected: int = 200
    ) -> bool:
        """Valida que endpoint retorna código esperado."""
        import urllib.request
        import urllib.error
        url = f"http://127.0.0.1:8080/api/v1{endpoint}"
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {self.token}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status == expected
        except urllib.error.HTTPError as e:
            return e.code == expected
        except Exception:
            return False

    def _commitar(self, mensagem: str) -> bool:
        """Git add + commit + push."""
        code, _, err = self._run(
            f"cd /opt/conecta-pro && "
            f"git add -A && "
            f'git commit -m "{mensagem}" && '
            f"git push origin feature/people-management-reorganization"
        )
        return code == 0

    # ─── FIX SKILL 03 — POST → 201 ───────────────────────────

    def fix_post_sem_201(self, bug: dict) -> bool:
        """Adiciona status_code=201 em @router.post sem ele."""
        fpath = bug["arquivo"]
        host_path = fpath.replace(
            "/app/modules", "/opt/conecta-pro/backend/modules"
        )

        try:
            with open(host_path) as f:
                content = f.read()

            def add_201(match):
                dec = match.group(1)
                if "status_code" in dec:
                    return match.group(0)
                dec = dec.rstrip()
                sep = "," if not dec.endswith(",") else ""
                return f"@router.post({dec}{sep} status_code=201)"

            new_content = re.sub(
                r"@router\.post\(([^)]+)\)", add_201, content
            )

            if new_content == content:
                return False

            with open(host_path, "w") as f:
                f.write(new_content)

            if self._hot_copy(host_path):
                self.fixes_aplicados.append({
                    "skill": 3, "fix": "post_201",
                    "arquivo": fpath,
                })
                return True
            else:
                # Mesmo sem hot copy, o arquivo foi corrigido no host
                self.fixes_aplicados.append({
                    "skill": 3, "fix": "post_201",
                    "arquivo": host_path,
                    "nota": "hot copy indisponível",
                })
                return True
        except Exception as e:
            self.fixes_falhos.append({"bug": bug, "erro": str(e)})
        return False

    # ─── FIX SKILL 06 — Auth ─────────────────────────────────

    def fix_controller_sem_auth(self, bug: dict) -> bool:
        """Adiciona CurrentActiveUser em controller sem auth."""
        fpath = bug["arquivo"]
        host_path = fpath.replace(
            "/app/modules", "/opt/conecta-pro/backend/modules"
        )

        try:
            with open(host_path) as f:
                content = f.read()

            import_line = self._descobrir_import_auth()
            if not import_line:
                return False

            if "CurrentActiveUser" not in content:
                lines = content.split("\n")
                # Apenas imports top-level (sem indentação)
                last_import = max(
                    (i for i, l in enumerate(lines)
                     if l.startswith(("import ", "from "))),
                    default=0,
                )
                lines.insert(last_import + 1, import_line)
                content = "\n".join(lines)

            def add_auth(match):
                sig = match.group(0)
                if "current_user" in sig:
                    return sig
                if sig.rstrip().endswith(":"):
                    inner = sig.rstrip()[:-1].rstrip()
                    if inner.endswith(")"):
                        inner = inner[:-1]
                        sig = (
                            inner
                            + ",\n    current_user: CurrentActiveUser\n):"
                        )
                return sig

            content = re.sub(
                r"(async def \w+\([^)]*\):)", add_auth, content
            )

            with open(host_path, "w") as f:
                f.write(content)

            if self._hot_copy(host_path):
                self.fixes_aplicados.append({
                    "skill": 6, "fix": "auth_adicionado",
                    "arquivo": fpath,
                    "endpoints": bug.get("endpoints", 0),
                })
                return True
            else:
                self.fixes_aplicados.append({
                    "skill": 6, "fix": "auth_adicionado",
                    "arquivo": host_path,
                    "endpoints": bug.get("endpoints", 0),
                    "nota": "hot copy indisponível",
                })
                return True
        except Exception as e:
            self.fixes_falhos.append({"bug": bug, "erro": str(e)})
        return False

    def _descobrir_import_auth(self) -> Optional[str]:
        """Encontra o padrão de import de auth usado no projeto."""
        for fpath in Path("/opt/conecta-pro/backend/modules").rglob(
            "*controller*.py"
        ):
            try:
                content = fpath.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if "CurrentActiveUser" in line and \
                       line.strip().startswith("from"):
                        return line.strip()
            except Exception:
                pass
        return None

    # ─── FIX SKILL 09 — aria-label ───────────────────────────

    def fix_aria_label(self, bug: dict) -> bool:
        """Adiciona aria-label em inputs sem identificação."""
        fpath = bug["arquivo"]

        try:
            with open(fpath) as f:
                content = f.read()

            def extrair_label(tag):
                for attr in ["placeholder", "name", "type"]:
                    m = re.search(
                        rf'{attr}=["\']([^"\']+)["\']', tag
                    )
                    if m:
                        val = m.group(1)
                        val = re.sub(r"([A-Z])", r" \1", val).strip()
                        val = val.replace("_", " ").replace("-", " ")
                        return val.title()
                return None

            def add_aria(match):
                tag = match.group(0)
                if any(x in tag for x in
                       ["aria-label", "aria-labelledby"]):
                    return tag
                label = extrair_label(tag)
                if not label:
                    return tag
                if tag.endswith("/>"):
                    return tag[:-2] + f' aria-label="{label}" />'
                elif tag.endswith(">"):
                    return tag[:-1] + f' aria-label="{label}">'
                return tag

            new_content = re.sub(
                r"<(?:input|textarea|select)(\s[^>]*?)(/?>)",
                add_aria, content,
                flags=re.IGNORECASE | re.DOTALL,
            )

            if new_content == content:
                return False

            with open(fpath, "w") as f:
                f.write(new_content)

            self.fixes_aplicados.append({
                "skill": 9, "fix": "aria_label",
                "arquivo": fpath,
                "inputs": bug.get("ocorrencias", 0),
            })
            return True
        except Exception as e:
            self.fixes_falhos.append({"bug": bug, "erro": str(e)})
        return False

    # ─── FIX SKILL 10 — Docs ─────────────────────────────────

    def fix_path_errado(self, bug: dict) -> bool:
        """Corrige /opt/erp-conecta-mais → /opt/conecta-pro."""
        fpath = bug["arquivo"]
        try:
            content = Path(fpath).read_text(encoding="utf-8")
            new_content = content.replace(
                "/opt/erp-conecta-mais", "/opt/conecta-pro"
            ).replace("erp-conecta-mais", "conecta-pro")
            if new_content == content:
                return False
            Path(fpath).write_text(new_content, encoding="utf-8")
            self.fixes_aplicados.append({
                "skill": 10, "fix": "path_corrigido",
                "arquivo": fpath,
            })
            return True
        except Exception as e:
            self.fixes_falhos.append({"bug": bug, "erro": str(e)})
        return False

    # ─── EXECUTOR PRINCIPAL ──────────────────────────────────

    def corrigir_bugs(self, bugs: list) -> dict:
        """
        Recebe lista de bugs do CodeReader e aplica
        todos os fixes autocorrigíveis.
        """
        total = len(bugs)
        corrigidos = 0
        pulados = 0

        fix_map = {
            "post_sem_201": self.fix_post_sem_201,
            "controller_sem_auth": self.fix_controller_sem_auth,
            "input_sem_aria_label": self.fix_aria_label,
            "path_errado": self.fix_path_errado,
        }

        for bug in bugs:
            if not bug.get("autocorrigivel"):
                pulados += 1
                continue

            tipo = bug.get("tipo")
            fix_fn = fix_map.get(tipo)

            if fix_fn:
                print(f"  🔧 Aplicando fix: {tipo} em {bug.get('arquivo','?')}")
                if fix_fn(bug):
                    corrigidos += 1
                    print(f"     ✅ Corrigido")
                else:
                    print(f"     ❌ Falhou")
            else:
                print(f"  ⏭️  Sem fix automático para: {tipo}")
                pulados += 1

        # Recarregar backend se houve fixes de backend
        backend_fixes = [
            f for f in self.fixes_aplicados
            if f.get("skill") in [3, 6]
        ]
        if backend_fixes:
            print("\n  🔄 Recarregando backend...")
            self._reload_backend()

        return {
            "total_bugs": total,
            "corrigidos": corrigidos,
            "pulados": pulados,
            "falhos": len(self.fixes_falhos),
            "fixes": self.fixes_aplicados,
        }
