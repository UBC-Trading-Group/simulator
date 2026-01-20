export const palette = {
  primaryText: '#1B212D',
  secondaryText: '#98A1B4',
  brandRed: '#892736',
  brandRedHover: '#72202d',
  marketBuy: '#10B981',
  marketBuyHover: '#059669',
  marketSell: '#EF4444',
  marketSellHover: '#DC2626',
  limitBuy: '#3B82F6',
  limitBuyHover: '#2563EB',
  border: '#E7E9F1',
  background: '#FFFFFF',
  cardShadow: '0 8px 24px rgba(0,0,0,0.04)',
};

export const widgetStyles = {
  card: {
    width: '100%',
    maxWidth: 420,
    border: 'none',
    background: palette.background,
    boxShadow: palette.cardShadow,
    padding: '20px',
    borderRadius: 12,
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

  pillButton: (type: 'buy' | 'sell', isHovered?: boolean) => ({
    flex: 1,
    padding: '12px 20px',
    fontSize: 13,
    fontWeight: 700,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: '#FFFFFF',
    background: type === 'buy'
      ? (isHovered ? palette.marketBuyHover : palette.marketBuy)
      : (isHovered ? palette.marketSellHover : palette.marketSell),
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    transform: isHovered ? 'translateY(-1px)' : 'none',
    boxShadow: isHovered ? '0 4px 12px rgba(0,0,0,0.1)' : 'none',
  } as React.CSSProperties),

  limitButton: (isHovered?: boolean) => ({
    width: '100%',
    padding: '12px 20px',
    fontSize: 13,
    fontWeight: 700,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: '#FFFFFF',
    background: isHovered ? palette.brandRedHover : palette.brandRed,
    border: 'none',
    borderRadius: 10,
    cursor: 'pointer',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    transform: isHovered ? 'translateY(-1px)' : 'none',
    boxShadow: isHovered ? '0 4px 12px rgba(137, 39, 54, 0.2)' : 'none',
  } as React.CSSProperties),

  divider: {
    height: 1,
    background: palette.border,
    margin: '24px 0',
  } as React.CSSProperties,

  toggleContainer: {
    display: 'flex',
    background: '#F3F4F6',
    borderRadius: 8,
    padding: 4,
    marginBottom: 4,
  } as React.CSSProperties,

  toggleOption: (isActive: boolean, side: 'buy' | 'sell') => ({
    flex: 1,
    padding: '8px 12px',
    fontSize: 12,
    fontWeight: 700,
    textAlign: 'center',
    cursor: 'pointer',
    borderRadius: 6,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    background: isActive
      ? (side === 'buy' ? palette.marketBuy : palette.marketSell)
      : 'transparent',
    color: isActive ? '#FFFFFF' : palette.secondaryText,
    boxShadow: isActive ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  } as React.CSSProperties),
};

export const focusStyles: React.CSSProperties = {
  borderColor: '#3B82F6',
  background: '#FFFFFF',
};
