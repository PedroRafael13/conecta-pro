// CPF Validation
export function validateCPF(cpf: string): boolean {
  const cleaned = cpf.replace(/\D/g, '');

  if (cleaned.length !== 11) return false;

  // Check for known invalid patterns
  if (/^(\d)\1{10}$/.test(cleaned)) return false;

  // Validate check digits
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleaned.charAt(i)) * (10 - i);
  }
  let remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cleaned.charAt(9))) return false;

  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleaned.charAt(i)) * (11 - i);
  }
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cleaned.charAt(10))) return false;

  return true;
}

// CNPJ Validation
export function validateCNPJ(cnpj: string): boolean {
  const cleaned = cnpj.replace(/\D/g, '');

  if (cleaned.length !== 14) return false;

  // Check for known invalid patterns
  if (/^(\d)\1{13}$/.test(cleaned)) return false;

  // Validate check digits
  const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];

  let sum = 0;
  for (let i = 0; i < 12; i++) {
    sum += parseInt(cleaned.charAt(i)) * weights1[i];
  }
  let remainder = sum % 11;
  const digit1 = remainder < 2 ? 0 : 11 - remainder;
  if (digit1 !== parseInt(cleaned.charAt(12))) return false;

  sum = 0;
  for (let i = 0; i < 13; i++) {
    sum += parseInt(cleaned.charAt(i)) * weights2[i];
  }
  remainder = sum % 11;
  const digit2 = remainder < 2 ? 0 : 11 - remainder;
  if (digit2 !== parseInt(cleaned.charAt(13))) return false;

  return true;
}

// CEP Validation
export function validateCEP(cep: string): boolean {
  const cleaned = cep.replace(/\D/g, '');
  return /^\d{8}$/.test(cleaned);
}

// Email Validation
export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

// Phone Validation (Brazilian format)
export function validatePhone(phone: string): boolean {
  const cleaned = phone.replace(/\D/g, '');
  return /^(\d{10}|\d{11})$/.test(cleaned);
}

// Password Validation
export interface PasswordValidation {
  strength: 'weak' | 'medium' | 'strong';
  score: number;
  errors: string[];
}

export function validatePassword(password: string): PasswordValidation {
  const errors: string[] = [];
  let score = 0;

  if (password.length < 8) {
    errors.push('Minimo de 8 caracteres');
  } else {
    score += 1;
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Pelo menos uma letra minuscula');
  } else {
    score += 1;
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Pelo menos uma letra maiuscula');
  } else {
    score += 1;
  }

  if (!/\d/.test(password)) {
    errors.push('Pelo menos um numero');
  } else {
    score += 1;
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Pelo menos um caractere especial');
  } else {
    score += 1;
  }

  let strength: 'weak' | 'medium' | 'strong';
  if (score <= 2) {
    strength = 'weak';
  } else if (score <= 4) {
    strength = 'medium';
  } else {
    strength = 'strong';
  }

  return { strength, score, errors };
}

// File Validation
export function validateFileSize(file: File, maxMB: number): boolean {
  const maxBytes = maxMB * 1024 * 1024;
  return file.size <= maxBytes;
}

export function validateFileType(
  file: File,
  allowedTypes: string[]
): boolean {
  const extension = file.name.split('.').pop()?.toLowerCase() || '';
  return allowedTypes.includes(extension);
}

// URL Validation
export function validateURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
