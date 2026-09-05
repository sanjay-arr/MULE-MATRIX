import React, { useState, useEffect } from 'react';
import { PageContainer } from '../components/layout/Layout';
import { Badge, Loader, EmptyState } from '../components/common/UI';
import { api } from '../services/api';
import { BarChart2, AlertCircle } from 'lucide-react';
import { RiskOverview } from '../components/dashboard/RiskOverview';

export const Analytics = () => {
  const [bankRisk, setBankRisk] = useState([]);
  const [overview, setOverview] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [mlMetrics, setMlMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [bankRes, overRes, riskRes, mlRes] = await Promise.all([
          api.getBankRisk(),
          api.getAnalyticsOverview(),
          api.getRiskDistribution(),
          api.getMLMetrics().catch(() => null)
        ]);
        setBankRisk(bankRes || []);
        setOverview(overRes);
        setRiskData(riskRes);
        setMlMetrics(mlRes);
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
        setError('Unable to load advanced analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <PageContainer title="Advanced Analytics"><Loader message="Aggregating analytics..." /></PageContainer>;
  if (error) return <PageContainer title="Advanced Analytics"><EmptyState title="Error" description={error} icon={AlertCircle} /></PageContainer>;

  // Find max suspicious accounts to scale the bars
  const maxSuspicious = Math.max(...bankRisk.map(b => b.suspicious_accounts), 1);

  return (
    <PageContainer title="Advanced Analytics">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
        
        {/* Risk Distribution overview */}
        <div style={{ gridColumn: 'span 4' }}>
          <RiskOverview riskData={riskData} overview={overview} />
        </div>

        {/* Bank Risk Comparison */}
        <div className="card" style={{ gridColumn: 'span 8', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
            <div>
              <h3 style={{ margin: '0 0 4px 0', fontSize: '16px' }}>Bank Risk Comparison</h3>
              <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)' }}>Suspicious accounts by financial institution</p>
            </div>
            <BarChart2 size={20} color="var(--accent-yellow)" />
          </div>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {bankRisk.map(bank => (
              <div key={bank.bank_id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', fontWeight: 500 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span>{bank.bank_id}</span>
                    <Badge variant="neutral">{bank.total_accounts} Total</Badge>
                  </div>
                  <span className="text-high">{bank.suspicious_accounts} Suspicious</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ flex: 1, height: '12px', backgroundColor: '#f1f5f9', borderRadius: '6px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        width: `${(bank.suspicious_accounts / maxSuspicious) * 100}%`, 
                        height: '100%', 
                        backgroundColor: 'var(--risk-high)',
                        borderRadius: '6px',
                        transition: 'width 1s ease-in-out'
                      }}
                    ></div>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', width: '60px', textAlign: 'right' }}>
                    Avg Risk: {Math.round(bank.average_risk)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div style={{ gridColumn: 'span 12', display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Cross-Bank Vol</h4>
            <div style={{ fontSize: '28px', fontWeight: 700 }}>{overview?.cross_bank_transactions?.toLocaleString()}</div>
          </div>
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Off-Ramps</h4>
            <div style={{ fontSize: '28px', fontWeight: 700 }}>{overview?.off_ramp_accounts}</div>
          </div>
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Value</h4>
            <div style={{ fontSize: '28px', fontWeight: 700 }}>₹{overview?.total_transaction_value?.toLocaleString()}</div>
          </div>
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Mule Networks</h4>
            <div style={{ fontSize: '28px', fontWeight: 700 }}>{overview?.mule_networks}</div>
          </div>
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Banks Involved</h4>
            <div style={{ fontSize: '28px', fontWeight: 700 }}>{overview?.banks_involved}</div>
          </div>
        </div>

        {/* Machine Learning Engine Overview */}
        {mlMetrics && (
          <div className="card" style={{ gridColumn: 'span 12', padding: '24px' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>Machine Learning Intelligence Engine</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
              <div style={{ gridColumn: 'span 6' }}>
                <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px' }}>Model Performance (Random Forest)</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ padding: '16px', background: 'var(--bg-primary)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Precision</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, color: 'var(--accent-blue)' }}>
                      {(mlMetrics.precision * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div style={{ padding: '16px', background: 'var(--bg-primary)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Recall</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, color: 'var(--accent-blue)' }}>
                      {(mlMetrics.recall * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div style={{ padding: '16px', background: 'var(--bg-primary)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>F1 Score</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, color: 'var(--accent-blue)' }}>
                      {(mlMetrics.f1_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div style={{ padding: '16px', background: 'var(--bg-primary)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>ROC-AUC</div>
                    <div style={{ fontSize: '24px', fontWeight: 600, color: 'var(--accent-blue)' }}>
                      {mlMetrics.roc_auc ? (mlMetrics.roc_auc * 100).toFixed(1) + '%' : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ gridColumn: 'span 6' }}>
                <h4 style={{ color: 'var(--text-muted)', marginBottom: '12px' }}>Top Feature Importance</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {mlMetrics.feature_importance && Object.entries(mlMetrics.feature_importance).slice(0, 5).map(([feat, imp], i) => (
                    <div key={feat} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '13px', fontFamily: 'monospace' }}>{feat}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '60%' }}>
                        <div style={{ flex: 1, height: '8px', background: 'var(--bg-primary)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${imp * 100}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: '4px' }} />
                        </div>
                        <span style={{ fontSize: '12px', width: '45px', textAlign: 'right', color: 'var(--text-muted)' }}>
                          {(imp * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Model Comparison Section */}
            <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid var(--border-subtle)' }}>
              <h4 style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>Model Comparison</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border-subtle)' }}>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Model / Engine</th>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Status</th>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Precision</th>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Recall</th>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>F1 Score</th>
                    <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px 8px', fontWeight: 600 }}>Rule Engine (Heuristics)</td>
                    <td style={{ padding: '12px 8px' }}><Badge variant="low">Active</Badge></td>
                    <td style={{ padding: '12px 8px' }}>Baseline</td>
                    <td style={{ padding: '12px 8px' }}>Baseline</td>
                    <td style={{ padding: '12px 8px' }}>Baseline</td>
                    <td style={{ padding: '12px 8px' }}>N/A</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(59, 130, 246, 0.05)' }}>
                    <td style={{ padding: '12px 8px', fontWeight: 600 }}>Random Forest (Tabular ML)</td>
                    <td style={{ padding: '12px 8px' }}><Badge variant="high">Active</Badge></td>
                    <td style={{ padding: '12px 8px' }}>{(mlMetrics.precision * 100).toFixed(1)}%</td>
                    <td style={{ padding: '12px 8px' }}>{(mlMetrics.recall * 100).toFixed(1)}%</td>
                    <td style={{ padding: '12px 8px' }}>{(mlMetrics.f1_score * 100).toFixed(1)}%</td>
                    <td style={{ padding: '12px 8px' }}>{mlMetrics.roc_auc ? (mlMetrics.roc_auc * 100).toFixed(1) + '%' : 'N/A'}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '12px 8px', fontWeight: 600, color: 'var(--text-muted)' }}>GNN (Graph Neural Network)</td>
                    <td style={{ padding: '12px 8px' }}><Badge variant="neutral">Unavailable</Badge></td>
                    <td colSpan="4" style={{ padding: '12px 8px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      GNN disabled / experimental - Environment incompatible with PyTorch Geometric
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </PageContainer>
  );
};
