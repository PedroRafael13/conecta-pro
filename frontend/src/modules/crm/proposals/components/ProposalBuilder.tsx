'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  Package,
  DollarSign,
  FileCheck,
  Eye,
  Send,
  ChevronLeft,
  ChevronRight,
  Check,
  AlertCircle,
  Plus,
  Trash2,
  User,
  Building,
  Calendar,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';
import { Input } from '@/core/components/ui/Input';
import { Card } from '@/core/components/ui/Card';
import type { Proposal, ProposalProduct } from '../../types';

interface ProposalBuilderProps {
  initialData?: Partial<Proposal>;
  onSubmit: (data: Proposal) => void;
  onCancel: () => void;
}

interface StepConfig {
  id: number;
  title: string;
  description: string;
  icon: React.ElementType;
}

const steps: StepConfig[] = [
  { id: 1, title: 'Informacoes Basicas', description: 'Dados do cliente e proposta', icon: FileText },
  { id: 2, title: 'Produtos/Servicos', description: 'Itens da proposta', icon: Package },
  { id: 3, title: 'Precos', description: 'Valores e descontos', icon: DollarSign },
  { id: 4, title: 'Termos', description: 'Condicoes e termos', icon: FileCheck },
  { id: 5, title: 'Revisao', description: 'Revisar proposta', icon: Eye },
  { id: 6, title: 'Enviar', description: 'Finalizar e enviar', icon: Send },
];

interface FormData {
  title: string;
  contactId: string;
  contactName: string;
  contactEmail: string;
  companyName: string;
  validUntil: string;
  currency: 'BRL' | 'USD';
  products: ProposalProduct[];
  discount: number;
  discountType: 'percentage' | 'fixed';
  terms: string;
  notes: string;
  paymentTerms: string;
}

const initialFormData: FormData = {
  title: '',
  contactId: '',
  contactName: '',
  contactEmail: '',
  companyName: '',
  validUntil: '',
  currency: 'BRL',
  products: [],
  discount: 0,
  discountType: 'percentage',
  terms: 'Proposta valida conforme data indicada. Pagamento conforme condicoes acordadas.',
  notes: '',
  paymentTerms: '30 dias apos aprovacao',
};

