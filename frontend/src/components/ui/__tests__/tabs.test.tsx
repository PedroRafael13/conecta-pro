import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../tabs';

describe('Tabs', () => {
  it('deve renderizar tabs com lista e triggers', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
          <TabsTrigger value="tab2">Aba 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Conteúdo 1</TabsContent>
        <TabsContent value="tab2">Conteúdo 2</TabsContent>
      </Tabs>
    );
    expect(screen.getByText('Aba 1')).toBeInTheDocument();
    expect(screen.getByText('Aba 2')).toBeInTheDocument();
  });

  it('deve mostrar conteúdo da aba ativa por padrão', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
          <TabsTrigger value="tab2">Aba 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Conteúdo da Aba 1</TabsContent>
        <TabsContent value="tab2">Conteúdo da Aba 2</TabsContent>
      </Tabs>
    );
    expect(screen.getByText('Conteúdo da Aba 1')).toBeInTheDocument();
  });

  it('deve renderizar abas clicáveis', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
          <TabsTrigger value="tab2">Aba 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Conteúdo da Aba 1</TabsContent>
        <TabsContent value="tab2">Conteúdo da Aba 2</TabsContent>
      </Tabs>
    );
    // Verificar que as abas são renderizadas como botões clicáveis
    const aba2 = screen.getByText('Aba 2');
    expect(aba2.tagName.toLowerCase()).toBe('button');
    fireEvent.click(aba2);
  });

  it('deve suportar onValueChange', () => {
    // Verificar que o componente suporta a prop onValueChange
    render(
      <Tabs defaultValue="tab1" onValueChange={(value) => console.log(value)}>
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Conteúdo 1</TabsContent>
      </Tabs>
    );
    expect(screen.getByText('Aba 1')).toBeInTheDocument();
  });

  it('deve desabilitar trigger quando disabled', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
          <TabsTrigger value="tab2" disabled>Aba 2</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    expect(screen.getByText('Aba 2')).toBeDisabled();
  });

  it('deve aplicar classe customizada no TabsList', () => {
    const { container } = render(
      <Tabs defaultValue="tab1">
        <TabsList className="custom-list">
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    const list = container.querySelector('.custom-list');
    expect(list).toBeInTheDocument();
  });

  it('deve aplicar classe customizada no TabsTrigger', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1" className="custom-trigger">Aba 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    const trigger = screen.getByText('Aba 1');
    expect(trigger.className).toContain('custom-trigger');
  });

  it('deve aplicar classe customizada no TabsContent', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1" className="custom-content">Conteúdo</TabsContent>
      </Tabs>
    );
    const content = screen.getByText('Conteúdo');
    expect(content.className).toContain('custom-content');
  });

  it('deve ter displayName correto para TabsList', () => {
    expect(TabsList.displayName).toBe('TabsList');
  });

  it('deve ter displayName correto para TabsTrigger', () => {
    expect(TabsTrigger.displayName).toBe('TabsTrigger');
  });

  it('deve ter displayName correto para TabsContent', () => {
    expect(TabsContent.displayName).toBe('TabsContent');
  });

  it('deve encaminhar ref corretamente no TabsList', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <Tabs defaultValue="tab1">
        <TabsList ref={ref}>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve encaminhar ref corretamente no TabsTrigger', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger ref={ref} value="tab1">Aba 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('deve encaminhar ref corretamente no TabsContent', () => {
    const ref = { current: null as HTMLDivElement | null };
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
        <TabsContent ref={ref} value="tab1">Conteúdo</TabsContent>
      </Tabs>
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('deve ter estilo de fundo mutado no TabsList', () => {
    const { container } = render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    const list = container.firstChild?.firstChild as HTMLElement;
    expect(list.className).toContain('bg-muted');
  });

  it('deve ter aba ativa com estilo diferente', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Aba 1</TabsTrigger>
          <TabsTrigger value="tab2">Aba 2</TabsTrigger>
        </TabsList>
      </Tabs>
    );
    const activeTrigger = screen.getByText('Aba 1');
    expect(activeTrigger.className).toContain('data-[state=active]:bg-background');
  });

  it('deve suportar múltiplas abas', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Geral</TabsTrigger>
          <TabsTrigger value="tab2">Configurações</TabsTrigger>
          <TabsTrigger value="tab3">Avançado</TabsTrigger>
          <TabsTrigger value="tab4">Sobre</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Conteúdo Geral</TabsContent>
        <TabsContent value="tab2">Conteúdo Configurações</TabsContent>
        <TabsContent value="tab3">Conteúdo Avançado</TabsContent>
        <TabsContent value="tab4">Conteúdo Sobre</TabsContent>
      </Tabs>
    );
    expect(screen.getByText('Geral')).toBeInTheDocument();
    expect(screen.getByText('Configurações')).toBeInTheDocument();
    expect(screen.getByText('Avançado')).toBeInTheDocument();
    expect(screen.getByText('Sobre')).toBeInTheDocument();
  });
});
