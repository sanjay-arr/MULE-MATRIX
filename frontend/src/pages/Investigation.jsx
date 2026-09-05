import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '../components/layout/Layout';
import { Badge, Loader, EmptyState } from '../components/common/UI';
import { api } from '../services/api';
import { 
  FileSearch, AlertCircle, Target, ArrowRight, 
  CheckCircle, Brain, Network, BarChart2, 
  Activity, Shield, AlertTriangle
} from 'lucide-react';

const RulePill = ({ rule }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: '4px',
    padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: 600,
    background: 'rgba(239, 68, 68, 0.08)', color: 'var(--risk-critical)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
  }}>
    <CheckCircle size={11} />
    {rule.replace(/_/g, ' ')}
  </span>
);

const SectionHeader = ({ icon: Icon, title, color = 'var(--text-muted)' }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
    <Icon size={16} color={color} />
    <h4 style={{ margin: 0, fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color }}>{title}</h4>
  </div>
);

const StatRow = ({ label, value, valueStyle }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
    <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{label}</span>
    <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', ...valueStyle }}>{value}</span>
  </div>
);

export const Investigation = () => {
  const [searchParams] = useSearchParams();
  const investigationIdParam = searchParams.get('id');
  const accountIdParam = searchParams.get('account_id');
  const networkIdParam = searchParams.get('network_id');
  
  const [investigation, setInvestigation] = useState(null);
  const [moneyTrail, setMoneyTrail] = useState(null);
  const [mlPrediction, setMlPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchInvestigation = async () => {
      try {
        setLoading(true);
        let data;
        
        if (investigationIdParam) {
          data = await api.getInvestigationDetails(investigationIdParam);
        } else if (accountIdParam) {
          data = await api.createInvestigation({ account_id: accountIdParam });
          navigate(`/investigations?id=${data.investigation_id}`, { replace: true });
        } else if (networkIdParam) {
          data = await api.createInvestigation({ network_id: networkIdParam });
          navigate(`/investigations?id=${data.investigation_id}`, { replace: true });
        } else {
          setLoading(false);
          return;
        }

        setInvestigation(data);
        setLoading(false);

        // Load money trail async
        const trailSource = (!data.money_trail || data.money_trail.length === 0) && data.network_id
          ? api.getNetworkMoneyTrail(data.network_id).then(r => r.trail || [])
          : Promise.resolve(data.money_trail || []);
        trailSource.then(setMoneyTrail).catch(() => setMoneyTrail([]));

        // Load ML prediction async
        if (data.account_id) {
          api.getMLPrediction(data.account_id)
            .then(setMlPrediction)
            .catch(() => setMlPrediction(null));
        }
      } catch (err) {
        console.error('Failed to load investigation:', err);
        setError('Failed to load investigation details.');
        setLoading(false);
      }
    };
    fetchInvestigation();
  }, [investigationIdParam, accountIdParam, networkIdParam, navigate]);

  if (loading) return <PageContainer title="Investigation Report"><Loader message="Compiling investigation report..." /></PageContainer>;
  if (error) return <PageContainer title="Investigation Report"><EmptyState title="Error" description={error} icon={AlertCircle} /></PageContainer>;
  
  if (!investigation) {
    return (
      <PageContainer title="Investigations">
        <EmptyState 
          title="No Active Investigation" 
          description="Start an investigation from the Account Explorer or Network Explorer." 
          icon={FileSearch} 
        />
      </PageContainer>
    );
  }

  const riskColor = investigation.risk_level === 'CRITICAL' ? 'var(--risk-critical)' 
    : investigation.risk_level === 'HIGH' ? 'var(--risk-high)'
    : investigation.risk_level === 'SUSPICIOUS' ? 'var(--risk-medium)'
    : 'var(--risk-low)';

  return (
    <PageContainer title={`Investigation: ${investigation.investigation_id}`}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>

        {/* ===== LEFT COLUMN: Summary ===== */}
        <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Case Header Card */}
          <div className="card" style={{ borderTop: `3px solid ${riskColor}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Shield size={18} color={riskColor} />
              <h3 style={{ margin: 0, fontSize: '15px' }}>Investigation Summary</h3>
            </div>
            
            <div style={{ marginBottom: '12px', padding: '12px', background: '#f8fafc', borderRadius: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Target Subject</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a', fontFamily: 'monospace', marginBottom: '6px' }}>
                {investigation.account_id}
              </div>
              <Badge variant={investigation.risk_level.toLowerCase()}>{investigation.risk_level}</Badge>
            </div>
            
            <StatRow label="Investigation ID" value={investigation.investigation_id} valueStyle={{ fontSize: '12px', fontFamily: 'monospace' }} />
            <StatRow 
              label="Risk Score" 
              value={`${Math.round(investigation.risk_score)} / 100`}
              valueStyle={{ color: riskColor, fontSize: '15px' }}
            />
            <StatRow label="Banks Involved" value={investigation.banks_involved?.length || 0} />
            <StatRow label="Connected Accounts" value={investigation.connected_accounts?.length || 0} />
            <StatRow 
              label="Off-Ramp" 
              value={investigation.off_ramp_account || 'None detected'} 
              valueStyle={{ fontSize: '11px', fontFamily: 'monospace', color: investigation.off_ramp_account ? 'var(--risk-critical)' : 'var(--text-muted)' }}
            />

            {/* Network Link */}
            {investigation.network_id && (
              <button
                onClick={() => navigate(`/networks?id=${investigation.network_id}`)}
                style={{ marginTop: '14px', width: '100%', padding: '10px', background: '#0f172a', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '13px', fontWeight: 600 }}
              >
                <Network size={14} /> View Network Graph <ArrowRight size={13} />
              </button>
            )}
          </div>

          {/* Intelligence Layers Card */}
          <div className="card">
            <h3 style={{ margin: '0 0 16px 0', fontSize: '15px' }}>Intelligence Layers</h3>

            {/* Rule Engine */}
            <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(239, 68, 68, 0.04)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.12)' }}>
              <SectionHeader icon={AlertTriangle} title="Rule Engine" color="var(--risk-critical)" />
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                {(investigation.evidence || []).length} behavioral rule(s) triggered
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(investigation.triggered_rules || []).map(rule => <RulePill key={rule} rule={rule} />)}
              </div>
            </div>

            {/* ML Layer */}
            <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(59, 130, 246, 0.04)', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.12)' }}>
              <SectionHeader icon={Brain} title="Random Forest ML" color="var(--accent-blue, #3b82f6)" />
              {mlPrediction ? (
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: mlPrediction.ml_prediction === 'MULE' ? 'var(--risk-critical)' : 'var(--risk-low)' }}>
                      {mlPrediction.ml_prediction}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Prediction</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '20px', fontWeight: 700 }}>
                      {(mlPrediction.mule_probability * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mule Probability</div>
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>Loading ML signal...</div>
              )}
            </div>

            {/* Graph Intelligence */}
            <div style={{ padding: '12px', background: 'rgba(34, 197, 94, 0.04)', borderRadius: '8px', border: '1px solid rgba(34, 197, 94, 0.12)' }}>
              <SectionHeader icon={Network} title="Graph Intelligence" color="var(--risk-low)" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Connected accounts</span>
                  <span style={{ fontWeight: 600 }}>{investigation.connected_accounts?.length || 0}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Banks in network</span>
                  <span style={{ fontWeight: 600 }}>{investigation.banks_involved?.length || 0}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Off-ramp connection</span>
                  <span style={{ fontWeight: 600, color: investigation.off_ramp_account ? 'var(--risk-critical)' : 'var(--text-muted)' }}>
                    {investigation.off_ramp_account ? 'Yes' : 'None'}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>GNN Signal</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)', fontStyle: 'italic' }}>Unavailable</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ===== RIGHT COLUMN: Evidence + Money Trail ===== */}
        <div style={{ gridColumn: 'span 8', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Key Evidence */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={16} color="var(--risk-high)" />
                <h3 style={{ margin: 0, fontSize: '15px' }}>Key Evidence</h3>
              </div>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{(investigation.evidence || []).length} findings</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(investigation.evidence || []).length > 0 ? (
                (investigation.evidence || []).map((ev, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '10px 12px', background: '#f8fafc', borderRadius: '6px', borderLeft: '3px solid var(--risk-critical)' }}>
                    <CheckCircle size={14} color="var(--risk-critical)" style={{ flexShrink: 0, marginTop: '1px' }} />
                    <span style={{ fontSize: '13px', lineHeight: '1.5' }}>{ev}</span>
                  </div>
                ))
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '13px', fontStyle: 'italic' }}>No specific evidence logged.</div>
              )}
            </div>
          </div>

          {/* Money Trail */}
          <div className="card" style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={16} color="var(--risk-critical)" />
                <div>
                  <h3 style={{ margin: '0 0 2px 0', fontSize: '15px' }}>Money Trail</h3>
                  <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>Reconstructed suspicious fund flow sequence</p>
                </div>
              </div>
              <BarChart2 size={18} color="var(--text-muted)" />
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
              {moneyTrail === null ? (
                <div style={{ padding: '24px', background: '#f8fafc', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', border: '1px dashed var(--border-subtle)' }}>
                  Loading money trail...
                </div>
              ) : moneyTrail.length === 0 ? (
                <div style={{ padding: '24px', background: '#f8fafc', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', border: '1px dashed var(--border-subtle)' }}>
                  No money trail available for this investigation.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
                  {moneyTrail.map((step, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '16px', position: 'relative' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '32px', flexShrink: 0 }}>
                        <div style={{
                          width: '32px', height: '32px', borderRadius: '50%',
                          background: idx === moneyTrail.length - 1 ? 'var(--risk-critical)' : '#0f172a',
                          color: 'white',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '12px', fontWeight: 700, zIndex: 1, flexShrink: 0,
                        }}>
                          {idx === moneyTrail.length - 1 ? '⚑' : idx + 1}
                        </div>
                        {idx < moneyTrail.length - 1 && (
                          <div style={{ width: '2px', flex: 1, background: 'var(--border-subtle)', margin: '4px 0', minHeight: '16px' }} />
                        )}
                      </div>
                      <div style={{
                        flex: 1,
                        background: idx === moneyTrail.length - 1 ? 'rgba(239,68,68,0.04)' : '#f8fafc',
                        padding: '12px 16px',
                        borderRadius: '8px',
                        border: `1px solid ${idx === moneyTrail.length - 1 ? 'rgba(239,68,68,0.2)' : 'var(--border-subtle)'}`,
                        marginBottom: idx < moneyTrail.length - 1 ? '8px' : '0',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <span style={{ fontSize: '14px', fontWeight: 700, fontFamily: 'monospace' }}>{step.account_id}</span>
                          <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--risk-critical)' }}>
                            ₹{(step.amount || 0).toLocaleString()}
                          </span>
                        </div>
                        <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--text-muted)' }}>
                          <span>Bank: <strong>{step.bank_id}</strong></span>
                          {idx === moneyTrail.length - 1 && <span style={{ color: 'var(--risk-critical)', fontWeight: 600 }}>⚑ OFF-RAMP</span>}
                        </div>
                        {step.transaction_id && (
                          <div style={{ fontSize: '10px', color: '#cbd5e1', marginTop: '4px', fontFamily: 'monospace' }}>TXN: {step.transaction_id}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </PageContainer>
  );
};
