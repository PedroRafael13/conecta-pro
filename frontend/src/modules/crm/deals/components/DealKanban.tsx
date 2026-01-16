import React, { useState } from 'react';
import { 
  DollarSign, 
  Calendar, 
  User, 
  TrendingUp,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Plus
} from 'lucide-react';
import type { Deal, DealStage } from '../../types';

interface DealKanbanProps {
  dealsByStage: Record<string, Deal[]>;
  stages: DealStage[];
  onMoveDealf?: (dealId: string, newStageId: string) => void;
  onEditDeal?: (deal: Deal) => void;
  onDeleteDeal?: (deal: Deal) => void;
  onViewDeal?: (deal: Deal) => void;
  onCreateDeal?: (stageId: string) => void;
}

interface DealCardProps {
  deal: Deal;
  onEdit?: (deal: Deal) => void;
  onDelete?: (deal: Deal) => void;
  onView?: (deal: Deal) => void;
}

const DealCard: React.FC<DealCardProps> = ({ deal, onEdit, onDelete, onView }) => {
  const [showMenu, setShowMenu] = useState(false);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
    });
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 80) return 'bg-green-500';
    if (probability >= 60) return 'bg-yellow-500';
    if (probability >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const isOverdue = new Date(deal.expectedCloseDate) < new Date();

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onView?.(deal)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900 truncate">{deal.title}</h4>
          {deal.contact && (
            <p className="text-sm text-gray-500 truncate">{deal.contact.name}</p>
          )}
        </div>
        
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {showMenu && (
            <div className="absolute right-0 top-8 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
              <div className="py-1">
                {onView && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onView(deal);
                      setShowMenu(false);
                    }}
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Visualizar
                  </button>
                )}
                {onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(deal);
                      setShowMenu(false);
                    }}
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(deal);
                      setShowMenu(false);
                    }}
                    className="flex items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Excluir
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Value */}
      <div className="flex items-center mb-3">
        <DollarSign className="w-4 h-4 text-green-600 mr-1" />
        <span className="text-lg font-semibold text-gray-900">
          {formatCurrency(deal.value)}
        </span>
      </div>

      {/* Probability */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-500">Probabilidade</span>
          <span className="text-xs font-medium text-gray-900">{deal.probability}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getProbabilityColor(deal.probability)}`}
            style={{ width: `${deal.probability}%` }}
          />
        </div>
      </div>

      {/* Expected Close Date */}
      <div className="flex items-center mb-3">
        <Calendar className={`w-4 h-4 mr-1 ${isOverdue ? 'text-red-500' : 'text-gray-500'}`} />
        <span className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-gray-600'}`}>
          {formatDate(deal.expectedCloseDate)}
          {isOverdue && ' (Atrasado)'}
        </span>
      </div>

      {/* Assigned To */}
      <div className="flex items-center mb-3">
        <User className="w-4 h-4 text-gray-500 mr-1" />
        <span className="text-sm text-gray-600 truncate">{deal.assignedTo}</span>
      </div>

      {/* Tags */}
      {deal.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {deal.tags.slice(0, 2).map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
            >
              {tag}
            </span>
          ))}
          {deal.tags.length > 2 && (
            <span className="text-xs text-gray-500">
              +{deal.tags.length - 2}
            </span>
          )}
        </div>
      )}

      {/* Activities Count */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{deal.activities.length} atividades</span>
        <div className="flex items-center">
          <TrendingUp className="w-3 h-3 mr-1" />
          <span>Score: {Math.round(deal.probability * deal.value / 1000)}</span>
        </div>
      </div>
    </div>
  );
};

export const DealKanban: React.FC<DealKanbanProps> = ({
  dealsByStage,
  stages,
  onMoveDealf,
  onEditDeal,
  onDeleteDeal,
  onViewDeal,
  onCreateDeal,
}) => {
  const calculateStageValue = (deals: Deal[]) => {
    return deals.reduce((sum, deal) => sum + deal.value, 0);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const handleDragStart = (e: React.DragEvent, deal: Deal) => {
    e.dataTransfer.setData('dealId', deal.id);
    e.dataTransfer.setData('currentStageId', deal.stage.id);
  };

  const handleDrop = (e: React.DragEvent, targetStageId: string) => {
    e.preventDefault();
    const dealId = e.dataTransfer.getData('dealId');
    const currentStageId = e.dataTransfer.getData('currentStageId');
    
    if (dealId && currentStageId !== targetStageId && onMoveDealf) {
      onMoveDealf(dealId, targetStageId);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="flex space-x-6 overflow-x-auto pb-4">
      {stages.map((stage) => {
        const stageDeals = dealsByStage[stage.id] || [];
        const stageValue = calculateStageValue(stageDeals);
        
        return (
          <div
            key={stage.id}
            className="flex-shrink-0 w-80 bg-gray-50 rounded-lg p-4"
            onDrop={(e) => handleDrop(e, stage.id)}
            onDragOver={handleDragOver}
          >
            {/* Stage Header */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 flex items-center">
                  <span 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: stage.color }}
                  />
                  {stage.name}
                </h3>
                {onCreateDeal && (
                  <button
                    onClick={() => onCreateDeal(stage.id)}
                    className="text-gray-500 hover:text-gray-700 p-1"
                    title="Criar deal"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              <div className="text-sm text-gray-600">
                <span className="font-medium">{stageDeals.length}</span> deals
                <span className="mx-2">•</span>
                <span className="font-medium">{formatCurrency(stageValue)}</span>
              </div>
              
              <div className="text-xs text-gray-500">
                Probabilidade média: {stage.probability}%
              </div>
            </div>

            {/* Deals */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {stageDeals.map((deal) => (
                <div
                  key={deal.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, deal)}
                  className="cursor-move"
                >
                  <DealCard
                    deal={deal}
                    onEdit={onEditDeal}
                    onDelete={onDeleteDeal}
                    onView={onViewDeal}
                  />
                </div>
              ))}
              
              {stageDeals.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Nenhum deal neste estágio</p>
                  {onCreateDeal && (
                    <button
                      onClick={() => onCreateDeal(stage.id)}
                      className="text-blue-600 text-sm hover:text-blue-700 mt-2"
                    >
                      Criar primeiro deal
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
