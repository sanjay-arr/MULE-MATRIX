import React from 'react';

export const RiskOverview = ({ riskData, overview }) => {
  if (!riskData || !overview) return null;

  const critical = riskData.CRITICAL || 0;
  const high = riskData.HIGH || 0;
  const suspicious = overview.suspicious_accounts || 0;
  const normal = overview.total_accounts - suspicious;

  const getWidth = (val) => `${Math.max((val / overview.total_accounts) * 100, 2)}%`;

  return (
    <div className="card" style={{ height: '100%' }}>
      <h3 style={{ margin: '0 0 20px 0', fontSize: '16px' }}>Risk Distribution</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
            <span>Critical</span>
            <span className="text-critical">{critical}</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: getWidth(critical), height: '100%', backgroundColor: 'var(--risk-critical)' }}></div>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
            <span>High</span>
            <span className="text-high">{high}</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: getWidth(high), height: '100%', backgroundColor: 'var(--risk-high)' }}></div>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
            <span>Suspicious (Total)</span>
            <span className="text-medium">{suspicious}</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: getWidth(suspicious), height: '100%', backgroundColor: 'var(--risk-medium)' }}></div>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
            <span>Normal</span>
            <span className="text-low">{normal}</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: getWidth(normal), height: '100%', backgroundColor: 'var(--risk-low)' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};
