'use client';

import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';

interface ConfigValueEditorProps {
  value: unknown;
  valueType: string;
  onChange: (value: unknown) => void;
  disabled?: boolean;
}

export function ConfigValueEditor({ value, valueType, onChange, disabled }: ConfigValueEditorProps) {
  switch (valueType) {
    case 'boolean':
      return (
        <Switch
          checked={Boolean(value)}
          onCheckedChange={(checked) => onChange(checked)}
          disabled={disabled}
        />
      );

    case 'number':
      return (
        <Input
          type="number"
          value={value !== undefined && value !== null ? String(value) : ''}
          onChange={(e) => onChange(Number(e.target.value))}
          disabled={disabled}
          className="w-48"
        />
      );

    case 'json':
      return (
        <Textarea
          value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
          onChange={(e) => {
            try {
              onChange(JSON.parse(e.target.value));
            } catch {
              onChange(e.target.value);
            }
          }}
          disabled={disabled}
          rows={4}
          className="font-mono text-xs"
        />
      );

    default: // string
      return (
        <Input
          value={String(value ?? '')}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
        />
      );
  }
}
