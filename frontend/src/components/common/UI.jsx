import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loader = ({ message = 'Loading...' }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px', color: 'var(--text-muted)' }}>
      <Loader2 size={32} className="animate-pulse" style={{ animation: 'spin 1s linear infinite', marginBottom: '16px', color: 'var(--accent-yellow)' }} />
      <p style={{ margin: 0, fontWeight: 500 }}>{message}</p>
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export const EmptyState = ({ title = 'No Data Available', description = 'There is currently no data to display here.', icon: Icon }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
      {Icon && <Icon size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />}
      <h3 style={{ margin: '0 0 8px 0', color: 'var(--text-main)' }}>{title}</h3>
      <p style={{ margin: 0, maxWidth: '400px' }}>{description}</p>
    </div>
  );
};

export const Badge = ({ variant = 'neutral', children }) => {
  return (
    <span className={`badge badge-${variant}`}>
      {children}
    </span>
  );
};
