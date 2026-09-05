import React, { useState, useEffect } from 'react';
import { PageContainer } from '../components/layout/Layout';
import { MetricCard } from '../components/dashboard/MetricCard';
import { RiskOverview } from '../components/dashboard/RiskOverview';
import { RecentAlerts } from '../components/dashboard/RecentAlerts';
import { NetworkSummary } from '../components/dashboard/NetworkSummary';
import { Loader, EmptyState } from '../components/common/UI';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { 
  Users, FileText, AlertOctagon, AlertTriangle, AlertCircle, 
  Building2, DollarSign, Play, ArrowRight, Shield, Zap, Target
} from 'lucide-react';

export const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [overviewRes, riskRes] = await Promise.all([
          api.getAnalyticsOverview(),
          api.getRiskDistribution()
        ]);
        setOverview(overviewRes);
        setRiskData(riskRes);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Backend connection unavailable');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleRunDemo = async () => {
    setDemoLoading(true);
    try {
      const scenario = await api.getDemoScenario();
      const accountId = scenario.scenario.account_id;
      navigate(`/accounts?id=${accountId}&demo=true`);
    } catch (err) {
      console.error('Demo failed:', err);
      // Fallback to hardcoded demo account
      navigate(`/accounts?id=CUS_7E3E2ACD&demo=true`);
    } finally {
      setDemoLoading(false);
    }
  };

  if (loading) {
    return <PageContainer><Loader message="Loading dashboard data..." /></PageContainer>;
  }

  if (error) {
    return (
      <PageContainer>
        <EmptyState title="Connection Error" description={error} icon={AlertCircle} />
      </PageContainer>
    );
  }

  if (!overview) {
    return <PageContainer><EmptyState /></PageContainer>;
  }

  return (
    <PageContainer title="Intelligence Dashboard">
      
      {/* === RUN DEMO INVESTIGATION BANNER === */}
      <div style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%)',
        border: '1px solid #facc15',
        borderRadius: '12px',
        padding: '24px 32px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Glow effect */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at 20% 50%, rgba(250, 204, 21, 0.08) 0%, transparent 60%)',
          pointerEvents: 'none',
        }} />
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', position: 'relative' }}>
          <div style={{
            width: '52px', height: '52px', borderRadius: '12px',
            background: 'rgba(250, 204, 21, 0.15)', border: '1px solid rgba(250, 204, 21, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <Shield size={26} color="#facc15" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
              <h3 style={{ margin: 0, fontSize: '18px', color: '#f8fafc', fontWeight: 700 }}>
                Operation Cross-Bank Mule Network
              </h3>
              <span style={{ 
                fontSize: '11px', fontWeight: 700, color: '#ef4444', 
                background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)',
                padding: '2px 8px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.5px'
              }}>CRITICAL</span>
            </div>
            <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
              Coordinated mule network detected · 5 banks · 7 behavioral rules triggered · Off-ramp identified
            </p>
          </div>
        </div>
        
        <button
          id="run-demo-btn"
          onClick={handleRunDemo}
          disabled={demoLoading}
          style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '14px 28px', borderRadius: '8px', border: 'none', cursor: 'pointer',
            background: demoLoading ? '#374151' : 'linear-gradient(135deg, #facc15 0%, #f59e0b 100%)',
            color: demoLoading ? '#9ca3af' : '#0f172a',
            fontSize: '15px', fontWeight: 700, transition: 'all 0.2s',
            boxShadow: demoLoading ? 'none' : '0 4px 20px rgba(250, 204, 21, 0.4)',
            whiteSpace: 'nowrap', flexShrink: 0, position: 'relative',
          }}
        >
          {demoLoading ? (
            <><Zap size={18} />Launching...</>
          ) : (
            <><Play size={18} />Run Demo Investigation</>
          )}
        </button>
      </div>

      {/* === METRIC CARDS === */}
      <div className="metrics-grid">
        <MetricCard title="Total Accounts" value={overview.total_accounts} icon={Users} color="#94a3b8" />
        <MetricCard title="Total Transactions" value={overview.total_transactions} icon={FileText} color="#94a3b8" />
        <MetricCard title="Suspicious Accounts" value={overview.suspicious_accounts} icon={AlertOctagon} color="var(--risk-medium)" />
        <MetricCard title="High-Risk Accounts" value={overview.high_risk_accounts} icon={AlertTriangle} color="var(--risk-high)" />
        <MetricCard title="Critical Accounts" value={overview.critical_accounts} icon={AlertCircle} color="var(--risk-critical)" />
        <MetricCard title="Transaction Value" value={overview.total_transaction_value} icon={DollarSign} color="var(--risk-low)" />
      </div>

      {/* === MAIN GRID === */}
      <div className="dashboard-grid">
        <div style={{ gridColumn: 'span 4' }}>
          <RiskOverview riskData={riskData} overview={overview} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <NetworkSummary overview={overview} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <RecentAlerts />
        </div>
      </div>
    </PageContainer>
  );
};
