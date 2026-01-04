export const palette = {
  primaryText: '#1B212D',
  secondaryText: '#98A1B4',
  marketBuy: '#10B981',
  marketSell: '#EF4444',
  limitBuy: '#3B82F6',
  border: '#E7E9F1',
  background: '#FFFFFF',
  cardShadow: '0 25px 45px rgba(30, 33, 50, 0.08)',
};

export const widgetStyles = {
  card: {
    width: '100%',
    maxWidth: 420,
    border: `1px solid ${palette.border}`,
    background: palette.background,
    boxShadow: palette.cardShadow,
    padding: '28px 28px 32px',
    borderRadius: 18,
  } as React.CSSProperties,

  headerRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 16,
    marginBottom: 24,
  } as React.CSSProperties,

  title: {
    margin: 0,
    fontSize: 20,
    fontWeight: 700,
    color: palette.primaryText,
  } as React.CSSProperties,

  statusPill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    borderRadius: 999,
    padding: '8px 14px',
    background: '#F4F6FB',
    color: '#2E354A',
    fontSize: 13,
    fontWeight: 600,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  } as React.CSSProperties,

  alert: (isError: boolean) => ({
    padding: '12px 16px',
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 500,
    marginBottom: 16,
    background: isError ? '#FEE2E2' : '#D1FAE5',
    color: isError ? '#991B1B' : '#065F46',
    border: `1px solid ${isError ? '#FCA5A5' : '#86EFAC'}`,
  } as React.CSSProperties),

  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  } as React.CSSProperties,

  sectionTitle: {
    margin: 0,
    fontSize: 16,
    fontWeight: 700,
    color: palette.primaryText,
  } as React.CSSProperties,

  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  } as React.CSSProperties,

  label: {
    fontSize: 14,
    fontWeight: 600,
    color: palette.primaryText,
  } as React.CSSProperties,

  input: {
    width: '100%',
    padding: '12px 16px',
    fontSize: 15,
    fontWeight: 500,
    color: palette.primaryText,
    background: '#F9FAFB',
    border: '2px solid #E5E7EB',
    borderRadius: 10,
    outline: 'none',
    transition: 'all 0.2s ease',
  } as React.CSSProperties,

  selectWrapper: {
    position: 'relative',
  } as React.CSSProperties,

  selectCaret: {
    position: 'absolute',
    right: 16,
    top: '50%',
    transform: 'translateY(-50%)',
    pointerEvents: 'none',
    fontSize: 14,
    color: palette.secondaryText,
  } as React.CSSProperties,

  priceActions: {
    display: 'flex',
    gap: 12,
  } as React.CSSProperties,

  pillButton: (type: 'buy' | 'sell') => ({
    flex: 1,
    padding: '14px 20px',
    fontSize: 14,
    fontWeight: 700,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: '#FFFFFF',
    background: type === 'buy' ? palette.marketBuy : palette.marketSell,
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  } as React.CSSProperties),

  limitButton: {
    width: '100%',
    padding: '14px 20px',
    fontSize: 14,
    fontWeight: 700,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: '#FFFFFF',
    background: palette.limitBuy,
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  } as React.CSSProperties,

  divider: {
    height: 1,
    background: palette.border,
    margin: '24px 0',
  } as React.CSSProperties,
};

export const focusStyles: React.CSSProperties = {
  borderColor: '#3B82F6',
  background: '#FFFFFF',
};

