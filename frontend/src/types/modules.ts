;

// Definição de um módulo do sistema
export interface Module {
  id: string;
  title: string;
  description: string;
  icon: string; // Nome do ícone Lucide
  href: string;
  color: 'cyan' | 'green' | 'orange' | 'purple' | 'red' | 'blue' | 'yellow' | 'pink';
  permissions: string[];
  subModules: SubModule[];
  badge?: string | number;
  enabled: boolean;
}

// Sub-módulo (aparece na sidebar após clicar no card)
export interface SubModule {
  id: string;
  title: string;
  href: string;
  icon: string;
  permissions: string[];
  badge?: number;
}

// Configuração de módulos por categoria
export interface ModuleCategory {
  id: string;
  title: string;
  modules: Module[];
}

// Roles de usuário
export type UserRole =
  | 'admin'
  | 'gerente'
  | 'supervisor'
  | 'operacional'
  | 'financeiro'
  | 'rh'
  | 'comercial'
  | 'cliente';

// Mapeamento de permissões por role
export const rolePermissions: Record<UserRole, string[]> = {
  admin: ['*'], // Acesso total
  gerente: [
    'crm:*',
    'financial:read',
    'financial:write',
    'operacional:*',
    'reports:*',
    'bidding:*', // Licitações - acesso completo
  ],
  supervisor: [
    'crm:read',
    'operacional:*',
    'campo:*',
    'reports:read',
    'bidding:read', // Licitações - leitura
  ],
  operacional: [
    'campo:read',
    'campo:write',
    'operacional:read',
  ],
  financeiro: [
    'financial:*',
    'government:*',
    'reports:financial',
    'bidding:*', // Licitações - acesso completo
  ],
  rh: [
    'users:*',
    'operacional:rh',
    'reports:rh',
  ],
  comercial: [
    'crm:*',
    'services:*',
    'reports:comercial',
    'bidding:read', // Licitações - leitura
  ],
  cliente: [
    'portal:*',
  ],
};

// Verificar se usuário tem permissão
export function hasPermission(userRole: UserRole, requiredPermissions: string[]): boolean {
  const userPermissions = rolePermissions[userRole];

  // Admin tem acesso total
  if (userPermissions.includes('*')) return true;

  // Verificar se tem alguma das permissões requeridas
  return requiredPermissions.some((required) => {
    return userPermissions.some((userPerm) => {
      // Permissão exata
      if (userPerm === required) return true;

      // Permissão com wildcard (ex: crm:* permite crm:read)
      if (userPerm.endsWith(':*')) {
        const prefix = userPerm.slice(0, -1); // Remove *
        return required.startsWith(prefix);
      }

      return false;
    });
  });
}
