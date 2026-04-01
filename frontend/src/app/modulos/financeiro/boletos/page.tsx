'use client';

import { useState, useCallback, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  FileText,
  Copy,
  Download,
  RefreshCw,
  CheckCircle,
  Plus,
  ExternalLink,
  Barcode,
  QrCode,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn, formatCurrency, formatDate } from '@/lib/utils';
import { emitirBoleto, listarBoletos } from '@/services/banking/bankingService';
import type { BoletoResponse, BoletoListItem } from '@/services/banking/bankingService';

// ─── Cores dos bancos ────────────────────────────────────────────────────────
const BANK_COLORS: Record<string, string> = {
  '403': '#e85d26', // Cora — laranja
  '077': '#00a859', // Inter — verde
};

const BANK_NAMES: Record<string, string> = {
  '403': 'Banco Cora',
  '077': 'Banco Inter',
};

// ─── Máscara CPF/CNPJ ────────────────────────────────────────────────────────
function maskDocument(value: string): string {
  const digits = value.replace(/\D/g, '').slice(0, 14);
  if (digits.length <= 11) {
    return digits
      .replace(/^(\d{3})(\d)/, '$1.$2')
      .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3-$4');
  }
  return digits
    .replace(/^(\d{2})(\d)/, '$1.$2')
    .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/^(\d{2})\.(\d{3})\.(\d{3})(\d)/, '$1.$2.$3/$4')
    .replace(/^(\d{2})\.(\d{3})\.(\d{3})\/(\d{4})(\d)/, '$1.$2.$3/$4-$5');
}

// ─── Badge de status ─────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    paid: { label: 'Pago', cls: 'bg-green-500/15 text-green-600 border-green-500/30' },
    pago: { label: 'Pago', cls: 'bg-green-500/15 text-green-600 border-green-500/30' },
    pending: { label: 'Pendente', cls: 'bg-yellow-500/15 text-yellow-600 border-yellow-500/30' },
    pendente: { label: 'Pendente', cls: 'bg-yellow-500/15 text-yellow-600 border-yellow-500/30' },
    overdue: { label: 'Vencido', cls: 'bg-red-500/15 text-red-600 border-red-500/30' },
    vencido: { label: 'Vencido', cls: 'bg-red-500/15 text-red-600 border-red-500/30' },
    cancelled: { label: 'Cancelado', cls: 'bg-gray-500/15 text-gray-500 border-gray-500/30' },
    cancelado: { label: 'Cancelado', cls: 'bg-gray-500/15 text-gray-500 border-gray-500/30' },
  };
  const key = status?.toLowerCase() ?? '';
  const entry = map[key] ?? { label: status, cls: 'bg-gray-500/15 text-gray-500 border-gray-500/30' };
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border', entry.cls)}>
      {entry.label}
    </span>
  );
}

// ─── Componente de campo copiável ─────────────────────────────────────────────
function CopyField({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [value]);

  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground flex items-center gap-1">
        {icon}
        {label}
      </p>
      <div className="flex items-center gap-2">
        <Input
          readOnly
          value={value}
          className="font-mono text-xs bg-muted/30 flex-1 truncate"
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleCopy}
          className={cn(
            'shrink-0 transition-colors',
            copied && 'border-green-500 text-green-600'
          )}
        >
          {copied ? (
            <><CheckCircle className="h-3.5 w-3.5 mr-1" /> Copiado!</>
          ) : (
            <><Copy className="h-3.5 w-3.5 mr-1" /> Copiar</>
          )}
        </Button>
      </div>
    </div>
  );
}

// ─── Formulário de emissão ────────────────────────────────────────────────────
interface FormData {
  bank_code: string;
  payer_name: string;
  payer_document: string;
  amount: string;
  due_date: string;
  description: string;
}

const INITIAL_FORM: FormData = {
  bank_code: '403',
  payer_name: '',
  payer_document: '',
  amount: '',
  due_date: '',
  description: '',
};

