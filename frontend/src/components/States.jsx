export function Skeleton({ height = 20, width = '100%', radius = 'var(--radius-sm)' }) {
  return (
    <div
      style={{
        height, width, borderRadius: radius,
        background: 'linear-gradient(90deg, var(--color-surface-alt) 25%, var(--color-border) 37%, var(--color-surface-alt) 63%)',
        backgroundSize: '400% 100%',
        animation: 'bb-shimmer 1.4s ease infinite',
      }}
    />
  );
}

export function EmptyState({ icon = '🌱', title, subtitle, action }) {
  return (
    <div style={{ textAlign: 'center', padding: 'var(--space-8) var(--space-4)' }}>
      <div style={{ fontSize: 48, marginBottom: 'var(--space-3)' }}>{icon}</div>
      <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>{title}</div>
      {subtitle && (
        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-4)' }}>
          {subtitle}
        </div>
      )}
      {action}
    </div>
  );
}

export function ErrorState({ message = 'Something went wrong.', onRetry }) {
  return (
    <div style={{ textAlign: 'center', padding: 'var(--space-6) var(--space-4)' }}>
      <div style={{ fontSize: 40, marginBottom: 'var(--space-3)' }}>⚠️</div>
      <div style={{ color: 'var(--color-danger)', fontWeight: 600, marginBottom: 'var(--space-3)' }}>{message}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            background: 'transparent', border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)', padding: '10px 18px', cursor: 'pointer',
            color: 'var(--color-primary-500)', fontWeight: 600,
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
