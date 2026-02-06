/**
 * Validações de documentos e dados brasileiros
 */

/**
 * Remove caracteres não numéricos
 */
const clean = (value: string): string => value.replace(/\D/g, '');

/**
 * Calcula o dígito verificador do CPF
 */
const calculateCPFCheckDigit = (digits: number[]): number => {
  const sum = digits.reduce((acc, digit, index) => {
    return acc + digit * (digits.length + 1 - index);
  }, 0);
  const remainder = sum % 11;
  return remainder < 2 ? 0 : 11 - remainder;
};

/**
 * Valida se um CPF é válido
 * Aceita formatado (123.456.789-09) ou não (12345678909)
 */
export const isValidCPF = (cpf: string): boolean => {
  if (!cpf) return false;

  const cleaned = clean(cpf);

  // CPF deve ter 11 dígitos
  if (cleaned.length !== 11) return false;

  // Verifica se todos os dígitos são iguais (CPF inválido)
  if (/^(\d)\1{10}$/.test(cleaned)) return false;

  const digits = cleaned.split('').map(Number);

  // Calcula o primeiro dígito verificador
  const firstDigit = calculateCPFCheckDigit(digits.slice(0, 9));
  if (firstDigit !== digits[9]) return false;

  // Calcula o segundo dígito verificador
  const secondDigit = calculateCPFCheckDigit(digits.slice(0, 10));
  if (secondDigit !== digits[10]) return false;

  return true;
};

/**
 * Calcula o dígito verificador do CNPJ
 */
const calculateCNPJCheckDigit = (digits: number[], weights: number[]): number => {
  const sum = digits.reduce((acc, digit, index) => {
    return acc + digit * weights[index]!;
  }, 0);
  const remainder = sum % 11;
  return remainder < 2 ? 0 : 11 - remainder;
};

/**
 * Valida se um CNPJ é válido
 * Aceita formatado (11.222.333/0001-81) ou não (11222333000181)
 */
export const isValidCNPJ = (cnpj: string): boolean => {
  if (!cnpj) return false;

  const cleaned = clean(cnpj);

  // CNPJ deve ter 14 dígitos
  if (cleaned.length !== 14) return false;

  // Verifica se todos os dígitos são iguais (CNPJ inválido)
  if (/^(\d)\1{13}$/.test(cleaned)) return false;

  const digits = cleaned.split('').map(Number);

  // Pesos para o primeiro dígito verificador
  const firstWeights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const firstDigit = calculateCNPJCheckDigit(digits.slice(0, 12), firstWeights);
  if (firstDigit !== digits[12]) return false;

  // Pesos para o segundo dígito verificador
  const secondWeights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const secondDigit = calculateCNPJCheckDigit(digits.slice(0, 13), secondWeights);
  if (secondDigit !== digits[13]) return false;

  return true;
};

/**
 * Valida se um email é válido
 */
export const isValidEmail = (email: string): boolean => {
  if (!email) return false;

  // Regex básica para validação de email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Valida se um telefone brasileiro é válido
 * Aceita formatado ou não, celular (11 dígitos) ou fixo (10 dígitos)
 */
export const isValidPhone = (phone: string): boolean => {
  if (!phone) return false;

  const cleaned = clean(phone);

  // Telefone deve ter 10 (fixo) ou 11 (celular) dígitos
  if (cleaned.length !== 10 && cleaned.length !== 11) return false;

  // Verifica DDD (deve estar entre 11 e 99)
  const ddd = parseInt(cleaned.substring(0, 2), 10);
  if (ddd < 11 || ddd > 99) return false;

  // Se for celular (11 dígitos), o nono dígito deve ser 9
  if (cleaned.length === 11) {
    const ninthDigit = parseInt(cleaned[2]!, 10);
    if (ninthDigit !== 9) return false;
  }

  return true;
};

/**
 * Valida se um CEP é válido
 * Aceita formatado (12345-678) ou não (12345678)
 */
export const isValidCEP = (cep: string): boolean => {
  if (!cep) return false;

  const cleaned = clean(cep);

  // CEP deve ter 8 dígitos
  return cleaned.length === 8;
};

/**
 * Valida se uma data é válida
 * Aceita Date object ou string ISO (YYYY-MM-DD)
 */
export const isValidDate = (date: Date | string): boolean => {
  if (!date) return false;

  const dateObj = date instanceof Date ? date : new Date(date);

  // Verifica se é uma data válida
  if (isNaN(dateObj.getTime())) return false;

  // Se for string, verifica se o formato está correto
  if (typeof date === 'string') {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
      // Aceita formato ISO completo também
      const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;
      if (!isoRegex.test(date)) return false;
    }

    // Verifica se a data existe (não é 32/13/2024 por exemplo)
    const dateParts = date.split('T')[0]!.split('-').map(Number);
    const year = dateParts[0]!;
    const month = dateParts[1]!;
    const day = dateParts[2]!;
    const testDate = new Date(year, month - 1, day);
    if (
      testDate.getFullYear() !== year ||
      testDate.getMonth() !== month - 1 ||
      testDate.getDate() !== day
    ) {
      return false;
    }
  }

  return true;
};
