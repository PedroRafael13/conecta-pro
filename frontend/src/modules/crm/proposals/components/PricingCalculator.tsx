'use client';

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Trash2,
  Calculator,
  Percent,
  DollarSign,
  Receipt,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';
import { Input } from '@/core/components/ui/Input';
import { Card } from '@/core/components/ui/Card';

interface PricingItem {
  id: string;
  name: string;
  quantity: number;
  unitPrice: number;
  discount: number;
}

interface PricingCalculatorProps {
  items?: PricingItem[];
  currency?: 'BRL' | 'USD';
  taxRate?: number;
  onItemsChange?: (items: PricingItem[]) => void;
  onTotalChange?: (total: number) => void;
  readOnly?: boolean;
}

export function PricingCalculator({
  items: initialItems = [],
  currency = 'BRL',
  taxRate = 0,
  onItemsChange,
  onTotalChange,
  readOnly = false,
}: PricingCalculatorProps) {
  const [items, setItems] = useState<PricingItem[]>(initialItems);
  const [globalDiscount, setGlobalDiscount] = useState(0);
  const [globalDiscountType, setGlobalDiscountType] = useState<'percentage' | 'fixed'>('percentage');

  const formatCurrency = useCallback((value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency,
    }).format(value);
  }, [currency]);

  const calculateItemTotal = useCallback((item: PricingItem) => {
    const subtotal = item.quantity * item.unitPrice;
    return subtotal - (subtotal * item.discount / 100);
  }, []);

  const subtotal = useMemo(() => {
    return items.reduce((acc, item) => acc + calculateItemTotal(item), 0);
  }, [items, calculateItemTotal]);

  const discountAmount = useMemo(() => {
    if (globalDiscountType === 'percentage') {
      return subtotal * globalDiscount / 100;
    }
    return globalDiscount;
  }, [subtotal, globalDiscount, globalDiscountType]);

  const subtotalAfterDiscount = useMemo(() => {
    return subtotal - discountAmount;
  }, [subtotal, discountAmount]);

  const taxAmount = useMemo(() => {
    return subtotalAfterDiscount * taxRate / 100;
  }, [subtotalAfterDiscount, taxRate]);

  const total = useMemo(() => {
    const finalTotal = subtotalAfterDiscount + taxAmount;
    onTotalChange?.(finalTotal);
    return finalTotal;
  }, [subtotalAfterDiscount, taxAmount, onTotalChange]);

  const addItem = useCallback(() => {
    const newItem: PricingItem = {
      id: `item-${Date.now()}`,
      name: '',
      quantity: 1,
      unitPrice: 0,
      discount: 0,
    };
    const newItems = [...items, newItem];
    setItems(newItems);
    onItemsChange?.(newItems);
  }, [items, onItemsChange]);

  const updateItem = useCallback((id: string, field: keyof PricingItem, value: unknown) => {
    const newItems = items.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    );
    setItems(newItems);
    onItemsChange?.(newItems);
  }, [items, onItemsChange]);

  const removeItem = useCallback((id: string) => {
    const newItems = items.filter(item => item.id !== id);
    setItems(newItems);
    onItemsChange?.(newItems);
  }, [items, onItemsChange]);

  return (
    <div className="space-y-6">
      {/* Items Table */}
      <Card padding="none" className="overflow-hidden">
        <div className="p-4 bg-gray-50 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calculator className="w-5 h-5 text-conecta-escuro" />
            <h3 className="font-semibold text-gray-900">Calculadora de Precos</h3>
          </div>
          {!readOnly && (
            <Button
              variant="outline"
              size="sm"
              onClick={addItem}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Adicionar Item
            </Button>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Item</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600 w-24">Qtd</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600 w-32">Preco Unit.</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-600 w-24">Desc. %</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600 w-32">Total</th>
                {!readOnly && <th className="px-4 py-3 w-12"></th>}
              </tr>
            </thead>
            <tbody className="divide-y">
              <AnimatePresence mode="popLayout">
                {items.map((item, index) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-4 py-3">
                      {readOnly ? (
                        <span className="font-medium">{item.name}</span>
                      ) : (
                        <input
                          type="text"
                          value={item.name}
                          onChange={e => updateItem(item.id, 'name', e.target.value)}
                          placeholder="Nome do item"
                          className="w-full px-2 py-1 border rounded focus:ring-1 focus:ring-conecta-escuro focus:border-conecta-escuro"
                        />
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {readOnly ? (
                        <span className="text-center block">{item.quantity}</span>
                      ) : (
                        <input
                          type="number"
                          min={1}
                          value={item.quantity}
                          onChange={e => updateItem(item.id, 'quantity', parseInt(e.target.value) || 1)}
                          className="w-full px-2 py-1 border rounded text-center focus:ring-1 focus:ring-conecta-escuro focus:border-conecta-escuro"
                        />
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {readOnly ? (
                        <span className="text-right block">{formatCurrency(item.unitPrice)}</span>
                      ) : (
                        <input
                          type="number"
                          min={0}
                          step={0.01}
                          value={item.unitPrice}
                          onChange={e => updateItem(item.id, 'unitPrice', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 border rounded text-right focus:ring-1 focus:ring-conecta-escuro focus:border-conecta-escuro"
                        />
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {readOnly ? (
                        <span className="text-center block">{item.discount}%</span>
                      ) : (
                        <input
                          type="number"
                          min={0}
                          max={100}
                          value={item.discount}
                          onChange={e => updateItem(item.id, 'discount', parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 border rounded text-center focus:ring-1 focus:ring-conecta-escuro focus:border-conecta-escuro"
                        />
                      )}
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-conecta-escuro">
                      {formatCurrency(calculateItemTotal(item))}
                    </td>
                    {!readOnly && (
                      <td className="px-4 py-3">
                        <button
                          onClick={() => removeItem(item.id)}
                          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    )}
                  </motion.tr>
                ))}
              </AnimatePresence>

              {items.length === 0 && (
                <tr>
                  <td colSpan={readOnly ? 5 : 6} className="px-4 py-12 text-center text-gray-500">
                    <Receipt className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Nenhum item adicionado</p>
                    {!readOnly && (
                      <p className="text-sm">Clique em "Adicionar Item" para comecar</p>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Discount Section */}
        {!readOnly && (
          <Card className="p-4">
            <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
              <Percent className="w-4 h-4" />
              Desconto Global
            </h4>
            <div className="space-y-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setGlobalDiscountType('percentage')}
                  className={`
                    flex-1 py-2 px-4 rounded-lg border transition-colors
                    ${globalDiscountType === 'percentage'
                      ? 'bg-conecta-escuro text-white border-conecta-escuro'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <Percent className="w-4 h-4 mx-auto" />
                </button>
                <button
                  onClick={() => setGlobalDiscountType('fixed')}
                  className={`
                    flex-1 py-2 px-4 rounded-lg border transition-colors
                    ${globalDiscountType === 'fixed'
                      ? 'bg-conecta-escuro text-white border-conecta-escuro'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <DollarSign className="w-4 h-4 mx-auto" />
                </button>
              </div>
              <Input
                type="number"
                min={0}
                step={globalDiscountType === 'percentage' ? 1 : 0.01}
                value={globalDiscount}
                onChange={e => setGlobalDiscount(parseFloat(e.target.value) || 0)}
                placeholder={globalDiscountType === 'percentage' ? 'Desconto em %' : 'Valor do desconto'}
                rightIcon={
                  globalDiscountType === 'percentage'
                    ? <span className="text-gray-400">%</span>
                    : <span className="text-gray-400">R$</span>
                }
              />
            </div>
          </Card>
        )}

        {/* Totals */}
        <Card className={`p-4 ${readOnly ? 'md:col-span-2' : ''}`}>
          <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Resumo
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between text-gray-600">
              <span>Subtotal ({items.length} {items.length === 1 ? 'item' : 'itens'})</span>
              <span>{formatCurrency(subtotal)}</span>
            </div>

            {globalDiscount > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="flex justify-between text-red-500"
              >
                <span>Desconto</span>
                <span>
                  -{globalDiscountType === 'percentage'
                    ? `${globalDiscount}% (${formatCurrency(discountAmount)})`
                    : formatCurrency(discountAmount)
                  }
                </span>
              </motion.div>
            )}

            {taxRate > 0 && (
              <div className="flex justify-between text-gray-600">
                <span>Impostos ({taxRate}%)</span>
                <span>{formatCurrency(taxAmount)}</span>
              </div>
            )}

            <motion.div
              layout
              className="flex justify-between pt-3 border-t text-lg font-bold"
            >
              <span className="text-gray-900">Total</span>
              <motion.span
                key={total}
                initial={{ scale: 1.1 }}
                animate={{ scale: 1 }}
                className="text-conecta-escuro"
              >
                {formatCurrency(total)}
              </motion.span>
            </motion.div>
          </div>
        </Card>
      </div>

      {/* Quick Stats */}
      {items.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-blue-50 rounded-lg p-4"
          >
            <p className="text-sm text-blue-600">Total de Itens</p>
            <p className="text-2xl font-bold text-blue-700">{items.length}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-green-50 rounded-lg p-4"
          >
            <p className="text-sm text-green-600">Quantidade Total</p>
            <p className="text-2xl font-bold text-green-700">
              {items.reduce((acc, item) => acc + item.quantity, 0)}
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-orange-50 rounded-lg p-4"
          >
            <p className="text-sm text-orange-600">Preco Medio</p>
            <p className="text-2xl font-bold text-orange-700">
              {formatCurrency(items.length > 0 ? subtotal / items.length : 0)}
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-purple-50 rounded-lg p-4"
          >
            <p className="text-sm text-purple-600">Economia Total</p>
            <p className="text-2xl font-bold text-purple-700">
              {formatCurrency(discountAmount + items.reduce((acc, item) => {
                const itemSubtotal = item.quantity * item.unitPrice;
                return acc + (itemSubtotal * item.discount / 100);
              }, 0))}
            </p>
          </motion.div>
        </div>
      )}
    </div>
  );
}

// Mock data para demonstracao
// eslint-disable-next-line react-refresh/only-export-components
export const mockPricingItems: PricingItem[] = [
  { id: '1', name: 'Servico de Portaria 24h', quantity: 1, unitPrice: 15000, discount: 0 },
  { id: '2', name: 'Limpeza de Areas Comuns', quantity: 1, unitPrice: 8500, discount: 5 },
  { id: '3', name: 'Manutencao Predial', quantity: 1, unitPrice: 12000, discount: 10 },
  { id: '4', name: 'Jardinagem', quantity: 2, unitPrice: 3500, discount: 0 },
];

export default PricingCalculator;
