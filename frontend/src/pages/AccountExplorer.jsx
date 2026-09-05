import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '../components/layout/Layout';
import { Badge, Loader, EmptyState } from '../components/common/UI';
import { api } from '../services/api';
import { Users, Search, AlertTriangle, ShieldAlert, ArrowRight } from 'lucide-react';

export const AccountExplorer = () => {
  const [searchParams] = useSearchParams();
  const accountIdParam = searchParams.get('id');
  
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [mlPrediction, setMlPrediction] = useState(null);
  const [neighbors, setNeighbors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState(null);
  const [searchTerm, setSearchTerm] = useState(accountIdParam || '');
  const navigate = useNavigate();

  useEffect(() => {
    fetchAccounts();
    if (accountIdParam) {
      handleSelectAccount(accountIdParam);
    }
  }, [accountIdParam]);

  const fetchAccounts = async (search = '') => {
    try {
      setLoading(true);
      const data = await api.getAccounts({ page_size: 50, account_id: search || undefined });
      setAccounts(data.accounts || []);
    } catch (err) {
      console.error('Failed to fetch accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      fetchAccounts(searchTerm.trim());
      handleSelectAccount(searchTerm.trim());
    } else {
      fetchAccounts();
    }
  };

  // Caches
  const accountCache = useRef({});
  const neighborsCache = useRef({});
  const mlCache = useRef({});

  const handleSelectAccount = async (accountId) => {
    try {
      setDetailsError(null);
      
      // If we have cached account data, use it immediately
      if (accountCache.current[accountId]) {
        setSelectedAccount(accountCache.current[accountId]);
        setDetailsLoading(false);
      } else {
        setDetailsLoading(true);
        const accountData = await api.getAccountDetails(accountId);
        accountCache.current[accountId] = accountData;
        setSelectedAccount(accountData);
        setDetailsLoading(false);
      }

      // Now load secondary data (neighbors/transactions) non-blockingly
      if (neighborsCache.current[accountId]) {
        setNeighbors(neighborsCache.current[accountId]);
      } else {
        // Show loading state for neighbors by clearing them temporarily
        setNeighbors([]);
        api.getAccountNeighbors(accountId)
          .then(neighborsData => {
            const data = neighborsData.neighbors || [];
            neighborsCache.current[accountId] = data;
            if (selectedAccount?.account_id === accountId || !selectedAccount) {
              setNeighbors(data);
            }
          })
          .catch(() => {
            setNeighbors([]);
          });
      }

      // Load ML Prediction non-blockingly
      if (mlCache.current[accountId]) {
        setMlPrediction(mlCache.current[accountId]);
      } else {
        setMlPrediction(null);
        api.getMLPrediction(accountId)
          .then(mlData => {
            mlCache.current[accountId] = mlData;
            if (selectedAccount?.account_id === accountId || !selectedAccount) {
              setMlPrediction(mlData);
            }
          })
          .catch(() => {
            setMlPrediction(null);
          });
      }
    } catch (err) {
      console.error('Failed to fetch account details:', err);
      setDetailsError('Account not found or error loading details.');
      setSelectedAccount(null);
      setMlPrediction(null);
      setDetailsLoading(false);
    }
  };

  const handleInvestigate = () => {
    if (!selectedAccount) return;
    navigate(`/investigations?account_id=${selectedAccount.account_id}`);
  };

  return (
    <PageContainer title="Account Explorer">
      <div style={{ display: 'flex', gap: '24px', height: 'calc(100vh - 140px)' }}>
        
        {/* Left pane: Account list */}
        <div style={{ width: '350px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="Search Account ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ flex: 1, padding: '10px 12px', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}
            />
            <button type="submit" style={{ padding: '10px', backgroundColor: 'var(--bg-dark)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              <Search size={18} />
            </button>
          </form>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {loading ? <Loader message="Loading accounts..." /> : accounts.map(acc => (
              <div 
                key={acc.account_id}
                onClick={() => handleSelectAccount(acc.account_id)}
                className="card"
                style={{ 
                  cursor: 'pointer', padding: '16px',
                  border: selectedAccount?.account_id === acc.account_id ? '2px solid var(--accent-yellow)' : '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0 }}>{acc.account_id}</h4>
                  {acc.risk_level && <Badge variant={acc.risk_level.toLowerCase()}>{acc.risk_level}</Badge>}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Bank: {acc.bank_id} | Type: {acc.account_type || 'UNKNOWN'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right pane: Account Details */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto', padding: '24px' }}>
          {detailsLoading ? (
            <Loader message="Loading account details..." />
          ) : detailsError ? (
            <EmptyState title="Error" description={detailsError} icon={AlertTriangle} />
          ) : !selectedAccount ? (
            <EmptyState title="No Account Selected" description="Select an account from the list to view its details and risk profile." icon={Users} />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '20px' }}>
                <div>
                  <h2 style={{ margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {selectedAccount.account_id}
                    {selectedAccount.is_suspicious && <ShieldAlert color="var(--risk-critical)" size={24} />}
                  </h2>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: 'var(--text-muted)' }}>
                    <span>Bank: <strong style={{ color: 'var(--text-main)' }}>{selectedAccount.bank_id}</strong></span>
                    <span>Type: <strong style={{ color: 'var(--text-main)' }}>{selectedAccount.account_type || 'UNKNOWN'}</strong></span>
                  </div>
                </div>
                <button 
                  onClick={handleInvestigate}
                  style={{ padding: '10px 16px', backgroundColor: 'var(--bg-dark)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', display: 'flex', gap: '8px', alignItems: 'center', fontWeight: 600 }}
                >
                  Start Investigation <ArrowRight size={16} />
                </button>
              </div>

              {/* Risk Profile */}
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Risk Assessment</h3>
                <div style={{ display: 'flex', gap: '24px', alignItems: 'center', backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '36px', fontWeight: 700, color: selectedAccount.risk_level === 'CRITICAL' ? 'var(--risk-critical)' : selectedAccount.risk_level === 'HIGH' ? 'var(--risk-high)' : 'var(--text-main)' }}>
                      {Math.round(selectedAccount.risk_score || 0)}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Risk Score</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Detection Reasons</h4>
                    <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: 'var(--text-main)' }}>
                      {(selectedAccount.explanations || []).map((exp, idx) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>{exp}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* ML Intelligence Signal */}
                  {mlPrediction && (
                    <div style={{ width: '180px', padding: '16px', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: `1px solid ${mlPrediction.ml_prediction === 'MULE' ? 'var(--risk-critical)' : 'var(--border-subtle)'}` }}>
                      <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>ML Signal</h4>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: mlPrediction.ml_prediction === 'MULE' ? 'var(--risk-critical)' : 'var(--risk-low)', marginBottom: '4px' }}>
                        {mlPrediction.ml_prediction}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        Prob: {(mlPrediction.mule_probability * 100).toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Triggered Rules */}
              {selectedAccount.triggered_rules && selectedAccount.triggered_rules.length > 0 && (
                <div>
                  <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Triggered Behaviors</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {selectedAccount.triggered_rules.map(rule => (
                      <Badge key={rule} variant="high">{rule.replace(/_/g, ' ')}</Badge>
                    ))}
                  </div>
                </div>
              )}
              {/* Transactions / Connected Accounts */}
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Transactions & Connected Accounts ({neighbors.length})</h3>
                {neighbors.length === 0 ? (
                  <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center' }}>
                    Loading transactions... or no transactions found.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                      <span style={{ width: '80px' }}>DIRECTION</span>
                      <span style={{ flex: 1 }}>ACCOUNT ID / BANK</span>
                      <span style={{ width: '120px', textAlign: 'right' }}>AMOUNT</span>
                    </div>
                    {neighbors.map((n, idx) => (
                      <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid var(--border-subtle)' }}>
                        <div style={{ width: '80px' }}>
                          <Badge variant={n.direction === 'INCOMING' ? 'low' : 'high'}>{n.direction}</Badge>
                        </div>
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                          <span 
                            onClick={() => handleSelectAccount(n.account_id)}
                            style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', cursor: 'pointer', textDecoration: 'underline' }}
                          >
                            {n.account_id}
                          </span>
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Bank: {n.bank_id} {n.account_type === 'OFF_RAMP' ? ' (OFF-RAMP)' : ''}</span>
                        </div>
                        <div style={{ width: '120px', textAlign: 'right', fontSize: '14px', fontWeight: 600 }}>
                          ₹{n.amount.toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

      </div>
    </PageContainer>
  );
};
