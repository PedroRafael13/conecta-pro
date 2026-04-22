export interface CNPJEnrichment {
  cnpj: string;
  razao_social: string | null;
  nome_fantasia: string | null;
  cnae_principal: string | null;
  cnaes_secundarios: string[];
  qsa: Array<{
    nome_socio: string | null;
    qualificacao_socio: string | null;
    data_entrada_sociedade: string | null;
  }>;
  capital_social: number | null;
  situacao: string | null;
  endereco: {
    logradouro: string | null;
    numero: string | null;
    complemento: string | null;
    bairro: string | null;
    municipio: string | null;
    uf: string | null;
    cep: string | null;
  };
  telefone: string | null;
  porte: string | null;
  data_abertura: string | null;
  simples_nacional: boolean | null;
  cache_hit: boolean;
}

export interface CEPEnrichment {
  cep: string;
  logradouro: string | null;
  bairro: string | null;
  cidade: string | null;
  uf: string | null;
  coordenadas: { latitude: string; longitude: string } | null;
  cache_hit: boolean;
}

export interface TaxasResponse {
  taxas: Array<{ nome: string; valor: number }>;
  selic: number | null;
  cdi: number | null;
  ipca: number | null;
  cache_hit: boolean;
}
