import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'accent' | 'danger' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral' }) => {
  const styles = {
    primary: 'bg-[#2E7D32]/10 text-[#2E7D32] border-[#2E7D32]/20',
    secondary: 'bg-[#4CAF50]/10 text-[#2E7D32] border-[#4CAF50]/20',
    accent: 'bg-[#F9A826]/10 text-[#D97706] border-[#F9A826]/20',
    danger: 'bg-[#D32F2F]/10 text-[#D32F2F] border-[#D32F2F]/20',
    neutral: 'bg-slate-100 text-slate-600 border-slate-200',
  };

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${styles[variant]}`}>
      {children}
    </span>
  );
};
