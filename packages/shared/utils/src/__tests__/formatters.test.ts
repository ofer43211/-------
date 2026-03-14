import { formatDate, formatCurrency } from '../formatters';

describe('formatDate', () => {
  it('formats a date as YYYY-MM-DD', () => {
    const date = new Date('2025-06-15T12:00:00Z');
    expect(formatDate(date)).toBe('2025-06-15');
  });
});

describe('formatCurrency', () => {
  it('formats USD by default', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
  });

  it('formats other currencies', () => {
    const result = formatCurrency(1000, 'EUR');
    expect(result).toContain('1,000');
  });
});
