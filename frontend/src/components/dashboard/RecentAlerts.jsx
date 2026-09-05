import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge, Loader, EmptyState } from '../common/UI';
import { AlertTriangle, TrendingUp, DownloadCloud, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';

export const RecentAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true);
        const res = await api.getAlerts();
        setAlerts(res.alerts || []);
      } catch (err) {
        console.error('Failed to fetch alerts:', err);
        setError('Unable to load alerts');
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  const getIcon = (level) => {
    if (level === 'CRITICAL') return <AlertTriangle size={18} color="var(--risk-critical)" />;
    if (level === 'HIGH') return <TrendingUp size={18} color="var(--risk-high)" />;
    return <DownloadCloud size={18} color="var(--risk-medium)" />;
  };

  const handleAlertClick = (accountId) => {
    navigate(`/accounts?id=${accountId}`);
  };

  if (loading) return <div className="card" style={{ height: '100%' }}><Loader message="Loading alerts..." /></div>;
  
  if (error) return (
    <div className="card" style={{ height: '100%' }}>
      <h3 style={{ margin: '0 0 20px 0', fontSize: '16px' }}>Recent Alerts</h3>
      <EmptyState title="Error" description={error} icon={AlertCircle} />
    </div>
  );

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, fontSize: '16px' }}>Recent Alerts</h3>
        <button onClick={() => navigate('/alerts')} style={{ background: 'none', border: 'none', color: 'var(--accent-yellow)', cursor: 'pointer', fontWeight: 600 }}>View All</button>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto', maxHeight: '300px' }}>
        {alerts.length === 0 ? <EmptyState title="No alerts" description="No suspicious activity detected." /> : alerts.slice(0, 5).map(alert => (
          <div 
            key={alert.id} 
            onClick={() => handleAlertClick(alert.account_id)}
            style={{ display: 'flex', gap: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer' }}
          >
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              {getIcon(alert.risk_level)}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <Badge variant={alert.risk_level.toLowerCase()}>{alert.risk_level}</Badge>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{alert.timestamp}</span>
              </div>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: 600 }}>{alert.title}</h4>
              <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.4' }}>{alert.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
