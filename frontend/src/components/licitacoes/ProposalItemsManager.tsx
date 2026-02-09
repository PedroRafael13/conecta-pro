'use client';

import { useState } from 'react';
import {
  Plus,
  Edit,
  Trash2,
  Package,
  DollarSign,
  Hash,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Modal, ModalFooter } from '@/components/ui/modal';
import { Card } from '@/components/ui/card';
import type { ProposalItemResponse } from '@/services/bidding/proposals.service';

interface ProposalItemsManagerProps {
  items: ProposalItemResponse[];
  isLoading?: boolean;
  onAddItem: (item: ItemFormData) => Promise<void>;
  onUpdateItem: (itemId: string, item: ItemFormData) => Promise<void>;
  onRemoveItem: (itemId: string) => Promise<void>;
}

interface ItemFormData {
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  unidade_medida?: string;
}

export function ProposalItemsManager({
  items,
  isLoading = false,
  onAddItem,
  onUpdateItem,
  onRemoveItem,
}: ProposalItemsManagerProps) {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ProposalItemResponse | null>(
    null
  );
  const [itemToDelete, setItemToDelete] = useState<ProposalItemResponse | null>(
    null
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<ItemFormData>({
    descricao: '',
    quantidade: 1,
    valor_unitario: 0,
    unidade_medida: 'UN',
  });

  const valorTotal =
    items?.reduce((acc, item) => acc + (item.valor_total || 0), 0) || 0;

  const handleOpenForm = (item?: ProposalItemResponse) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        descricao: item.descricao,
        quantidade: item.quantidade,
        valor_unitario: item.valor_unitario,
        unidade_medida: (item as any).unidade_medida || 'UN',
      });
    } else {
      setEditingItem(null);
      setFormData({
        descricao: '',
        quantidade: 1,
        valor_unitario: 0,
        unidade_medida: 'UN',
      });
    }
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingItem(null);
    setFormData({
      descricao: '',
      quantidade: 1,
      valor_unitario: 0,
      unidade_medida: 'UN',
    });
  };

  const handleSubmitForm = async () => {
    setIsSubmitting(true);
    try {
      if (editingItem) {
        await onUpdateItem(editingItem.id, formData);
      } else {
        await onAddItem(formData);
      }
      handleCloseForm();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDeleteDialog = (item: ProposalItemResponse) => {
    setItemToDelete(item);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!itemToDelete) return;
    setIsSubmitting(true);
    try {
      await onRemoveItem(itemToDelete.id);
      setIsDeleteDialogOpen(false);
      setItemToDelete(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Package className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-semibold">Itens da Proposta</h3>
            <span className="text-sm text-muted-foreground">
              ({items?.length || 0} {items?.length === 1 ? 'item' : 'itens'})
            </span>
          </div>
          <Button onClick={() => handleOpenForm()} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Adicionar Item
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : items?.length > 0 ? (
          <>
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Descrição</TableHead>
                    <TableHead className="text-center">Unidade</TableHead>
                    <TableHead className="text-right">Quantidade</TableHead>
                    <TableHead className="text-right">Valor Unit.</TableHead>
                    <TableHead className="text-right">Valor Total</TableHead>
                    <TableHead className="text-center w-[100px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">
                        {item.descricao}
                      </TableCell>
                      <TableCell className="text-center">
                        {(item as any).unidade_medida || 'UN'}
                      </TableCell>
                      <TableCell className="text-right">
                        {item.quantidade}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(item.valor_unitario)}
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.valor_total)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleOpenForm(item)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleOpenDeleteDialog(item)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="flex justify-end pt-4 border-t">
              <div className="space-y-2">
                <div className="flex items-center gap-4 text-lg font-bold">
                  <span>Valor Total:</span>
                  <span className="text-green-600">
                    {formatCurrency(valorTotal)}
                  </span>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Package className="h-12 w-12 mx-auto mb-2 opacity-30" />
            <p>Nenhum item adicionado</p>
            <p className="text-sm">Clique em &quot;Adicionar Item&quot; para começar</p>
          </div>
        )}
      </Card>

      {/* Modal de Formulário */}
      <Modal
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        title={editingItem ? 'Editar Item' : 'Adicionar Item'}
        size="lg"
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="descricao">
              Descrição do Item <span className="text-destructive">*</span>
            </Label>
            <Input
              id="descricao"
              value={formData.descricao}
              onChange={(e) =>
                setFormData({ ...formData, descricao: e.target.value })
              }
              placeholder="Ex: Serviço de vigilância armada"
              disabled={isSubmitting}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="unidade_medida">Unidade</Label>
              <Input
                id="unidade_medida"
                value={formData.unidade_medida}
                onChange={(e) =>
                  setFormData({ ...formData, unidade_medida: e.target.value })
                }
                placeholder="UN"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantidade">
                Quantidade <span className="text-destructive">*</span>
              </Label>
              <Input
                id="quantidade"
                type="number"
                min="0"
                step="1"
                value={formData.quantidade}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    quantidade: parseFloat(e.target.value) || 0,
                  })
                }
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="valor_unitario">
                Valor Unitário (R$) <span className="text-destructive">*</span>
              </Label>
              <Input
                id="valor_unitario"
                type="number"
                min="0"
                step="0.01"
                value={formData.valor_unitario}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    valor_unitario: parseFloat(e.target.value) || 0,
                  })
                }
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="bg-muted p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="font-medium">Valor Total do Item:</span>
              <span className="text-lg font-bold text-green-600">
                {formatCurrency(formData.quantidade * formData.valor_unitario)}
              </span>
            </div>
          </div>
        </div>

        <ModalFooter>
          <Button
            variant="outline"
            onClick={handleCloseForm}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSubmitForm}
            disabled={
              !formData.descricao ||
              formData.quantidade <= 0 ||
              formData.valor_unitario <= 0 ||
              isSubmitting
            }
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : editingItem ? (
              'Atualizar Item'
            ) : (
              'Adicionar Item'
            )}
          </Button>
        </ModalFooter>
      </Modal>

      {/* Dialog de Confirmação de Exclusão */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja remover o item{' '}
              <strong>{itemToDelete?.descricao}</strong>?
              <br />
              Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isSubmitting}>
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={isSubmitting}
              className="bg-destructive hover:bg-destructive/90"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Removendo...
                </>
              ) : (
                'Remover Item'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
