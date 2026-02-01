import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

function HelloWorld() {
  return <div>Hello Conecta PRO</div>;
}

describe('Smoke Test', () => {
  it('renderiza corretamente', () => {
    render(<HelloWorld />);
    expect(screen.getByText('Hello Conecta PRO')).toBeInTheDocument();
  });

  it('environment esta configurado', () => {
    expect(typeof window).toBe('object');
    expect(typeof document).toBe('object');
  });
});
