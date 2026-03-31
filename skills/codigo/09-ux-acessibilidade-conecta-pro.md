---
name: ux-acessibilidade-conecta-pro
description: Auditoria de UX, acessibilidade e qualidade visual do frontend do Conecta PRO — Next.js 16 + Tailwind. Usar para corrigir problemas visuais reportados por Jordan, garantir consistência de interface e melhorar a experiência de uso do ERP.
---

# UX e Qualidade Visual — Conecta PRO

## Design System
- Azul marinho primário: `#1E3A5F` / `#0A2540`
- Laranja acento: `#F97316` / `#FF6B35`
- Branco: `#FFFFFF`
- Logo: CONECTA (branco) + PRO (laranja) + engrenagem SVG
- Fonte: -apple-system, 'Segoe UI', sans-serif
- Framework: Tailwind CSS

## Quando usar
- Jordan reporta que interface está "feia" ou difícil de usar
- Modal com fundo transparente ilegível
- Markdown bruto (`**texto**`) aparecendo no chat
- Dropdown vazio, botão sem ação, form que não valida
- Cores não combinam ou quebram o padrão da marca

## Checklist visual por componente

### Modais e Dialogs
```tsx
// ✅ CORRETO — modal legível e acessível
<div className="fixed inset-0 bg-black/70 z-50
                flex items-center justify-center p-4">
  <div className="bg-white rounded-xl shadow-2xl
                  border border-gray-200 p-6
                  max-w-lg w-full">
    {/* Título */}
    <h2 className="text-gray-900 font-bold text-lg mb-4">
      {titulo}
    </h2>

    {/* Área de avisos — amarelo claro, legível */}
    {avisos.length > 0 && (
      <div className="bg-yellow-50 border border-yellow-200
                      rounded-lg p-4 mb-4">
        {avisos.map((aviso, i) => (
          <div key={i} className="flex items-start gap-2
                                   text-yellow-800 text-sm mb-1">
            <span>⚠️</span>
            <span>{aviso}</span>
          </div>
        ))}
      </div>
    )}

    {/* Botões */}
    <div className="flex justify-end gap-2 mt-4">
      <button className="px-4 py-2 bg-white border
                         border-gray-300 text-gray-700
                         rounded-lg hover:bg-gray-50">
        Cancelar
      </button>
      <button className="px-4 py-2 bg-blue-600
                         text-white rounded-lg
                         hover:bg-blue-700">
        Confirmar
      </button>
    </div>
  </div>
</div>

// ❌ ERRADO — fundo marrom transparente, texto preto ilegível
<div className="bg-amber-900/50 rounded p-4 text-black">
```

### Dropdowns — carregar dados corretamente
```tsx
// ✅ CORRETO — buscar clientes ao abrir o modal
const [clientes, setClientes] = useState([])
const [isOpen, setIsOpen] = useState(false)

useEffect(() => {
  if (!isOpen) return  // ← SÓ busca quando modal abre
  fetch('/api/v1/ged/clients', {
    headers: { Authorization: `Bearer ${token}` }
  })
    .then(r => r.json())
    .then(data => {
      const lista = Array.isArray(data) ? data :
                    data.clients || data.data || []
      setClientes(lista)
    })
}, [isOpen])  // ← isOpen como dependência

// ❌ ERRADO — busca só na montagem, não quando modal abre
useEffect(() => {
  fetch('/api/v1/ged/clients', ...)
}, [])  // ← [] significa só na montagem
```

### Renderização de Markdown no Bartolo
```tsx
// Instalar: npm install react-markdown
import ReactMarkdown from 'react-markdown'

// ✅ CORRETO — renderizar markdown como HTML
<div className="prose prose-sm max-w-none">
  <ReactMarkdown>{mensagem.content}</ReactMarkdown>
</div>

// ❌ ERRADO — exibe **texto** bruto
<p>{mensagem.content}</p>
```

### Indicadores de loading
```tsx
// ✅ Sempre mostrar loading enquanto busca dados
const [loading, setLoading] = useState(false)

const buscarDados = async () => {
  setLoading(true)
  try {
    const data = await fetch(url, headers)
    setDados(await data.json())
  } finally {
    setLoading(false)
  }
}

// No JSX
{loading ? (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin w-6 h-6 border-2
                    border-orange-500 border-t-transparent
                    rounded-full"/>
  </div>
) : (
  <ListaDeItems dados={dados}/>
)}
```

## Auditoria de problemas visuais comuns

```bash
# Verificar erros de TypeScript que causam problemas visuais
cd /opt/conecta-pro/frontend
npx tsc --noEmit 2>&1 | head -20

# Verificar warnings do ESLint
npm run lint 2>&1 | grep -i "warning\|error" | head -20

# Verificar tamanho das páginas (pesadas = lentas)
find .next -name "*.js" -size +500k 2>/dev/null \
  | while read f; do
    echo "$(du -sh $f | cut -f1) → $f"
  done | sort -rh | head -10
```

## Padrão de cores do Conecta PRO — referência

```css
/* Variáveis de cor — usar em todos os componentes */
:root {
  --azul-primario: #1E3A5F;
  --azul-escuro: #0A2540;
  --azul-medio: #2E5984;
  --laranja-primario: #F97316;
  --laranja-hover: #EA6A0A;
  --laranja-claro: #FF6B35;
  --branco: #FFFFFF;
  --cinza-claro: #F8F9FB;
  --cinza-borda: #E9ECEF;
  --texto-primario: #111827;
  --texto-secundario: #6B7280;
  --sucesso: #10B981;
  --erro: #EF4444;
  --aviso: #F59E0B;
}

/* Tailwind equivalentes */
/* azul-primario = [#1E3A5F] */
/* laranja = orange-500 = #F97316 */
```

## Bugs visuais recorrentes — verificar sempre

```
[ ] Modal de confirmação: fundo marrom/âmbar → usar bg-white
[ ] Texto de aviso: cor preta sobre fundo laranja → usar text-yellow-800 sobre bg-yellow-50
[ ] Dropdown vazio: useEffect sem isOpen como dependência
[ ] Markdown bruto: instalar react-markdown ou remover ** do backend
[ ] Coluna "Cliente" vazia: verificar LEFT JOIN no SELECT da query
[ ] Indicadores R$ 0,00: endpoint retorna undefined → formatCurrency(undefined)
[ ] Loading infinito: useState não sendo setado no catch do try/catch
```
