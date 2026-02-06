/**
 * Funções utilitárias para manipulação de datas
 */

/**
 * Converte uma string de data para objeto Date
 * Aceita formato ISO (YYYY-MM-DD) ou brasileiro (DD/MM/YYYY)
 */
export const parseDate = (dateString: string): Date | null => {
  if (!dateString) return null;

  // Formato ISO: YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    const parts = dateString.split('-').map(Number);
    const year = parts[0]!;
    const month = parts[1]!;
    const day = parts[2]!;
    const date = new Date(year, month - 1, day);

    // Valida se a data é válida
    if (
      date.getFullYear() === year &&
      date.getMonth() === month - 1 &&
      date.getDate() === day
    ) {
      return date;
    }
    return null;
  }

  // Formato brasileiro: DD/MM/YYYY
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateString)) {
    const brParts = dateString.split('/').map(Number);
    const day = brParts[0]!;
    const month = brParts[1]!;
    const year = brParts[2]!;
    const date = new Date(year, month - 1, day);

    // Valida se a data é válida
    if (
      date.getFullYear() === year &&
      date.getMonth() === month - 1 &&
      date.getDate() === day
    ) {
      return date;
    }
    return null;
  }

  // Tenta parsing padrão (ISO completo)
  const parsed = new Date(dateString);
  if (!isNaN(parsed.getTime())) {
    return parsed;
  }

  return null;
};

/**
 * Formata uma data para o padrão brasileiro (DD/MM/YYYY)
 */
export const formatDateBR = (date: Date | string): string => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj || isNaN(dateObj.getTime())) {
    return '';
  }

  const day = String(dateObj.getDate()).padStart(2, '0');
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const year = dateObj.getFullYear();

  return `${day}/${month}/${year}`;
};

/**
 * Formata uma data para o padrão ISO (YYYY-MM-DD)
 */
export const formatDateISO = (date: Date | string): string => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj || isNaN(dateObj.getTime())) {
    return '';
  }

  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
};

/**
 * Adiciona dias a uma data
 */
export const addDays = (date: Date | string, days: number): Date => {
  const dateObj = date instanceof Date ? new Date(date) : parseDate(date);

  if (!dateObj) {
    throw new Error('Data inválida');
  }

  const result = new Date(dateObj);
  result.setDate(result.getDate() + days);
  return result;
};

/**
 * Subtrai dias de uma data
 */
export const subDays = (date: Date | string, days: number): Date => {
  return addDays(date, -days);
};

/**
 * Adiciona meses a uma data
 */
export const addMonths = (date: Date | string, months: number): Date => {
  const dateObj = date instanceof Date ? new Date(date) : parseDate(date);

  if (!dateObj) {
    throw new Error('Data inválida');
  }

  const result = new Date(dateObj);
  result.setMonth(result.getMonth() + months);
  return result;
};

/**
 * Subtrai meses de uma data
 */
export const subMonths = (date: Date | string, months: number): Date => {
  return addMonths(date, -months);
};

/**
 * Verifica se uma data é fim de semana
 */
export const isWeekend = (date: Date | string): boolean => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    return false;
  }

  const dayOfWeek = dateObj.getDay();
  return dayOfWeek === 0 || dayOfWeek === 6; // Domingo (0) ou Sábado (6)
};

/**
 * Lista de feriados nacionais brasileiros fixos (formato MM-DD)
 * Ano novo, Tiradentes, Dia do Trabalho, Independência, Nossa Senhora Aparecida, Finados, Proclamação da República, Natal
 */
const FIXED_HOLIDAYS = [
  '01-01', // Ano Novo
  '04-21', // Tiradentes
  '05-01', // Dia do Trabalho
  '09-07', // Independência
  '10-12', // Nossa Senhora Aparecida
  '11-02', // Finados
  '11-15', // Proclamação da República
  '12-25', // Natal
];

/**
 * Verifica se uma data é feriado nacional brasileiro
 * Considera apenas feriados fixos (não calcula Carnaval, Páscoa, etc.)
 */
export const isHoliday = (date: Date | string): boolean => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    return false;
  }

  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  const dateKey = `${month}-${day}`;

  return FIXED_HOLIDAYS.includes(dateKey);
};

/**
 * Calcula a diferença em dias entre duas datas
 */
export const diffInDays = (
  startDate: Date | string,
  endDate: Date | string
): number => {
  const start = startDate instanceof Date ? startDate : parseDate(startDate);
  const end = endDate instanceof Date ? endDate : parseDate(endDate);

  if (!start || !end) {
    return 0;
  }

  const startUTC = Date.UTC(start.getFullYear(), start.getMonth(), start.getDate());
  const endUTC = Date.UTC(end.getFullYear(), end.getMonth(), end.getDate());

  const diffTime = endUTC - startUTC;
  return Math.round(diffTime / (1000 * 60 * 60 * 24));
};

/**
 * Retorna o primeiro dia do mês
 */
export const startOfMonth = (date: Date | string): Date => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    throw new Error('Data inválida');
  }

  return new Date(dateObj.getFullYear(), dateObj.getMonth(), 1);
};

/**
 * Retorna o último dia do mês
 */
export const endOfMonth = (date: Date | string): Date => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    throw new Error('Data inválida');
  }

  return new Date(dateObj.getFullYear(), dateObj.getMonth() + 1, 0);
};

/**
 * Verifica se duas datas são o mesmo dia
 */
export const isSameDay = (
  date1: Date | string,
  date2: Date | string
): boolean => {
  const d1 = date1 instanceof Date ? date1 : parseDate(date1);
  const d2 = date2 instanceof Date ? date2 : parseDate(date2);

  if (!d1 || !d2) {
    return false;
  }

  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
};

/**
 * Retorna o nome do dia da semana em português
 */
export const getDayOfWeekName = (
  date: Date | string,
  short: boolean = false
): string => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    return '';
  }

  const days = short
    ? ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    : [
        'Domingo',
        'Segunda-feira',
        'Terça-feira',
        'Quarta-feira',
        'Quinta-feira',
        'Sexta-feira',
        'Sábado',
      ];

  return days[dateObj.getDay()] ?? '';
};

/**
 * Retorna o nome do mês em português
 */
export const getMonthName = (
  date: Date | string,
  short: boolean = false
): string => {
  const dateObj = date instanceof Date ? date : parseDate(date);

  if (!dateObj) {
    return '';
  }

  const months = short
    ? ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    : [
        'Janeiro',
        'Fevereiro',
        'Março',
        'Abril',
        'Maio',
        'Junho',
        'Julho',
        'Agosto',
        'Setembro',
        'Outubro',
        'Novembro',
        'Dezembro',
      ];

  return months[dateObj.getMonth()] ?? '';
};
