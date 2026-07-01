import Card from '../../components/Card';
import { Skeleton } from '../../components/States';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../theme/ThemeContext';
import { ROLES } from '../auth/roles';

const ROLE_WIDGETS = {
  farmer: ['🌦️ Weather', '🩺 Farm Health Score', '💧 Water Status', '🌱 Crop Progress'],
  admin: ['👥 Total Users', '🚩 Flagged Disease Alerts', '📊 Platform Activity'],
  agronomist: ['📋 Pending Consultations', '🔬 Disease Reports to Review'],
  equipment_vendor: ['🚜 My Listings', '📅 Upcoming Bookings'],
  labour_contractor: ['👥 Available Labour', '📅 Active Contracts'],
  buyer: ['🛒 Nearby Produce', '📦 Active Orders'],
  government_officer: ['📈 Regional Crop Stats', '🚨 Active Risk Zones'],
};

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const roleMeta = ROLES.find((r) => r.value === user?.role);
  const widgets = ROLE_WIDGETS[user?.role] || [];

  return (
    <div style={{ paddingBottom: 'var(--space-8)' }}>
      <header style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: 'var(--space-5)', borderBottom: '1px solid var(--color-border)',
      }}>
        <div>
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            {roleMeta?.icon} {roleMeta?.label}
          </div>
          <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>
            Hi, {user?.name?.split(' ')[0] || 'there'} 👋
          </div>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button onClick={toggleTheme} style={iconBtnStyle}>{theme === 'light' ? '🌙' : '☀️'}</button>
          <button onClick={logout} style={iconBtnStyle}>🚪</button>
        </div>
      </header>

      <div style={{ padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        {!user?.is_profile_complete && (
          <Card style={{ background: 'var(--color-primary-50)', border: '1px solid var(--color-primary-300)' }}>
            <strong>Complete your profile</strong>
            <p style={{ margin: '4px 0 0', color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
              Set up your {user?.role === 'farmer' ? 'farm' : 'business'} details to unlock personalized features.
            </p>
          </Card>
        )}

        {widgets.length === 0 ? (
          <>
            <Skeleton height={90} />
            <Skeleton height={90} />
          </>
        ) : (
          widgets.map((w) => (
            <Card key={w}>
              <div style={{ fontWeight: 600, marginBottom: 'var(--space-2)' }}>{w}</div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
                Coming online in the next module — this module only builds Auth + Roles.
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

const iconBtnStyle = {
  width: 40, height: 40, borderRadius: 'var(--radius-full)',
  border: '1px solid var(--color-border)', background: 'var(--color-surface)',
  fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
};
