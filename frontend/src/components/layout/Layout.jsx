import React from 'react';
import { Bell, Database } from 'lucide-react';
import { Badge } from '../common/UI';

export const Header = () => {
  return (
    <header className="header">
      <div>
        <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Financial Crime Intelligence Platform</h1>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', backgroundColor: '#f1f5f9', borderRadius: '100px', fontSize: '13px', fontWeight: 500, color: '#475569' }}>
          <Database size={16} color="var(--risk-high)" />
          SYNTHETIC DATA ENVIRONMENT
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="status-dot"></div>
          <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)' }}>System Online</span>
        </div>
        <div style={{ position: 'relative', cursor: 'pointer', color: 'var(--text-muted)' }}>
          <Bell size={20} />
          <span style={{ position: 'absolute', top: -4, right: -4, width: 8, height: 8, backgroundColor: 'var(--risk-critical)', borderRadius: '50%' }}></span>
        </div>
      </div>
    </header>
  );
};

export const PageContainer = ({ title, children }) => {
  return (
    <div className="page-container">
      {title && (
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: 0, fontSize: '24px' }}>{title}</h2>
        </div>
      )}
      {children}
    </div>
  );
};
