import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '../components/layout/Layout';
import { Badge, Loader, EmptyState } from '../components/common/UI';
import { AlertTriangle, TrendingUp, DownloadCloud, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export const Alerts = () => {
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
    if (level === 'CRITICAL') return <AlertTriangle size={20} color="var(--risk-critical)" />;
    if (level === 'HIGH') return <TrendingUp size={20} color="var(--risk-high)" />;
    return <DownloadCloud size={20} color="var(--risk-medium)" />;
  };

  const handleAlertClick = (accountId) => {
    navigate(`/accounts?id=${accountId}`);
  };

  const handleNetworkClick = (e, networkId) => {
    e.stopPropagation();
    navigate(`/networks?id=${networkId}`);
  };

  if (loading) return <PageContainer title="System Alerts"><Loader message="Loading alerts..." /></PageContainer>;
  if (error) return <PageContainer title="System Alerts"><EmptyState title="Error" description={error} icon={AlertCircle} /></PageContainer>;

  return (
    <PageContainer title="System Alerts">
      <div className="card">
        <h3 style={{ margin: '0 0 20px 0', fontSize: '16px' }}>All Suspicious Activity Alerts</h3>
        
        {alerts.length === 0 ? (
          <EmptyState title="No Alerts" description="No suspicious activity detected in the system." />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {alerts.map(alert => (
              <div 
                key={alert.id} 
                onClick={() => handleAlertClick(alert.account_id)}
                style={{ display: 'flex', gap: '20px', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-subtle)', cursor: 'pointer', transition: 'background-color 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {getIcon(alert.risk_level)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{alert.title}</h4>
                      <Badge variant={alert.risk_level.toLowerCase()}>{alert.risk_level}</Badge>
                    </div>
                    <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{alert.timestamp}</span>
                  </div>
                  <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: 'var(--text-main)', lineHeight: '1.5' }}>{alert.description}</p>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <span>Account: <strong style={{ color: 'var(--text-main)' }}>{alert.account_id}</strong></span>
                    <span>Alert ID: {alert.id}</span>
                    {alert.network_id && (
                      <button 
                        onClick={(e) => handleNetworkClick(e, alert.network_id)}
                        style={{ padding: '4px 8px', fontSize: '12px', backgroundColor: 'var(--bg-dark)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                      >
                        View Network {alert.network_id}
                      </button>
                    )}
                  </div>
                  {alert.triggered_rules && alert.triggered_rules.length > 0 && (
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '12px' }}>
                      {alert.triggered_rules.slice(0, 3).map(rule => (
                        <Badge key={rule} variant="high">{rule.replace(/_/g, ' ')}</Badge>
                      ))}
                      {alert.triggered_rules.length > 3 && (
                        <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
                          +{alert.triggered_rules.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  );
};
