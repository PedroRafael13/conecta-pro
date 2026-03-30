'use client';

import React, { useEffect, useRef, useState } from 'react';
import { CheckCircle, PenLine, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

function portalFetch(path: string, options?: RequestInit) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('portal_token') : '';
  return fetch(`${API_BASE}/api/v1/portal${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
}

interface ApprovalStatus {
  status: string;
  approved_at?: string;
  approved_by?: string;
  signature_id?: string;
}

interface KitApprovalSectionProps {
  kitId: string;
  kitStatus: string;
  onApproved?: () => void;
}

// ─── Signature Canvas ─────────────────────────────────────────────────────────

function SignaturePad({
  onSignature,
}: {
  onSignature: (dataUrl: string | null) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const [hasSignature, setHasSignature] = useState(false);

  function getPos(e: React.MouseEvent | React.TouchEvent, canvas: HTMLCanvasElement) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if ('touches' in e) {
      const t = e.touches[0];
      if (!t) return { x: 0, y: 0 };
      return { x: (t.clientX - rect.left) * scaleX, y: (t.clientY - rect.top) * scaleY };
    }
    return {
      x: ((e as React.MouseEvent).clientX - rect.left) * scaleX,
      y: ((e as React.MouseEvent).clientY - rect.top) * scaleY,
    };
  }

  function startDraw(e: React.MouseEvent | React.TouchEvent) {
    drawing.current = true;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(x, y);
  }

  function draw(e: React.MouseEvent | React.TouchEvent) {
    if (!drawing.current) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { x, y } = getPos(e, canvas);
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#1e293b';
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
    setHasSignature(true);
    onSignature(canvas.toDataURL('image/png'));
  }

  function stopDraw() {
    drawing.current = false;
  }

  function clearPad() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
    onSignature(null);
  }

  return (
    <div className="space-y-2">
      <div className="relative border-2 border-dashed border-gray-300 rounded-lg overflow-hidden bg-gray-50">
        <canvas
          ref={canvasRef}
          width={520}
          height={140}
          className="w-full touch-none cursor-crosshair"
          onMouseDown={startDraw}
          onMouseMove={draw}
          onMouseUp={stopDraw}
          onMouseLeave={stopDraw}
          onTouchStart={startDraw}
          onTouchMove={draw}
          onTouchEnd={stopDraw}
        />
        {!hasSignature && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="text-sm text-gray-400 flex items-center gap-1.5">
              <PenLine className="h-4 w-4" />
              Assine aqui
            </p>
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={clearPad}
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
      >
        <RotateCcw className="h-3 w-3" />
        Limpar assinatura
      </button>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function KitApprovalSection({ kitId, kitStatus, onApproved }: KitApprovalSectionProps) {
  const [approvalStatus, setApprovalStatus] = useState<ApprovalStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [signatoryName, setSignatoryName] = useState('');
  const [declared, setDeclared] = useState(false);
  const [signature, setSignature] = useState<string | null>(null);
  const [confirm, setConfirm] = useState(false);

  useEffect(() => {
    portalFetch(`/kits/${kitId}/approval-status`)
      .then((r) => r.json())
      .then(setApprovalStatus)
      .catch(() => setApprovalStatus({ status: kitStatus }))
      .finally(() => setLoading(false));
  }, [kitId, kitStatus]);

  async function handleApprove() {
    if (!signatoryName.trim() || !declared || !signature) return;
    setSubmitting(true);
    try {
      const res = await portalFetch(`/kits/${kitId}/approve`, {
        method: 'POST',
        body: JSON.stringify({
          signatory_name: signatoryName.trim(),
          declaration: 'Declaro que revisei e aprovo todos os documentos deste kit mensal.',
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Erro ao aprovar');
      }
      const data = await res.json();
      setApprovalStatus({ status: 'aprovado', approved_at: data.approved_at, approved_by: signatoryName });
      setConfirm(false);
      toast.success('Kit aprovado com sucesso!');
      onApproved?.();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Erro ao aprovar kit');
    } finally {
      setSubmitting(false);
    }
  }

  const isApprovable = ['completo', 'enviado', 'COMPLETO', 'ENVIADO'].includes(kitStatus);

  if (loading) {
    return <div className="animate-pulse bg-gray-100 rounded-xl h-20 w-full" />;
  }

  // Kit já aprovado
  if (approvalStatus?.status === 'aprovado') {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-start gap-3">
        <CheckCircle className="h-5 w-5 text-emerald-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold text-emerald-800">Kit Aprovado Digitalmente</p>
          {approvalStatus.approved_by && (
            <p className="text-xs text-emerald-600 mt-0.5">Por: {approvalStatus.approved_by}</p>
          )}
          {approvalStatus.approved_at && (
            <p className="text-xs text-emerald-600">
              Em: {new Date(approvalStatus.approved_at).toLocaleString('pt-BR')}
            </p>
          )}
          {approvalStatus.signature_id && (
            <p className="text-xs text-emerald-500 mt-0.5">
              ID: {approvalStatus.signature_id.slice(0, 16).toUpperCase()}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Kit não aprovável ainda
  if (!isApprovable) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm text-gray-500">
        <p>O kit precisa estar <strong>completo</strong> ou <strong>enviado</strong> para ser aprovado.</p>
        <p className="mt-0.5">Status atual: <span className="font-medium capitalize">{kitStatus}</span></p>
      </div>
    );
  }

  // Formulário de aprovação
  return (
    <div className="bg-white border border-indigo-100 rounded-xl p-5 space-y-4 shadow-sm">
      <div className="flex items-center gap-2">
        <PenLine className="h-5 w-5 text-indigo-600" />
        <h3 className="text-sm font-semibold text-gray-800">Aprovar Kit Digitalmente</h3>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Nome completo do signatário *</label>
        <input
          type="text"
          value={signatoryName}
          onChange={(e) => setSignatoryName(e.target.value)}
          placeholder="Ex: João da Silva"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Assinatura *</label>
        <SignaturePad onSignature={setSignature} />
      </div>

      <label className="flex items-start gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={declared}
          onChange={(e) => setDeclared(e.target.checked)}
          className="mt-0.5 h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
        />
        <span className="text-xs text-gray-600">
          Declaro que li e revisei todos os documentos deste kit mensal e os aprovo formalmente.
        </span>
      </label>

      {!confirm ? (
        <button
          disabled={!signatoryName.trim() || !declared || !signature}
          onClick={() => setConfirm(true)}
          className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Aprovar Kit
        </button>
      ) : (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 space-y-2">
          <p className="text-sm text-amber-800 font-medium">⚠️ Confirmar aprovação?</p>
          <p className="text-xs text-amber-700">Esta ação não pode ser desfeita.</p>
          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={submitting}
              className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              {submitting ? 'Aprovando...' : 'Confirmar'}
            </button>
            <button
              onClick={() => setConfirm(false)}
              className="flex-1 py-2 bg-white border border-gray-200 text-gray-600 text-sm rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
