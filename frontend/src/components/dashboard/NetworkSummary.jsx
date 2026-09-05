import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, ArrowRight } from 'lucide-react';

export const NetworkSummary = ({ overview }) => {
  const navigate = useNavigate();

  if (!overview) return null;

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, fontSize: '16px' }}>Mule Network Summary</h3>
        <Network size={20} color="var(--accent-yellow)" />
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Detected Mule Networks</span>
          <span style={{ fontSize: '16px', fontWeight: 600 }}>{overview.mule_networks}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Cross-Bank Transactions</span>
          <span style={{ fontSize: '16px', fontWeight: 600 }}>{overview.cross_bank_transactions?.toLocaleString()}</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Off-Ramp Accounts</span>
          <span style={{ fontSize: '16px', fontWeight: 600 }}>{overview.off_ramp_accounts}</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Banks Involved</span>
          <span style={{ fontSize: '16px', fontWeight: 600 }}>{overview.banks_involved}</span>
        </div>
      </div>

      <button 
        onClick={() => navigate('/networks')}
        style={{ 
          marginTop: '20px', 
          width: '100%', 
          padding: '12px', 
          backgroundColor: 'var(--bg-dark)', 
          color: 'var(--text-light)', 
          border: 'none', 
          borderRadius: 'var(--radius-sm)', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          gap: '8px',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        Explore Networks <ArrowRight size={16} />
      </button>
    </div>
  );
};
