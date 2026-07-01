export default function Button({
  children, onClick, variant = 'primary', disabled = false, type = 'button', fullWidth = true,
}) {
  const styles = {
    base: {
      fontFamily: 'var(--font-family)',
      fontSize: 'var(--font-size-md)',
      fontWeight: 600,
      padding: '14px 20px',
      borderRadius: 'var(--radius-md)',
      border: 'none',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.5 : 1,
      width: fullWidth ? '100%' : 'auto',
      transition: 'transform var(--transition-fast), box-shadow var(--transition-fast)',
    },
    primary: {
      background: 'var(--color-primary-500)',
      color: '#fff',
      boxShadow: 'var(--shadow-sm)',
    },
    secondary: {
      background: 'var(--color-surface-alt)',
      color: 'var(--color-text-primary)',
      border: '1px solid var(--color-border)',
    },
    ghost: {
      background: 'transparent',
      color: 'var(--color-primary-500)',
    },
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{ ...styles.base, ...styles[variant] }}
      onMouseDown={(e) => { if (!disabled) e.currentTarget.style.transform = 'scale(0.98)'; }}
      onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
    >
      {children}
    </button>
  );
}
