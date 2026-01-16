import React from 'react';
import { Brain, CheckCircle, AlertTriangle, XCircle, Tag } from 'lucide-react';
import type { Classification } from '../types';

interface ClassificationBadgeProps {
  classification: Classification;
  onOverride?: (newCategory: string) => void;
  showDetails?: boolean;
}

export const ClassificationBadge: React.FC<ClassificationBadgeProps> = ({
  classification,
  onOverride,
  showDetails = false,
}) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'yellow';
    return 'red';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return <CheckCircle className="w-3 h-3" />;
    if (confidence >= 0.6) return <AlertTriangle className="w-3 h-3" />;
    return <XCircle className="w-3 h-3" />;
  };

  const confidence = classification.confidence;
  const color = getConfidenceColor(confidence);

  const colorClasses = {
    green: {
      badge: 'bg-green-100 text-green-800 border-green-200',
      icon: 'text-green-600',
    },
    yellow: {
      badge: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: 'text-yellow-600',
    },
    red: {
      badge: 'bg-red-100 text-red-800 border-red-200',
      icon: 'text-red-600',
    },
  };

  return (
    <div className="space-y-2">
      {/* Main Classification Badge */}
      <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${colorClasses[color].badge}`}>
        <Brain className={`w-3 h-3 mr-1 ${colorClasses[color].icon}`} />
        <span>{classification.category}</span>
        <span className="ml-1 opacity-75">
          ({Math.round(confidence * 100)}%)
        </span>
        {getConfidenceIcon(confidence)}
      </div>

      {/* Detailed View */}
      {showDetails && (
        <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
          
          {/* Confidence Breakdown */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-gray-700">Confiança IA</span>
              <span className="text-xs text-gray-500">{Math.round(confidence * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  color === 'green' ? 'bg-green-500' : 
                  color === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
          </div>

          {/* Suggested Category */}
          <div className="mb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1">
                <Tag className="w-3 h-3 text-gray-400" />
                <span className="text-xs font-medium text-gray-700">Categoria Sugerida</span>
              </div>
              {onOverride && (
                <button
                  onClick={() => onOverride(classification.category)}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  Aceitar
                </button>
              )}
            </div>
            <p className="text-sm text-gray-900 mt-1">{classification.category}</p>
          </div>

          {/* Suggested Tags */}
          {classification.suggestedTags.length > 0 && (
            <div className="mb-3">
              <span className="text-xs font-medium text-gray-700 block mb-1">Tags Sugeridas</span>
              <div className="flex flex-wrap gap-1">
                {classification.suggestedTags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Extracted Entities */}
          {classification.extractedEntities.length > 0 && (
            <div>
              <span className="text-xs font-medium text-gray-700 block mb-2">Entidades Extraídas</span>
              <div className="space-y-2">
                {classification.extractedEntities.map((entity, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <div>
                      <span className="text-xs font-medium text-gray-900">{entity.value}</span>
                      <span className="text-xs text-gray-500 ml-2">({entity.type})</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {Math.round(entity.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Override Actions */}
          {onOverride && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-700">Categoria incorreta?</span>
                <select
                  onChange={(e) => e.target.value && onOverride(e.target.value)}
                  className="text-xs border border-gray-300 rounded px-2 py-1"
                  defaultValue=""
                >
                  <option value="">Corrigir para...</option>
                  <option value="financial">Financeiro</option>
                  <option value="legal">Jurídico</option>
                  <option value="hr">RH</option>
                  <option value="operational">Operacional</option>
                  <option value="commercial">Comercial</option>
                  <option value="administrative">Administrativo</option>
                </select>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
