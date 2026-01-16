'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Send,
  Calendar,
  DollarSign,
  FileText,
  Building,
  User,
  Mail,
  Phone,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';
import { Input } from '@/core/components/ui/Input';
import { Badge } from '@/core/components/ui/Badge';
import type { MarketplaceService, ServiceRequest } from '../../types';

interface QuoteRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: MarketplaceService | null;
  onSubmit: (request: Partial<ServiceRequest>) => Promise<void>;
}

interface FormData {
  contactName: string;
  contactEmail: string;
  contactPhone: string;
  companyName: string;
  description: string;
  budget: string;
  deadline: string;
  selectedPricing: string;
}

const initialFormData: FormData = {
  contactName: '',
  contactEmail: '',
  contactPhone: '',
  companyName: '',
  description: '',
  budget: '',
  deadline: '',
  selectedPricing: '',
};

export function QuoteRequestModal({
  isOpen,
  onClose,
  service,
  onSubmit,
}: QuoteRequestModalProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const updateField = useCallback((field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [errors]);

  const validate = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.contactName.trim()) {
      newErrors.contactName = 'Nome obrigatorio';
    }

    if (!formData.contactEmail.trim()) {
      newErrors.contactEmail = 'Email obrigatorio';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contactEmail)) {
      newErrors.contactEmail = 'Email invalido';
    }

    if (!formData.contactPhone.trim()) {
      newErrors.contactPhone = 'Telefone obrigatorio';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Descreva sua necessidade';
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Descricao muito curta (minimo 20 caracteres)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate() || !service) return;

    setIsSubmitting(true);

    try {
      const request: Partial<ServiceRequest> = {
        serviceId: service.id,
        description: formData.description,
        budget: formData.budget ? parseFloat(formData.budget) : undefined,
        deadline: formData.deadline || undefined,
        status: 'pending',
        createdAt: new Date().toISOString(),
      };

      await onSubmit(request);
      setIsSuccess(true);

      // Reset form after delay
      setTimeout(() => {
        setFormData(initialFormData);
        setIsSuccess(false);
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Erro ao enviar solicitacao:', error);
      setErrors({ submit: 'Erro ao enviar. Tente novamente.' });
    } finally {
      setIsSubmitting(false);
    }
  }, [validate, service, formData, onSubmit, onClose]);

  const handleClose = useCallback(() => {
    if (isSubmitting) return;
    setFormData(initialFormData);
    setErrors({});
    setIsSuccess(false);
    onClose();
  }, [isSubmitting, onClose]);

  const formatCurrency = (value: number, currency: 'BRL' | 'USD') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency,
    }).format(value);
  };

  if (!service) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-4 md:inset-auto md:left-1/2 md:top-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:max-w-2xl md:w-full bg-white rounded-xl shadow-xl z-50 flex flex-col max-h-[90vh] overflow-hidden"
          >
            {/* Success State */}
            <AnimatePresence mode="wait">
              {isSuccess ? (
                <motion.div
                  key="success"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center p-12 text-center"
                >
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', delay: 0.2 }}
                    className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6"
                  >
                    <CheckCircle className="w-10 h-10 text-green-600" />
                  </motion.div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Solicitacao Enviada!
                  </h3>
                  <p className="text-gray-600">
                    O fornecedor entrara em contato em breve.
                  </p>
                </motion.div>
              ) : (
                <motion.div
                  key="form"
                  initial={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col h-full"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between p-6 border-b">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">
                        Solicitar Orcamento
                      </h2>
                      <p className="text-gray-500 mt-1">
                        Preencha os dados para receber uma proposta
                      </p>
                    </div>
                    <button
                      onClick={handleClose}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>

                  {/* Service Info */}
                  <div className="px-6 py-4 bg-gray-50 border-b">
                    <div className="flex items-center gap-4">
                      {service.images[0] ? (
                        <img
                          src={service.images[0]}
                          alt={service.title}
                          className="w-16 h-16 rounded-lg object-cover"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-lg bg-conecta-escuro/10 flex items-center justify-center">
                          <FileText className="w-6 h-6 text-conecta-escuro" />
                        </div>
                      )}
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {service.title}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {service.provider.companyName}
                        </p>
                      </div>
                      {service.pricing[0] && (
                        <Badge variant="primary" size="lg">
                          A partir de {formatCurrency(service.pricing[0].price, service.pricing[0].currency)}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Form */}
                  <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
                    <div className="space-y-6">
                      {/* Contact Info */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">
                          Seus Dados
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <Input
                            label="Nome Completo"
                            value={formData.contactName}
                            onChange={e => updateField('contactName', e.target.value)}
                            error={errors.contactName}
                            placeholder="Seu nome"
                            leftIcon={<User className="w-4 h-4" />}
                            required
                          />
                          <Input
                            label="Empresa"
                            value={formData.companyName}
                            onChange={e => updateField('companyName', e.target.value)}
                            placeholder="Nome da empresa"
                            leftIcon={<Building className="w-4 h-4" />}
                          />
                          <Input
                            label="Email"
                            type="email"
                            value={formData.contactEmail}
                            onChange={e => updateField('contactEmail', e.target.value)}
                            error={errors.contactEmail}
                            placeholder="seu@email.com"
                            leftIcon={<Mail className="w-4 h-4" />}
                            required
                          />
                          <Input
                            label="Telefone"
                            value={formData.contactPhone}
                            onChange={e => updateField('contactPhone', e.target.value)}
                            error={errors.contactPhone}
                            placeholder="(11) 99999-9999"
                            leftIcon={<Phone className="w-4 h-4" />}
                            required
                          />
                        </div>
                      </div>

                      {/* Pricing Options */}
                      {service.pricing.length > 1 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-4">
                            Plano de Interesse
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {service.pricing.map(pricing => (
                              <button
                                key={pricing.id}
                                type="button"
                                onClick={() => updateField('selectedPricing', pricing.id)}
                                className={`
                                  p-4 rounded-lg border-2 text-left transition-all
                                  ${formData.selectedPricing === pricing.id
                                    ? 'border-conecta-escuro bg-conecta-escuro/5'
                                    : 'border-gray-200 hover:border-gray-300'
                                  }
                                `}
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <span className="font-medium">{pricing.name}</span>
                                  <span className="font-bold text-conecta-escuro">
                                    {formatCurrency(pricing.price, pricing.currency)}
                                    {pricing.period && `/${pricing.period}`}
                                  </span>
                                </div>
                                {pricing.description && (
                                  <p className="text-sm text-gray-600">
                                    {pricing.description}
                                  </p>
                                )}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Request Details */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">
                          Detalhes da Solicitacao
                        </h4>
                        <div className="space-y-4">
                          <div>
                            <label className="label">
                              Descreva sua Necessidade
                              <span className="text-red-500 ml-1">*</span>
                            </label>
                            <textarea
                              value={formData.description}
                              onChange={e => updateField('description', e.target.value)}
                              rows={4}
                              className={`input ${errors.description ? 'input-error' : ''}`}
                              placeholder="Descreva detalhadamente o que voce precisa, incluindo especificacoes, quantidade, local, etc."
                            />
                            {errors.description && (
                              <p className="error-text">{errors.description}</p>
                            )}
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                              label="Orcamento Estimado"
                              type="number"
                              min={0}
                              step={100}
                              value={formData.budget}
                              onChange={e => updateField('budget', e.target.value)}
                              placeholder="R$ 0,00"
                              hint="Opcional - ajuda o fornecedor a entender seu investimento"
                              leftIcon={<DollarSign className="w-4 h-4" />}
                            />
                            <Input
                              label="Prazo Desejado"
                              type="date"
                              value={formData.deadline}
                              onChange={e => updateField('deadline', e.target.value)}
                              hint="Opcional - quando voce precisa do servico"
                              leftIcon={<Calendar className="w-4 h-4" />}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Error message */}
                      {errors.submit && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-4 bg-red-50 text-red-600 rounded-lg text-sm"
                        >
                          {errors.submit}
                        </motion.div>
                      )}
                    </div>
                  </form>

                  {/* Footer */}
                  <div className="flex items-center justify-between p-6 border-t bg-gray-50">
                    <p className="text-sm text-gray-500">
                      Suas informacoes estao protegidas
                    </p>
                    <div className="flex gap-3">
                      <Button
                        variant="ghost"
                        onClick={handleClose}
                        disabled={isSubmitting}
                      >
                        Cancelar
                      </Button>
                      <Button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        leftIcon={isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      >
                        {isSubmitting ? 'Enviando...' : 'Enviar Solicitacao'}
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default QuoteRequestModal;