export function ProposalBuilder({ initialData, onSubmit, onCancel }: ProposalBuilderProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateFormData = useCallback((field: keyof FormData, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [errors]);

  const validateStep = useCallback((step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.title.trim()) newErrors.title = 'Titulo obrigatorio';
        if (!formData.contactName.trim()) newErrors.contactName = 'Nome do cliente obrigatorio';
        if (!formData.contactEmail.trim()) newErrors.contactEmail = 'Email obrigatorio';
        if (!formData.validUntil) newErrors.validUntil = 'Data de validade obrigatoria';
        break;
      case 2:
        if (formData.products.length === 0) newErrors.products = 'Adicione pelo menos um produto/servico';
        break;
      case 3:
        // Pricing validation se necessario
        break;
      case 4:
        if (!formData.terms.trim()) newErrors.terms = 'Termos obrigatorios';
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleNext = useCallback(() => {
    if (validateStep(currentStep) && currentStep < 6) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep, validateStep]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const handleStepClick = useCallback((step: number) => {
    if (step < currentStep) {
      setCurrentStep(step);
    }
  }, [currentStep]);

  const addProduct = useCallback(() => {
    const newProduct: ProposalProduct = {
      id: `prod-${Date.now()}`,
      name: '',
      description: '',
      quantity: 1,
      unitPrice: 0,
      discount: 0,
      total: 0,
    };
    setFormData(prev => ({
      ...prev,
      products: [...prev.products, newProduct],
    }));
  }, []);

  const updateProduct = useCallback((index: number, field: keyof ProposalProduct, value: unknown) => {
    setFormData(prev => {
      const products = [...prev.products];
      products[index] = { ...products[index], [field]: value };
      // Recalcular total
      const product = products[index];
      const subtotal = product.quantity * product.unitPrice;
      product.total = subtotal - (subtotal * product.discount / 100);
      return { ...prev, products };
    });
  }, []);

  const removeProduct = useCallback((index: number) => {
    setFormData(prev => ({
      ...prev,
      products: prev.products.filter((_, i) => i !== index),
    }));
  }, []);

  const calculateSubtotal = useCallback(() => {
    return formData.products.reduce((acc, p) => acc + p.total, 0);
  }, [formData.products]);

  const calculateTotal = useCallback(() => {
    const subtotal = calculateSubtotal();
    if (formData.discountType === 'percentage') {
      return subtotal - (subtotal * formData.discount / 100);
    }
    return subtotal - formData.discount;
  }, [calculateSubtotal, formData.discount, formData.discountType]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: formData.currency,
    }).format(value);
  };

  const handleSubmit = useCallback(() => {
    // Criar proposta completa
    const proposal: Proposal = {
      id: initialData?.id || `prop-${Date.now()}`,
      dealId: initialData?.dealId,
      contactId: formData.contactId || `contact-${Date.now()}`,
      title: formData.title,
      status: 'draft',
      sections: [
        {
          id: 'sec-intro',
          type: 'intro',
          title: 'Introducao',
          content: formData.notes,
          order: 1,
        },
        {
          id: 'sec-products',
          type: 'products',
          title: 'Produtos/Servicos',
          content: '',
          order: 2,
          products: formData.products,
        },
        {
          id: 'sec-terms',
          type: 'terms',
          title: 'Termos e Condicoes',
          content: formData.terms,
          order: 3,
        },
      ],
      total: calculateTotal(),
      currency: formData.currency,
      validUntil: formData.validUntil,
      createdBy: 'current-user',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      comments: [],
      version: initialData?.version || 1,
    };

    onSubmit(proposal);
  }, [formData, calculateTotal, initialData, onSubmit]);

  const renderStepContent = () => {
    const variants = {
      enter: { opacity: 0, x: 20 },
      center: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: -20 },
    };

    return (
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.3 }}
          className="min-h-[400px]"
        >
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Titulo da Proposta"
                  value={formData.title}
                  onChange={e => updateFormData('title', e.target.value)}
                  error={errors.title}
                  placeholder="Ex: Proposta de Manutencao Predial"
                  leftIcon={<FileText className="w-4 h-4" />}
                />
                <Input
                  label="Data de Validade"
                  type="date"
                  value={formData.validUntil}
                  onChange={e => updateFormData('validUntil', e.target.value)}
                  error={errors.validUntil}
                  leftIcon={<Calendar className="w-4 h-4" />}
                />
              </div>

              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-4">Dados do Cliente</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Nome do Contato"
                    value={formData.contactName}
                    onChange={e => updateFormData('contactName', e.target.value)}
                    error={errors.contactName}
                    placeholder="Nome completo"
                    leftIcon={<User className="w-4 h-4" />}
                  />
                  <Input
                    label="Email"
                    type="email"
                    value={formData.contactEmail}
                    onChange={e => updateFormData('contactEmail', e.target.value)}
                    error={errors.contactEmail}
                    placeholder="email@empresa.com"
                  />
                  <Input
                    label="Empresa"
                    value={formData.companyName}
                    onChange={e => updateFormData('companyName', e.target.value)}
                    placeholder="Nome da empresa"
                    leftIcon={<Building className="w-4 h-4" />}
                  />
                  <div>
                    <label className="label">Moeda</label>
                    <select
                      value={formData.currency}
                      onChange={e => updateFormData('currency', e.target.value)}
                      className="input"
                    >
                      <option value="BRL">Real (BRL)</option>
                      <option value="USD">Dolar (USD)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="font-medium text-gray-900">Produtos/Servicos</h4>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addProduct}
                  leftIcon={<Plus className="w-4 h-4" />}
                >
                  Adicionar Item
                </Button>
              </div>

              {errors.products && (
                <div className="flex items-center gap-2 text-red-600 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  {errors.products}
                </div>
              )}

              <div className="space-y-4">
                {formData.products.map((product, index) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="p-4 border rounded-lg bg-gray-50"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                      <div className="md:col-span-2">
                        <Input
                          label="Nome"
                          value={product.name}
                          onChange={e => updateProduct(index, 'name', e.target.value)}
                          placeholder="Nome do produto/servico"
                        />
                      </div>
                      <Input
                        label="Quantidade"
                        type="number"
                        min={1}
                        value={product.quantity}
                        onChange={e => updateProduct(index, 'quantity', parseInt(e.target.value) || 1)}
                      />
                      <Input
                        label="Preco Unit."
                        type="number"
                        min={0}
                        step={0.01}
                        value={product.unitPrice}
                        onChange={e => updateProduct(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                      />
                      <Input
                        label="Desconto %"
                        type="number"
                        min={0}
                        max={100}
                        value={product.discount}
                        onChange={e => updateProduct(index, 'discount', parseFloat(e.target.value) || 0)}
                      />
                      <div className="flex items-end gap-2">
                        <div className="flex-1">
                          <label className="label">Total</label>
                          <div className="input bg-gray-100 font-semibold">
                            {formatCurrency(product.total)}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeProduct(index)}
                          className="text-red-500 hover:text-red-700 mb-1"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2">
                      <Input
                        label="Descricao"
                        value={product.description || ''}
                        onChange={e => updateProduct(index, 'description', e.target.value)}
                        placeholder="Descricao do item (opcional)"
                      />
                    </div>
                  </motion.div>
                ))}
              </div>

              {formData.products.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Nenhum item adicionado</p>
                  <p className="text-sm">Clique em "Adicionar Item" para comecar</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-4">
                  <h4 className="font-medium text-gray-900 mb-4">Desconto Global</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="label">Tipo de Desconto</label>
                      <select
                        value={formData.discountType}
                        onChange={e => updateFormData('discountType', e.target.value)}
                        className="input"
                      >
                        <option value="percentage">Percentual (%)</option>
                        <option value="fixed">Valor Fixo (R$)</option>
                      </select>
                    </div>
                    <Input
                      label={formData.discountType === 'percentage' ? 'Desconto (%)' : 'Desconto (R$)'}
                      type="number"
                      min={0}
                      step={formData.discountType === 'percentage' ? 1 : 0.01}
                      value={formData.discount}
                      onChange={e => updateFormData('discount', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </Card>

                <Card className="p-4">
                  <h4 className="font-medium text-gray-900 mb-4">Resumo</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between text-gray-600">
                      <span>Subtotal</span>
                      <span>{formatCurrency(calculateSubtotal())}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <span>Desconto</span>
                      <span className="text-red-500">
                        -{formData.discountType === 'percentage'
                          ? `${formData.discount}%`
                          : formatCurrency(formData.discount)}
                      </span>
                    </div>
                    <div className="border-t pt-3">
                      <div className="flex justify-between text-lg font-bold text-conecta-escuro">
                        <span>Total</span>
                        <span>{formatCurrency(calculateTotal())}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>

              <Card className="p-4">
                <h4 className="font-medium text-gray-900 mb-4">Condicoes de Pagamento</h4>
                <Input
                  value={formData.paymentTerms}
                  onChange={e => updateFormData('paymentTerms', e.target.value)}
                  placeholder="Ex: 30/60/90 dias"
                />
              </Card>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-6">
              <div>
                <label className="label">Termos e Condicoes</label>
                <textarea
                  value={formData.terms}
                  onChange={e => updateFormData('terms', e.target.value)}
                  rows={6}
                  className="input"
                  placeholder="Descreva os termos e condicoes da proposta..."
                />
                {errors.terms && <p className="error-text">{errors.terms}</p>}
              </div>

              <div>
                <label className="label">Observacoes Adicionais</label>
                <textarea
                  value={formData.notes}
                  onChange={e => updateFormData('notes', e.target.value)}
                  rows={4}
                  className="input"
                  placeholder="Notas ou observacoes para o cliente..."
                />
              </div>
            </div>
          )}

          {currentStep === 5 && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-2">{formData.title}</h3>
                <p className="text-gray-600">Para: {formData.contactName} - {formData.companyName}</p>
                <p className="text-sm text-gray-500">Valida ate: {formData.validUntil}</p>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Item</th>
                      <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Qtd</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Unit.</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {formData.products.map(product => (
                      <tr key={product.id}>
                        <td className="px-4 py-3">
                          <div className="font-medium">{product.name}</div>
                          {product.description && (
                            <div className="text-sm text-gray-500">{product.description}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-center">{product.quantity}</td>
                        <td className="px-4 py-3 text-right">{formatCurrency(product.unitPrice)}</td>
                        <td className="px-4 py-3 text-right font-medium">{formatCurrency(product.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50">
                    <tr>
                      <td colSpan={3} className="px-4 py-3 text-right font-medium">Subtotal</td>
                      <td className="px-4 py-3 text-right">{formatCurrency(calculateSubtotal())}</td>
                    </tr>
                    {formData.discount > 0 && (
                      <tr>
                        <td colSpan={3} className="px-4 py-3 text-right font-medium">Desconto</td>
                        <td className="px-4 py-3 text-right text-red-500">
                          -{formData.discountType === 'percentage'
                            ? `${formData.discount}%`
                            : formatCurrency(formData.discount)}
                        </td>
                      </tr>
                    )}
                    <tr className="text-lg font-bold">
                      <td colSpan={3} className="px-4 py-3 text-right">Total</td>
                      <td className="px-4 py-3 text-right text-conecta-escuro">{formatCurrency(calculateTotal())}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">Termos e Condicoes</h5>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{formData.terms}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">Condicoes de Pagamento</h5>
                  <p className="text-sm text-gray-600">{formData.paymentTerms}</p>
                </div>
              </div>
            </div>
          )}

          {currentStep === 6 && (
            <div className="text-center py-12">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
                className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <Send className="w-10 h-10 text-green-600" />
              </motion.div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Proposta Pronta!</h3>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Revise os dados e clique em "Enviar Proposta" para enviar ao cliente ou "Salvar Rascunho" para continuar depois.
              </p>

              <div className="bg-gray-50 rounded-lg p-6 max-w-md mx-auto text-left">
                <h4 className="font-medium text-gray-900 mb-3">Resumo</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cliente:</span>
                    <span className="font-medium">{formData.contactName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Itens:</span>
                    <span className="font-medium">{formData.products.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Validade:</span>
                    <span className="font-medium">{formData.validUntil}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span className="text-gray-900 font-medium">Total:</span>
                    <span className="font-bold text-conecta-escuro">{formatCurrency(calculateTotal())}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;

            return (
              <div
                key={step.id}
                className="flex flex-1 items-center"
              >
                <button
                  onClick={() => handleStepClick(step.id)}
                  disabled={step.id > currentStep}
                  className={`
                    flex flex-col items-center relative group
                    ${step.id <= currentStep ? 'cursor-pointer' : 'cursor-not-allowed'}
                  `}
                >
                  <motion.div
                    initial={false}
                    animate={{
                      scale: isActive ? 1.1 : 1,
                      backgroundColor: isCompleted ? '#10B981' : isActive ? '#1E3A5F' : '#E5E7EB',
                    }}
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center
                      transition-colors
                    `}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5 text-white" />
                    ) : (
                      <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                    )}
                  </motion.div>
                  <span className={`
                    mt-2 text-xs font-medium hidden md:block
                    ${isActive ? 'text-conecta-escuro' : 'text-gray-500'}
                  `}>
                    {step.title}
                  </span>
                </button>

                {index < steps.length - 1 && (
                  <div className="flex-1 h-0.5 mx-2">
                    <motion.div
                      initial={false}
                      animate={{
                        backgroundColor: isCompleted ? '#10B981' : '#E5E7EB',
                      }}
                      className="h-full"
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <Card className="p-6">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">
            {steps[currentStep - 1].title}
          </h2>
          <p className="text-gray-500">{steps[currentStep - 1].description}</p>
        </div>

        {renderStepContent()}

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8 pt-6 border-t">
          <Button
            variant="ghost"
            onClick={currentStep === 1 ? onCancel : handlePrevious}
            leftIcon={<ChevronLeft className="w-4 h-4" />}
          >
            {currentStep === 1 ? 'Cancelar' : 'Anterior'}
          </Button>

          <div className="flex gap-2">
            {currentStep === 6 && (
              <Button
                variant="outline"
                onClick={() => handleSubmit()}
              >
                Salvar Rascunho
              </Button>
            )}
            {currentStep < 6 ? (
              <Button
                onClick={handleNext}
                rightIcon={<ChevronRight className="w-4 h-4" />}
              >
                Proximo
              </Button>
            ) : (
              <Button
                onClick={() => {
                  handleSubmit();
                  // Aqui enviaria a proposta
                }}
                leftIcon={<Send className="w-4 h-4" />}
              >
                Enviar Proposta
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

export default ProposalBuilder;
