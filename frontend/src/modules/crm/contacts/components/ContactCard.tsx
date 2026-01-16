import React from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  Building, 
  Star, 
  Tag,
  MoreVertical,
  Edit,
  Trash2,
  MessageSquare,
  Calendar
} from 'lucide-react';
import type { Contact } from '../../types';

interface ContactCardProps {
  contact: Contact;
  onEdit?: (contact: Contact) => void;
  onDelete?: (contact: Contact) => void;
  onClick?: (contact: Contact) => void;
}

export const ContactCard: React.FC<ContactCardProps> = ({
  contact,
  onEdit,
  onDelete,
  onClick,
}) => {
  const getStatusColor = (status: Contact['status']) => {
    switch (status) {
      case 'lead':
        return 'bg-yellow-100 text-yellow-800';
      case 'customer':
        return 'bg-green-100 text-green-800';
      case 'active':
        return 'bg-blue-100 text-blue-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSegmentColor = (segment: Contact['segment']) => {
    switch (segment) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-800';
      case 'mid-market':
        return 'bg-blue-100 text-blue-800';
      case 'small-business':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const renderLeadScore = (score?: number) => {
    if (!score) return null;
    
    const color = score >= 80 ? 'text-green-600' : 
                  score >= 60 ? 'text-yellow-600' : 'text-red-600';
    
    return (
      <div className={`flex items-center space-x-1 ${color}`}>
        <Star className="w-3 h-3 fill-current" />
        <span className="text-xs font-medium">{score}</span>
      </div>
    );
  };

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick?.(contact)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          {contact.avatar ? (
            <img
              src={contact.avatar}
              alt={contact.name}
              className="w-10 h-10 rounded-full object-cover"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="w-5 h-5 text-gray-500" />
            </div>
          )}
          
          <div className="flex-1">
            <h3 className="font-medium text-gray-900 truncate">{contact.name}</h3>
            {contact.position && (
              <p className="text-sm text-gray-500 truncate">{contact.position}</p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="relative group">
          <button className="text-gray-400 hover:text-gray-600 p-1">
            <MoreVertical className="w-4 h-4" />
          </button>
          
          <div className="absolute right-0 top-8 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-opacity">
            <div className="py-1">
              {onEdit && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(contact);
                  }}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Editar
                </button>
              )}
              <button
                onClick={(e) => e.stopPropagation()}
                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Nova Interação
              </button>
              <button
                onClick={(e) => e.stopPropagation()}
                className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                <Calendar className="w-4 h-4 mr-2" />
                Agendar Reunião
              </button>
              {onDelete && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(contact);
                  }}
                  className="flex items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Excluir
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Company */}
      {contact.company && (
        <div className="flex items-center text-sm text-gray-600 mb-2">
          <Building className="w-4 h-4 mr-1" />
          <span className="truncate">{contact.company}</span>
        </div>
      )}

      {/* Contact Info */}
      <div className="space-y-1 mb-3">
        <div className="flex items-center text-sm text-gray-600">
          <Mail className="w-4 h-4 mr-2" />
          <span className="truncate">{contact.email}</span>
        </div>
        
        {contact.phone && (
          <div className="flex items-center text-sm text-gray-600">
            <Phone className="w-4 h-4 mr-2" />
            <span>{contact.phone}</span>
          </div>
        )}
      </div>

      {/* Status & Segment */}
      <div className="flex items-center space-x-2 mb-3">
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contact.status)}`}>
          {contact.status}
        </span>
        
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSegmentColor(contact.segment)}`}>
          {contact.segment.replace('-', ' ')}
        </span>
      </div>

      {/* Tags */}
      {contact.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {contact.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700"
            >
              <Tag className="w-3 h-3 mr-1" />
              {tag}
            </span>
          ))}
          {contact.tags.length > 3 && (
            <span className="text-xs text-gray-500">
              +{contact.tags.length - 3} mais
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
        <div className="flex items-center space-x-4">
          {renderLeadScore(contact.leadScore)}
          <span>
            {contact.interactions.length} interações
          </span>
        </div>
        
        {contact.lastContact && (
          <span>
            Último: {new Date(contact.lastContact).toLocaleDateString('pt-BR')}
          </span>
        )}
      </div>
    </div>
  );
};
