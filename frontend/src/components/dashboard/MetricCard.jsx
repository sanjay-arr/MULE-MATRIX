import React from 'react';

export const MetricCard = ({ title, value, icon: Icon, color = 'var(--accent-yellow)', format = true }) => {
  // Guard against undefined/null values
  const safeValue = value ?? 0;
  const formattedValue = format && typeof safeValue === 'number' && safeValue > 1000
    ? safeValue.toLocaleString()
    : safeValue;

  // Add Rupee formatting for the total transaction value
  const isCurrency = title?.toLowerCase().includes('value');
  const displayValue = isCurrency ? `₹${Number(safeValue).toLocaleString()}` : formattedValue;

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h4 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          {title}
        </h4>
        {Icon && <Icon size={20} color={color} />}
      </div>
      <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text-main)' }}>
        {displayValue}
      </div>
    </div>
  );
};
