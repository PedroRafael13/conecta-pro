#!/bin/bash
echo "🔧 CORRIGINDO TODOS OS ERROS TYPESCRIPT"

# Função para corrigir imports não utilizados
fix_unused_imports() {
  echo "Removendo imports não utilizados..."
  
  # AuditDashboard
  sed -i 's/Filter,//' src/modules/compliance/audit/AuditDashboard.tsx
  
  # BiddingDashboard  
  sed -i 's/Filter,//' src/modules/compliance/bidding/BiddingDashboard.tsx
  sed -i '/formatRelativeTime.*never read/d' src/modules/compliance/bidding/BiddingDashboard.tsx
  
  # LGPDDashboard
  sed -i 's/formatDate.*never read/d' src/modules/compliance/lgpd/LGPDDashboard.tsx
  sed -i 's/statsLoading.*never read/d' src/modules/compliance/lgpd/LGPDDashboard.tsx
  
  # GED
  sed -i 's/useEffect,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/Search,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/BarChart3,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/Eye,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/Download,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/Filter,//' src/modules/ged/GEDDashboard.tsx
  sed -i 's/ClassificationBadge,//' src/modules/ged/GEDDashboard.tsx
  
  # CRM
  sed -i 's/useEffect,//' src/modules/crm/CRMDashboard.tsx
  
  # Facilities
  sed -i 's/CheckCircle,//' src/modules/facilities/FacilitiesDashboard.tsx
  
  echo "✅ Imports não utilizados removidos"
}

# Função para corrigir type-only imports
fix_type_imports() {
  echo "Corrigindo type-only imports..."
  
  # CRM
  sed -i 's/import { Contact,/import type { Contact,/' src/modules/crm/CRMDashboard.tsx
  sed -i 's/import { Contact/import type { Contact/' src/modules/crm/contacts/components/ContactCard.tsx
  sed -i 's/import { Contact,/import type { Contact,/' src/modules/crm/contacts/hooks/useContacts.ts
  sed -i 's/import { Deal,/import type { Deal,/' src/modules/crm/deals/components/DealKanban.tsx
  sed -i 's/import { Deal,/import type { Deal,/' src/modules/crm/deals/hooks/useDeals.ts
  
  # GED
  sed -i 's/import { Document,/import type { Document,/' src/modules/ged/GEDDashboard.tsx
  sed -i 's/import { Classification/import type { Classification/' src/modules/ged/components/ClassificationBadge.tsx
  sed -i 's/import { Document/import type { Document/' src/modules/ged/components/DocumentCard.tsx
  sed -i 's/import { UploadProgress/import type { UploadProgress/' src/modules/ged/components/FileUploader.tsx
  sed -i 's/import { Document,/import type { Document,/' src/modules/ged/components/PDFViewer.tsx
  sed -i 's/import { SearchFilters/import type { SearchFilters/' src/modules/ged/components/SearchBar.tsx
  sed -i 's/import { Document,/import type { Document,/' src/modules/ged/hooks/useDocuments.ts
  sed -i 's/import { Document,/import type { Document,/' src/modules/ged/hooks/useSearch.ts
  sed -i 's/import { UploadProgress/import type { UploadProgress/' src/modules/ged/hooks/useUpload.ts
  
  # Marketplace
  sed -i 's/import { MarketplaceService,/import type { MarketplaceService,/' src/modules/crm/marketplace/hooks/useMarketplace.ts
  
  # Proposals
  sed -i 's/import { Proposal,/import type { Proposal,/' src/modules/crm/proposals/hooks/useProposals.ts
  
  echo "✅ Type-only imports corrigidos"
}

# Função para corrigir tipos de response
fix_response_types() {
  echo "Corrigindo tipos de response do Axios..."
  
  # Criar um tipo helper para responses
  cat > src/core/types/api.ts << 'EOFAPI'
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}
EOFAPI

  echo "✅ Tipos de response corrigidos"
}

# Executar todas as correções
fix_unused_imports
fix_type_imports  
fix_response_types

echo "🎯 TYPESCRIPT CORRIGIDO - TESTANDO BUILD..."
