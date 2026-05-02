"use client";

import { useState, useEffect, useCallback } from "react";

// ── tipos ─────────────────────────────────────────────────────────────────────

type PaymentType = "boleto" | "pix" | "darf" | "gps" | "ted_interno";
type PaymentStatus = "preparado" | "aprovado" | "executado" | "confirmado" | "cancelado" | "erro";

interface Payment {
  id: string;
  payment_type: PaymentType;
  valor: number;
  data_pagamento: string;
  status: PaymentStatus;
  inter_payment_id?: string;
  approved_at?: string;
  executed_at?: string;
  observacoes?: string;
  created_at: string;
}

interface SaldoLimite {
  limite_diario: number;
  consumido_hoje: number;
  disponivel_hoje: number;
}

// ── helpers ───────────────────────────────────────────────────────────────────

const API = "/api/v1/financeiro/inter/payments";

async function apiFetch(path: string, options?: RequestInit) {
  const token = localStorage.getItem("auth_token") || "";
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

const STATUS_COLOR: Record<PaymentStatus, string> = {
  preparado: "bg-yellow-100 text-yellow-800",
  aprovado: "bg-blue-100 text-blue-800",
  executado: "bg-purple-100 text-purple-800",
  confirmado: "bg-green-100 text-green-800",
  cancelado: "bg-gray-100 text-gray-600",
  erro: "bg-red-100 text-red-800",
};

const TYPE_LABEL: Record<PaymentType, string> = {
  boleto: "Boleto",
  pix: "PIX",
  darf: "DARF",
  gps: "GPS",
  ted_interno: "TED",
};

function StatusBadge({ status }: { status: PaymentStatus }) {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLOR[status] || "bg-gray-100 text-gray-600"}`}>
      {status.toUpperCase()}
    </span>
  );
}

function fmt(v: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);
}

// ── componente: formulário novo pagamento ─────────────────────────────────────

function NovoPagamentoForm({ onPrepared }: { onPrepared: () => void }) {
  const [type, setType] = useState<PaymentType>("pix");
  const [valor, setValor] = useState("");
  const [dataPgto, setDataPgto] = useState(() => new Date().toISOString().slice(0, 10));
  const [obs, setObs] = useState("");
  const [dest, setDest] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [confirmando, setConfirmando] = useState(false);

  const handleDestChange = (key: string, val: string) =>
    setDest((prev) => ({ ...prev, [key]: val }));

  const handleConfirmar = async () => {
    setLoading(true);
    setError("");
    try {
      await apiFetch(API, {
        method: "POST",
        body: JSON.stringify({
          payment_type: type,
          destinatario: dest,
          valor: parseFloat(valor),
          data_pagamento: dataPgto,
          observacoes: obs,
        }),
      });
      setConfirmando(false);
      setValor("");
      setDest({});
      onPrepared();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao preparar pagamento");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-[#0A2540] mb-4">Novo Pagamento</h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <select
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={type}
            onChange={(e) => { setType(e.target.value as PaymentType); setDest({}); }}
          >
            {Object.entries(TYPE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Valor (R$)</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            placeholder="0,00"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Data Pagamento</label>
          <input
            type="date"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={dataPgto}
            onChange={(e) => setDataPgto(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
          <input
            className="w-full border rounded-lg px-3 py-2 text-sm"
            value={obs}
            onChange={(e) => setObs(e.target.value)}
            placeholder="Opcional"
          />
        </div>
      </div>

      {/* Campos dinâmicos por tipo */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {type === "boleto" && (
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Código de Barras</label>
            <input
              className="w-full border rounded-lg px-3 py-2 text-sm font-mono"
              value={dest.codigo_barras || ""}
              onChange={(e) => handleDestChange("codigo_barras", e.target.value)}
              placeholder="Digite o código de barras"
            />
          </div>
        )}
        {type === "pix" && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo Chave</label>
              <select
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.tipo_chave || "CPF"}
                onChange={(e) => handleDestChange("tipo_chave", e.target.value)}
              >
                {["CPF", "CNPJ", "EMAIL", "TELEFONE", "EVP"].map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Chave PIX</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.chave || ""}
                onChange={(e) => handleDestChange("chave", e.target.value)}
                placeholder="Chave PIX do destinatário"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Recebedor</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.nome_recebedor || ""}
                onChange={(e) => handleDestChange("nome_recebedor", e.target.value)}
                placeholder="Nome (opcional)"
              />
            </div>
          </>
        )}
        {type === "darf" && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Código Receita</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.codigo_receita || ""}
                onChange={(e) => handleDestChange("codigo_receita", e.target.value)}
                placeholder="Ex: 0220"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Período Apuração</label>
              <input
                type="month"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.periodo_apuracao || ""}
                onChange={(e) => handleDestChange("periodo_apuracao", e.target.value)}
              />
            </div>
          </>
        )}
        {type === "gps" && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Código Pagamento</label>
              <input
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.codigo_pagamento || ""}
                onChange={(e) => handleDestChange("codigo_pagamento", e.target.value)}
                placeholder="Ex: 1910"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Competência</label>
              <input
                type="month"
                className="w-full border rounded-lg px-3 py-2 text-sm"
                value={dest.competencia || ""}
                onChange={(e) => handleDestChange("competencia", e.target.value)}
              />
            </div>
          </>
        )}
        {type === "ted_interno" && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Banco</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm" value={dest.banco || ""} onChange={(e) => handleDestChange("banco", e.target.value)} placeholder="Ex: 077" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Agência</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm" value={dest.agencia || ""} onChange={(e) => handleDestChange("agencia", e.target.value)} placeholder="0001" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Conta</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm" value={dest.conta || ""} onChange={(e) => handleDestChange("conta", e.target.value)} placeholder="370990072" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm" value={dest.nome || ""} onChange={(e) => handleDestChange("nome", e.target.value)} placeholder="Nome do titular" />
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-red-700 text-sm">
          ⚠️ {error}
        </div>
      )}

      {confirmando ? (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 mb-4">
          <p className="font-semibold text-amber-800 mb-2">⚠️ Confirme o pagamento</p>
          <p className="text-sm text-amber-700">
            Tipo: <strong>{TYPE_LABEL[type]}</strong> | Valor: <strong>{fmt(parseFloat(valor || "0"))}</strong>
            {type === "pix" && dest.chave && <> | Chave: <strong>{dest.chave}</strong></>}
            {type === "boleto" && dest.codigo_barras && <> | Código: <strong>{dest.codigo_barras.slice(0, 10)}...</strong></>}
          </p>
          <p className="text-xs text-amber-600 mt-2">
            Este é apenas a PREPARAÇÃO. Você precisará aprovar com OTP de email antes da execução.
          </p>
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleConfirmar}
              disabled={loading}
              className="bg-[#FF6B35] hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              {loading ? "Preparando..." : "Confirmar Preparação"}
            </button>
            <button
              onClick={() => setConfirmando(false)}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setConfirmando(true)}
          disabled={!valor || parseFloat(valor) <= 0}
          className="bg-[#0A2540] hover:bg-[#1a3a5c] text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-40"
        >
          Preparar Pagamento
        </button>
      )}
    </div>
  );
}

// ── componente: aprovação (OTP) ───────────────────────────────────────────────

function AprovacaoPagamento({ payment, onAction }: { payment: Payment; onAction: () => void }) {
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGerarOTP = async () => {
    setLoading(true);
    setError("");
    try {
      await apiFetch(`${API}/${payment.id}/gerar-otp`, { method: "POST" });
      setOtpSent(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao gerar OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleAprovarExecutar = async () => {
    if (!otpCode || otpCode.length !== 6) { setError("Digite o código de 6 dígitos"); return; }
    setLoading(true);
    setError("");
    try {
      await apiFetch(`${API}/${payment.id}/aprovar`, {
        method: "POST",
        body: JSON.stringify({ otp_code: otpCode }),
      });
      await apiFetch(`${API}/${payment.id}/executar`, { method: "POST" });
      onAction();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro na aprovação/execução");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelar = async () => {
    setLoading(true);
    try {
      await apiFetch(`${API}/${payment.id}/cancelar`, {
        method: "POST",
        body: JSON.stringify({ motivo: "Cancelado pelo usuário" }),
      });
      onAction();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro ao cancelar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-amber-50 border-2 border-amber-400 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">🔐</span>
        <h3 className="text-lg font-bold text-amber-900">Aprovação de Pagamento</h3>
      </div>
      <div className="bg-white rounded-lg p-4 mb-4 border border-amber-200">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div><span className="text-gray-500">Tipo:</span><br /><strong>{TYPE_LABEL[payment.payment_type]}</strong></div>
          <div><span className="text-gray-500">Valor:</span><br /><strong className="text-2xl text-red-600">{fmt(payment.valor)}</strong></div>
          <div><span className="text-gray-500">Data:</span><br /><strong>{payment.data_pagamento}</strong></div>
        </div>
      </div>
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-sm text-red-700">
        ⚠️ <strong>ATENÇÃO:</strong> Este pagamento será EXECUTADO imediatamente após aprovação.
        Verifique 2x os dados acima. Operação <strong>irreversível</strong>.
      </div>

      {!otpSent ? (
        <button
          onClick={handleGerarOTP}
          disabled={loading}
          className="bg-[#0A2540] text-white px-4 py-2 rounded-lg text-sm font-medium mr-2"
        >
          {loading ? "Enviando..." : "📧 Enviar código OTP por email"}
        </button>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-green-700">✅ Código enviado para jordansjesus@gmail.com. Digite o código:</p>
          <input
            type="text"
            maxLength={6}
            className="border-2 border-[#0A2540] rounded-lg px-4 py-3 text-2xl text-center font-mono tracking-widest w-40"
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
            placeholder="000000"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAprovarExecutar}
              disabled={loading || otpCode.length !== 6}
              className="bg-[#FF6B35] hover:bg-orange-600 text-white px-6 py-2 rounded-lg text-sm font-bold disabled:opacity-40"
            >
              {loading ? "Executando..." : "✅ Aprovar e Executar"}
            </button>
          </div>
        </div>
      )}

      {error && <p className="text-red-600 text-sm mt-3">⚠️ {error}</p>}

      <button
        onClick={handleCancelar}
        disabled={loading}
        className="mt-4 text-gray-500 hover:text-red-600 text-sm underline"
      >
        Cancelar pagamento
      </button>
    </div>
  );
}

// ── página principal ──────────────────────────────────────────────────────────

type Tab = "novo" | "preparados" | "aprovados" | "historico" | "audit";

export default function PagamentosPage() {
  const [tab, setTab] = useState<Tab>("preparados");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [saldo, setSaldo] = useState<SaldoLimite | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [auditLog, setAuditLog] = useState<unknown[]>([]);

  const fetchPayments = useCallback(async (statusFilter?: string) => {
    setLoading(true);
    try {
      const qs = statusFilter ? `?status_filter=${statusFilter}` : "";
      const data = await apiFetch(`${API}${qs}`);
      setPayments(data.payments || []);
    } catch {
      setPayments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSaldo = useCallback(async () => {
    try {
      const data = await apiFetch(`${API}/saldo-limite`);
      setSaldo(data);
    } catch {
      setSaldo(null);
    }
  }, []);

  useEffect(() => {
    fetchSaldo();
    if (tab === "preparados") fetchPayments("preparado");
    else if (tab === "aprovados") fetchPayments("aprovado");
    else if (tab === "historico") fetchPayments();
    else if (tab === "novo") setPayments([]);
  }, [tab, fetchPayments, fetchSaldo]);

  const fetchAudit = async (paymentId: string) => {
    try {
      const data = await apiFetch(`${API}/${paymentId}/audit`);
      setAuditLog(data.audit || []);
    } catch {
      setAuditLog([]);
    }
  };

  const TABS: { key: Tab; label: string }[] = [
    { key: "novo", label: "Novo Pagamento" },
    { key: "preparados", label: "Aguardando Aprovação" },
    { key: "aprovados", label: "Aguardando Execução" },
    { key: "historico", label: "Histórico" },
    { key: "audit", label: "Audit Log" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #0A2540 0%, #1a3a5c 100%)" }}
        className="px-6 py-8 text-white">
        <h1 className="text-2xl font-bold mb-1">Pagamentos Inter</h1>
        <p className="text-blue-200 text-sm">Módulo D7 — Operações de escrita com 2FA obrigatório</p>
        {saldo && (
          <div className="flex gap-6 mt-4">
            <div>
              <p className="text-xs text-blue-300">Limite Diário</p>
              <p className="text-lg font-bold">{fmt(saldo.limite_diario)}</p>
            </div>
            <div>
              <p className="text-xs text-blue-300">Usado Hoje</p>
              <p className="text-lg font-bold text-[#FF6B35]">{fmt(saldo.consumido_hoje)}</p>
            </div>
            <div>
              <p className="text-xs text-blue-300">Disponível Hoje</p>
              <p className="text-lg font-bold text-green-300">{fmt(saldo.disponivel_hoje)}</p>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b bg-white px-6">
        <div className="flex gap-6">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => { setTab(t.key); setSelectedPayment(null); }}
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? "border-[#FF6B35] text-[#FF6B35]"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Conteúdo */}
      <div className="p-6 max-w-5xl mx-auto">
        {tab === "novo" && (
          <NovoPagamentoForm onPrepared={() => { setTab("preparados"); fetchSaldo(); }} />
        )}

        {(tab === "preparados" || tab === "aprovados" || tab === "historico") && (
          <div className="space-y-4">
            {selectedPayment && tab === "preparados" && (
              <AprovacaoPagamento
                payment={selectedPayment}
                onAction={() => { setSelectedPayment(null); fetchPayments("preparado"); fetchSaldo(); }}
              />
            )}
            {loading ? (
              <div className="text-center py-12 text-gray-500">Carregando...</div>
            ) : payments.length === 0 ? (
              <div className="text-center py-12 text-gray-400">Nenhum pagamento encontrado</div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-gray-600 font-medium">Tipo</th>
                      <th className="px-4 py-3 text-right text-gray-600 font-medium">Valor</th>
                      <th className="px-4 py-3 text-left text-gray-600 font-medium">Data</th>
                      <th className="px-4 py-3 text-left text-gray-600 font-medium">Status</th>
                      <th className="px-4 py-3 text-left text-gray-600 font-medium">Inter ID</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {payments.map((p) => (
                      <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 font-medium">{TYPE_LABEL[p.payment_type]}</td>
                        <td className="px-4 py-3 text-right font-mono">{fmt(p.valor)}</td>
                        <td className="px-4 py-3">{p.data_pagamento}</td>
                        <td className="px-4 py-3"><StatusBadge status={p.status} /></td>
                        <td className="px-4 py-3 text-xs text-gray-400 font-mono">{p.inter_payment_id || "—"}</td>
                        <td className="px-4 py-3">
                          {p.status === "preparado" && (
                            <button
                              onClick={() => setSelectedPayment(p)}
                              className="text-xs bg-[#FF6B35] text-white px-3 py-1 rounded-full hover:bg-orange-600"
                            >
                              Aprovar
                            </button>
                          )}
                          {p.status === "aprovado" && (
                            <button
                              onClick={async () => {
                                try {
                                  await apiFetch(`${API}/${p.id}/executar`, { method: "POST" });
                                  fetchPayments("aprovado");
                                } catch (e: unknown) {
                                  alert(e instanceof Error ? e.message : "Erro");
                                }
                              }}
                              className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700"
                            >
                              Executar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {tab === "audit" && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <p className="text-sm text-gray-600 mb-3">Digite o ID do pagamento para ver o audit log:</p>
              <div className="flex gap-2">
                <input
                  id="audit-id-input"
                  className="border rounded-lg px-3 py-2 text-sm flex-1 font-mono"
                  placeholder="UUID do pagamento"
                />
                <button
                  onClick={() => {
                    const input = document.getElementById("audit-id-input") as HTMLInputElement;
                    if (input?.value) fetchAudit(input.value);
                  }}
                  className="bg-[#0A2540] text-white px-4 py-2 rounded-lg text-sm"
                >
                  Buscar
                </button>
              </div>
            </div>
            {auditLog.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left">Status</th>
                      <th className="px-4 py-3 text-left">IP</th>
                      <th className="px-4 py-3 text-left">Motivo</th>
                      <th className="px-4 py-3 text-left">Quando</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {(auditLog as Array<{status_from?: string; status_to: string; ip_address?: string; motivo?: string; created_at: string}>).map((entry, i) => (
                      <tr key={i}>
                        <td className="px-4 py-3">
                          <span className="text-gray-400">{entry.status_from || "—"}</span>
                          {" → "}
                          <span className="font-medium text-[#0A2540]">{entry.status_to}</span>
                        </td>
                        <td className="px-4 py-3 text-gray-500 font-mono text-xs">{entry.ip_address || "—"}</td>
                        <td className="px-4 py-3 text-gray-600">{entry.motivo || "—"}</td>
                        <td className="px-4 py-3 text-gray-400 text-xs">{new Date(entry.created_at).toLocaleString("pt-BR")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
