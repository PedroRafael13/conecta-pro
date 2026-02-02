/**
 * AI Bartolo API Type Stubs
 */

export interface SendMessageRequest {
  message: string;
  context?: Record<string, unknown>;
  session_id?: string;
  module?: string;
  metadata?: Record<string, unknown>;
}

export interface SendMessageResponse {
  response: string;
  message_id?: string;
  response_html?: string;
  suggestions?: string[];
  actions?: Array<Record<string, unknown>>;
  data_results?: unknown;
  context?: Record<string, unknown>;
}

export interface FeedbackRequest {
  message_id?: string;
  interaction_id?: string;
  rating?: number;
  feedback_type?: string;
  comment?: string;
}

export interface WizardStartRequest {
  wizard_type: string;
  params?: Record<string, unknown>;
}

export interface WizardInputRequest {
  wizard_id: string;
  step: string;
  data: Record<string, unknown>;
}

export type EntityType = string;