// ─── Página Principal ─────────────────────────────────────────────────────────
export default function BoletosPage() {
  const [activeTab, setActiveTab] = useState<'emitir' | 'listagem'>('emitir');

  // Formulário
  const [form, setForm] = useState<FormData>(INITIAL_FORM);
  const [isPending, setIsPending] = useState(false);
  const [resultado, setResultado] = useState<BoletoResponse | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  // Listagem
  const [boletos, setBoletos] = useState<BoletoListItem[]>([]);
  const [isLoadingList, setIsLoadingList] = useState(false);
  const [filterBanco, setFilterBanco] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // ── Carregar lista ──────────────────────────────────────────────────────────
  const carregarBoletos = useCallback(async () => {
    setIsLoadingList(true);
    try {
      const res = await listarBoletos(filterBanco || undefined, filterStatus || undefined);
      setBoletos(res.boletos ?? []);
    } finally {
      setIsLoadingList(false);
    }
  }, [filterBanco, filterStatus]);

  useEffect(() => {
    if (activeTab === 'listagem') carregarBoletos();
  }, [activeTab, carregarBoletos]);

  // ── Atualizar campo do formulário ───────────────────────────────────────────
  const setField = useCallback(<K extends keyof FormData>(key: K, value: FormData[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  }, []);

  // ── Formatar documento ──────────────────────────────────────────────────────
  const handleDocumentChange = useCallback((raw: string) => {
    setField('payer_document', maskDocument(raw));
  }, [setField]);

  // ── Validação básica ────────────────────────────────────────────────────────
  const validate = (): string | null => {
    if (!form.payer_name.trim()) return 'Nome do pagador é obrigatório.';
    const digits = form.payer_document.replace(/\D/g, '');
    if (digits.length !== 11 && digits.length !== 14) return 'CPF ou CNPJ inválido.';
    const amount = parseFloat(form.amount.replace(',', '.'));
    if (isNaN(amount) || amount <= 0) return 'Informe um valor maior que zero.';
    if (!form.due_date) return 'Data de vencimento é obrigatória.';
    return null;
  };

  // ── Emitir boleto ───────────────────────────────────────────────────────────
  const handleEmitir = useCallback(async () => {
    setFormError(null);
    const err = validate();
    if (err) { setFormError(err); return; }

    setIsPending(true);
    try {
      const res = await emitirBoleto({
        bank_code: form.bank_code,
        payer_name: form.payer_name.trim(),
        payer_document: form.payer_document.replace(/\D/g, ''),
        amount: parseFloat(form.amount.replace(',', '.')),
        due_date: form.due_date,
        description: form.description.trim(),
      });
      if (!res.success) {
        setFormError(res.error ?? 'Erro ao emitir boleto. Tente novamente.');
      } else {
        setResultado(res);
      }
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } }; message?: string })
        ?.response?.data?.detail ?? (e as { message?: string })?.message ?? 'Erro inesperado ao emitir boleto.';
      setFormError(msg);
    } finally {
      setIsPending(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form]);

  // ── Novo boleto ─────────────────────────────────────────────────────────────
  const handleNovo = useCallback(() => {
    setResultado(null);
    setFormError(null);
    setForm(INITIAL_FORM);
  }, []);

  // ── Copiar código de barras de boleto listado ───────────────────────────────
  const copiarBarcode = useCallback(async (barcode: string) => {
    await navigator.clipboard.writeText(barcode);
  }, []);

  // ─────────────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-background animate-fade-in">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="sm" className="gap-1.5 text-muted-foreground hover:text-foreground">
              <ArrowLeft className="h-4 w-4" />
              Voltar
            </Button>
          </Link>
          <div className="h-5 w-px bg-border" />
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Barcode className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h1 className="text-base font-semibold leading-tight">Boletos Bancários</h1>
              <p className="text-xs text-muted-foreground">Emissão via Cora e Inter</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="flex gap-1 border-b mt-0">
          {(['emitir', 'listagem'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-4 py-3 text-sm font-medium border-b-2 transition-colors -mb-px',
                activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {tab === 'emitir' ? 'Emitir Boleto' : 'Boletos Emitidos'}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6">

        {/* ═══ Tab: Emitir ════════════════════════════════════════════════════ */}
        {activeTab === 'emitir' && (
          <>
            {/* Resultado de emissão bem-sucedida */}
            {resultado ? (
              <Card className="border-green-500/30 bg-green-500/5">
                <CardContent className="pt-6 space-y-5">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-green-500/15 flex items-center justify-center">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h2 className="text-base font-semibold text-green-700">Boleto Emitido com Sucesso</h2>
                      <p className="text-sm text-muted-foreground">
                        {resultado.bank_name} &mdash; {resultado.payer_name}
                      </p>
                    </div>
                  </div>

                  {/* Resumo */}
                  <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-background/60 border">
                    <div>
                      <p className="text-xs text-muted-foreground">Valor</p>
                      <p className="text-sm font-semibold">{formatCurrency(resultado.amount)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Vencimento</p>
                      <p className="text-sm font-semibold">{formatDate(resultado.due_date)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Banco</p>
                      <p
                        className="text-sm font-semibold"
                        style={{ color: BANK_COLORS[resultado.bank_code] ?? 'inherit' }}
                      >
                        {resultado.bank_name}
                      </p>
                    </div>
                    {resultado.boleto_id && (
                      <div>
                        <p className="text-xs text-muted-foreground">ID Boleto</p>
                        <p className="text-sm font-mono truncate">{resultado.boleto_id}</p>
                      </div>
                    )}
                  </div>

                  {/* Linha digitável */}
                  {resultado.digitable_line && (
                    <CopyField
                      label="Linha Digitável"
                      value={resultado.digitable_line}
                      icon={<FileText className="h-3 w-3" />}
                    />
                  )}

                  {/* Código de barras */}
                  {resultado.barcode && (
                    <CopyField
                      label="Código de Barras"
                      value={resultado.barcode}
                      icon={<Barcode className="h-3 w-3" />}
                    />
                  )}

                  {/* PIX Copia e Cola */}
                  {resultado.pix_copy_paste && (
                    <CopyField
                      label="PIX Copia e Cola"
                      value={resultado.pix_copy_paste}
                      icon={<QrCode className="h-3 w-3" />}
                    />
                  )}

                  {/* QR Code PIX */}
                  {resultado.pix_qrcode && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                        <QrCode className="h-3 w-3" />
                        QR Code PIX
                      </p>
                      {resultado.pix_qrcode.startsWith('data:image') || resultado.pix_qrcode.match(/^[A-Za-z0-9+/=]{40,}$/) ? (
                        <img
                          src={
                            resultado.pix_qrcode.startsWith('data:')
                              ? resultado.pix_qrcode
                              : `data:image/png;base64,${resultado.pix_qrcode}`
                          }
                          alt="QR Code PIX"
                          className="w-36 h-36 rounded-lg border object-contain bg-white p-1"
                        />
                      ) : (
                        <a
                          href={resultado.pix_qrcode}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary underline flex items-center gap-1"
                        >
                          Ver QR Code <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  )}

                  {/* Ações */}
                  <div className="flex flex-wrap gap-2 pt-1">
                    {resultado.pdf_url && (
                      <a href={resultado.pdf_url} target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="gap-1.5">
                          <Download className="h-4 w-4" />
                          Baixar PDF
                        </Button>
                      </a>
                    )}
                    <Button onClick={handleNovo} size="sm" className="gap-1.5">
                      <Plus className="h-4 w-4" />
                      Emitir Novo Boleto
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              /* Formulário de emissão */
              <Card>
                <CardContent className="pt-6 space-y-5">
                  <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                    Dados do Boleto
                  </h2>

                  {/* Erro */}
                  {formError && (
                    <div className="flex items-start gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 text-sm">
                      <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                      {formError}
                    </div>
                  )}

                  {/* Select banco */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Banco</label>
                    <div className="flex gap-3">
                      {[
                        { code: '403', name: 'Cora', sub: '403' },
                        { code: '077', name: 'Inter', sub: '077' },
                      ].map((b) => (
                        <button
                          key={b.code}
                          type="button"
                          onClick={() => setField('bank_code', b.code)}
                          className={cn(
                            'flex-1 flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all text-left',
                            form.bank_code === b.code
                              ? 'border-current bg-current/5'
                              : 'border-border hover:border-border/80'
                          )}
                          style={form.bank_code === b.code ? { color: BANK_COLORS[b.code], borderColor: BANK_COLORS[b.code] } : {}}
                        >
                          <div
                            className="h-8 w-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                            style={{ backgroundColor: BANK_COLORS[b.code] }}
                          >
                            {b.name[0]}
                          </div>
                          <div>
                            <p className="text-sm font-semibold">{b.name}</p>
                            <p className="text-xs text-muted-foreground">Banco {b.sub}</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Nome pagador */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Nome Completo do Pagador</label>
                    <Input
                      placeholder="Ex: João da Silva"
                      value={form.payer_name}
                      onChange={(e) = aria-label="Ex:  João Da  Silva"> setField('payer_name', e.target.value)}
                    />
                  </div>

                  {/* CPF/CNPJ */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">CPF / CNPJ</label>
                    <Input
                      placeholder="000.000.000-00 ou 00.000.000/0001-00"
                      value={form.payer_document}
                      onChange={(e) = aria-label="000.000.000 00 Ou 00.000.000/0001 00"> handleDocumentChange(e.target.value)}
                      maxLength={18}
                    />
                  </div>

                  {/* Valor e Vencimento em linha */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium">Valor (R$)</label>
                      <Input
                        type="number"
                        min="0.01"
                        step="0.01"
                        placeholder="0,00"
                        value={form.amount}
                        onChange={(e) = aria-label="0,00"> setField('amount', e.target.value)}
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium">Data de Vencimento</label>
                      <Input
                        type="date"
                        value={form.due_date}
                        min={new Date().toISOString().split('T')[0]}
                        onChange={(e) = aria-label="Date"> setField('due_date', e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Descrição */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Descrição / Referência</label>
                    <textarea
                      rows={3}
                      placeholder="Ex: Mensalidade de vigilância — Janeiro/2026"
                      value={form.description}
                      onChange={(e) = aria-label="Ex:  Mensalidade De Vigilância —  Janeiro/2026"> setField('description', e.target.value)}
                      className={cn(
                        'w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
                        'placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1',
                        'resize-none'
                      )}
                    />
                  </div>

                  {/* Botão emitir */}
                  <Button
                    onClick={handleEmitir}
                    disabled={isPending}
                    className="w-full gap-2"
                    style={{ backgroundColor: BANK_COLORS[form.bank_code] }}
                  >
                    {isPending ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Emitindo boleto…
                      </>
                    ) : (
                      <>
                        <Barcode className="h-4 w-4" />
                        Emitir Boleto via {BANK_NAMES[form.bank_code]}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* ═══ Tab: Listagem ══════════════════════════════════════════════════ */}
        {activeTab === 'listagem' && (
          <div className="space-y-4">
            {/* Filtros */}
            <div className="flex flex-wrap gap-3 items-center">
              <select
                value={filterBanco}
                onChange={(e) => setFilterBanco(e.target.value)}
                className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Todos os bancos</option>
                <option value="403">Cora (403)</option>
                <option value="077">Inter (077)</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Todos os status</option>
                <option value="pending">Pendente</option>
                <option value="paid">Pago</option>
                <option value="overdue">Vencido</option>
                <option value="cancelled">Cancelado</option>
              </select>

              <Button
                variant="outline"
                size="sm"
                onClick={carregarBoletos}
                disabled={isLoadingList}
                className="gap-1.5 ml-auto"
              >
                <RefreshCw className={cn('h-4 w-4', isLoadingList && 'animate-spin')} />
                {isLoadingList ? 'Atualizando…' : 'Atualizar'}
              </Button>
            </div>

            {/* Tabela / Lista */}
            {boletos.length === 0 ? (
              <Card>
                <CardContent className="py-16 flex flex-col items-center gap-3 text-center">
                  <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                    <Barcode className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <p className="text-sm font-medium">Nenhum boleto encontrado.</p>
                  <p className="text-xs text-muted-foreground max-w-xs">
                    Emita seu primeiro boleto na aba ao lado.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2 gap-1.5"
                    onClick={() => setActiveTab('emitir')}
                  >
                    <Plus className="h-4 w-4" />
                    Emitir Boleto
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {boletos.map((b) => (
                  <Card
                    key={b.boleto_id}
                    className="overflow-hidden"
                    style={{ borderLeft: `4px solid ${BANK_COLORS[b.bank_code] ?? '#888'}` }}
                  >
                    <CardContent className="py-3 px-4">
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                        {/* Pagador + banco */}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{b.payer_name}</p>
                          <p
                            className="text-xs font-medium"
                            style={{ color: BANK_COLORS[b.bank_code] ?? '#888' }}
                          >
                            {b.bank_name}
                          </p>
                        </div>

                        {/* Valor */}
                        <div className="text-right">
                          <p className="text-sm font-semibold">{formatCurrency(b.amount)}</p>
                          <p className="text-xs text-muted-foreground">
                            Vence {formatDate(b.due_date)}
                          </p>
                        </div>

                        {/* Data emissão */}
                        {b.created_at && (
                          <div className="hidden sm:block text-right">
                            <p className="text-xs text-muted-foreground">Emitido</p>
                            <p className="text-xs">{formatDate(b.created_at)}</p>
                          </div>
                        )}

                        {/* Status */}
                        <StatusBadge status={b.status} />

                        {/* Ações */}
                        <div className="flex items-center gap-1 ml-auto">
                          {b.barcode && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8"
                              title="Copiar código de barras"
                              onClick={() => copiarBarcode(b.barcode!)}
                            >
                              <Copy className="h-3.5 w-3.5" />
                            </Button>
                          )}
                          {b.pdf_url && (
                            <a href={b.pdf_url} target="_blank" rel="noopener noreferrer">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                title="Ver PDF"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </Button>
                            </a>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
