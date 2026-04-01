export interface BartoloMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  contentHtml?: string;
  timestamp: Date;
  suggestions?: string[];
  actions?: BartoloAction[];
}

export interface BartoloAction {
  type: 'navigate' | 'create' | 'edit' | 'delete' | 'export' | 'help';
  label: string;
  target?: string;
  data?: Record<string, unknown>;
}

export interface ActionPreview {
  action_id: string;
  action_type: string;
  title: string;
  description: string;
  affected_entities: Array<{
    type: string;
    id: string;
    name?: string;
  }>;
  changes_summary: string[];
  warnings: string[];
  required_permission: string;
  user_has_permission: boolean;
  parameters: Record<string, unknown>;
  can_be_undone: boolean;
  requires_confirmation: boolean;
}
