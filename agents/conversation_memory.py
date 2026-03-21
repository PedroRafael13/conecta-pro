#!/usr/bin/env python3
"""
Conversation Memory — Persiste histórico de conversas Jordan ↔ Assistente.

Armazena no PostgreSQL:
- Histórico de mensagens com contexto
- Ações executadas e resultados
- Preferências aprendidas de Jordan
"""

import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path("/opt/conecta-pro")


def _get_pg_ip():
    try:
        out = subprocess.run("docker inspect conecta-pro-postgres",
                             shell=True, capture_output=True, text=True, timeout=10).stdout
        data = json.loads(out)
        for info in data[0]["NetworkSettings"]["Networks"].values():
            if info.get("IPAddress"):
                return info["IPAddress"]
    except Exception:
        pass
    return None


def _get_pg_password():
    env = PROJECT_DIR / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD=") and "STAGING" not in line:
            return line.split("=", 1)[1]
    return ""


def _get_conn():
    import psycopg2
    ip = _get_pg_ip()
    pw = _get_pg_password()
    return psycopg2.connect(host=ip, port="5432", dbname="conecta_pro",
                            user="postgres", password=pw, connect_timeout=5)


class ConversationMemory:
    """Gerencia memória de conversas com PostgreSQL."""

    def __init__(self, chat_id: str, user_id: str = "jordan"):
        self.chat_id = str(chat_id)
        self.user_id = user_id

    def save_message(self, role: str, content: str,
                     action_executed: str = None, action_result: dict = None,
                     metadata: dict = None):
        """Salva uma mensagem na conversa."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO assistant_conversations
            (id, user_id, chat_id, role, content, action_executed, action_result, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                str(uuid.uuid4()),
                self.user_id,
                self.chat_id,
                role,
                content[:5000],  # limita tamanho
                action_executed,
                json.dumps(action_result) if action_result else None,
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_recent_messages(self, limit: int = 20) -> list[dict]:
        """Retorna as últimas N mensagens da conversa."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT role, content, action_executed, action_result, created_at
            FROM assistant_conversations
            WHERE chat_id = %s
            ORDER BY created_at DESC LIMIT %s""",
            (self.chat_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        messages = []
        for role, content, action, result, created_at in reversed(rows):
            msg = {
                "role": role,
                "content": content,
                "timestamp": created_at.isoformat() if created_at else None,
            }
            if action:
                msg["action_executed"] = action
            if result:
                msg["action_result"] = result if isinstance(result, dict) else json.loads(result)
            messages.append(msg)
        return messages

    def get_context_window(self, limit: int = 20) -> str:
        """Retorna contexto formatado para enviar ao LLM."""
        messages = self.get_recent_messages(limit)
        if not messages:
            return "(sem histórico de conversa)"

        lines = []
        for msg in messages:
            role_label = "Jordan" if msg["role"] == "user" else "Assistente"
            lines.append(f"[{role_label}] {msg['content']}")
            if msg.get("action_executed"):
                result = msg.get("action_result", {})
                success = result.get("success", "?")
                lines.append(f"  → Ação: {msg['action_executed']} (sucesso: {success})")
        return "\n".join(lines)

    def get_actions_history(self, limit: int = 10) -> list[dict]:
        """Retorna últimas ações executadas."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT action_executed, action_result, created_at
            FROM assistant_conversations
            WHERE chat_id = %s AND action_executed IS NOT NULL
            ORDER BY created_at DESC LIMIT %s""",
            (self.chat_id, limit),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "action": action,
                "result": result if isinstance(result, dict) else json.loads(result) if result else {},
                "timestamp": ts.isoformat() if ts else None,
            }
            for action, result, ts in rows
        ]

    # =========================================================================
    # PREFERÊNCIAS
    # =========================================================================

    def get_preferences(self) -> dict:
        """Retorna preferências salvas de Jordan."""
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT preferences, learned_patterns FROM assistant_preferences WHERE user_id = %s",
            (self.user_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            prefs = row[0] if isinstance(row[0], dict) else json.loads(row[0]) if row[0] else {}
            patterns = row[1] if isinstance(row[1], list) else json.loads(row[1]) if row[1] else []
            return {"preferences": prefs, "learned_patterns": patterns}
        return {"preferences": {}, "learned_patterns": []}

    def update_preferences(self, key: str, value):
        """Atualiza uma preferência de Jordan."""
        conn = _get_conn()
        cur = conn.cursor()

        # Upsert
        cur.execute(
            """INSERT INTO assistant_preferences (id, user_id, preferences, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET preferences = assistant_preferences.preferences || %s,
                updated_at = NOW()""",
            (
                str(uuid.uuid4()),
                self.user_id,
                json.dumps({key: value}),
                json.dumps({key: value}),
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

    def learn_pattern(self, pattern: str):
        """Registra um padrão aprendido sobre Jordan."""
        conn = _get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT learned_patterns FROM assistant_preferences WHERE user_id = %s",
            (self.user_id,),
        )
        row = cur.fetchone()

        if row:
            patterns = row[0] if isinstance(row[0], list) else json.loads(row[0]) if row[0] else []
            if pattern not in patterns:
                patterns.append(pattern)
                cur.execute(
                    "UPDATE assistant_preferences SET learned_patterns = %s, updated_at = NOW() WHERE user_id = %s",
                    (json.dumps(patterns), self.user_id),
                )
        else:
            cur.execute(
                "INSERT INTO assistant_preferences (id, user_id, learned_patterns, updated_at) VALUES (%s, %s, %s, NOW())",
                (str(uuid.uuid4()), self.user_id, json.dumps([pattern])),
            )

        conn.commit()
        cur.close()
        conn.close()

    def get_conversation_stats(self) -> dict:
        """Estatísticas da conversa."""
        conn = _get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT COUNT(*), MIN(created_at), MAX(created_at) "
            "FROM assistant_conversations WHERE chat_id = %s",
            (self.chat_id,),
        )
        total, first, last = cur.fetchone()

        cur.execute(
            "SELECT COUNT(*) FROM assistant_conversations "
            "WHERE chat_id = %s AND action_executed IS NOT NULL",
            (self.chat_id,),
        )
        actions = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "total_messages": total or 0,
            "total_actions": actions or 0,
            "first_message": first.isoformat() if first else None,
            "last_message": last.isoformat() if last else None,
        }


if __name__ == "__main__":
    # Teste básico
    mem = ConversationMemory(chat_id="5536961034")

    # Salvar mensagens de teste
    mem.save_message("user", "Como está o sistema?")
    mem.save_message("assistant", "Sistema operacional. 21 containers healthy, RAM 56%, disco 11%.")
    mem.save_message(
        "user", "Roda os testes do financeiro",
        action_executed="execute_tests",
        action_result={"success": True, "summary": "42 passed, 0 failed"},
    )

    # Recuperar
    msgs = mem.get_recent_messages(5)
    print(f"Mensagens salvas: {len(msgs)}")
    for m in msgs:
        print(f"  [{m['role']}] {m['content'][:60]}")

    # Preferências
    mem.update_preferences("notification_level", "critical_only")
    mem.learn_pattern("Jordan prefere respostas curtas e diretas")

    prefs = mem.get_preferences()
    print(f"\nPreferências: {prefs['preferences']}")
    print(f"Padrões: {prefs['learned_patterns']}")

    stats = mem.get_conversation_stats()
    print(f"\nStats: {stats}")
