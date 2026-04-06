'use client';

import { Bot } from 'lucide-react';

export default function AssistentePage() {
  return (
    <div className="flex flex-col items-center justify-center h-96 gap-4 text-gray-500">
      <Bot className="h-12 w-12 text-gray-300" />
      <h1 className="text-xl font-semibold text-gray-700">Assistente em breve</h1>
      <p className="text-sm">Novo assistente de IA em desenvolvimento.</p>
    </div>
  );
}
