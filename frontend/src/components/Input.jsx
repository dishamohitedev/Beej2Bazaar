export default function Input({ label, value, onChange, placeholder, type = 'text', maxLength, autoFocus }) {
  return (
    <div style={{ marginBottom: 'var(--space-4)' }}>
      {label && (
        <label style={{
          display: 'block', fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text-secondary)', marginBottom: 'var(--space-2)', fontWeight: 500,
        }}>
          {label}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        maxLength={maxLength}
        autoFocus={autoFocus}
        style={{
          width: '100%',
          padding: '14px 16px',
          fontSize: 'var(--font-size-md)',
          fontFamily: 'var(--font-family)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
          background: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          outline: 'none',
          transition: 'border-color var(--transition-fast)',
        }}
        onFocus={(e) => (e.target.style.borderColor = 'var(--color-primary-500)')}
        onBlur={(e) => (e.target.style.borderColor = 'var(--color-border)')}
      />
    </div>
  );
}
