import React, { useState, useEffect, useRef } from 'react';
import { PageContainer } from '../components/layout/Layout';
import { Badge, Loader, EmptyState } from '../components/common/UI';
import { api } from '../services/api';
import { Network, AlertCircle, ArrowRight, Info } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const getRiskColor = (score) => {
  if (score >= 80) return '#ef4444';
  if (score >= 60) return '#f97316';
  if (score >= 40) return '#eab308';
  return '#22c55e';
};

const GraphVisualization = ({ elements, onNodeSelect, onEdgeSelect }) => {
  const containerRef = useRef(null);
  const graphRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !elements) return;

    const nodes = (elements.nodes || []).map(n => ({
      id: n.id,
      label: n.id.slice(-8),
      bank_id: n.bank_id,
      risk_score: n.risk_score || 0,
      account_type: n.account_type || 'CUSTOMER',
      ...n
    }));

    const links = (elements.edges || []).map(e => ({
      source: e.source,
      target: e.target,
      amount: e.amount || 0
    }));

    // Clean up previous graph instance if it exists
    if (graphRef.current) {
      containerRef.current.innerHTML = '';
    }

    if (window.ForceGraph) {
      graphRef.current = window.ForceGraph()(containerRef.current)
        .width(containerRef.current.clientWidth)
        .height(containerRef.current.clientHeight || 500)
        .graphData({ nodes, links })
        .nodeCanvasObject((node, ctx, globalScale) => {
          const label = node.id.slice(-8);
          const fontSize = 10 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          
          const size = Math.max(3, Math.min(8, node.risk_score / 15));
          
          ctx.fillStyle = getRiskColor(node.risk_score);
          
          if (node.account_type === 'OFF_RAMP') {
            // Draw star
            ctx.beginPath();
            for (let i = 0; i < 5; i++) {
              ctx.lineTo(node.x + size * 1.5 * Math.cos((18 + i * 72) * Math.PI / 180), node.y - size * 1.5 * Math.sin((18 + i * 72) * Math.PI / 180));
              ctx.lineTo(node.x + size * 0.7 * Math.cos((54 + i * 72) * Math.PI / 180), node.y - size * 0.7 * Math.sin((54 + i * 72) * Math.PI / 180));
            }
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 0.5 / globalScale;
            ctx.stroke();
          } else {
            // Draw circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI, false);
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 0.5 / globalScale;
            ctx.stroke();
          }

          // Draw label
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#cbd5e1';
          ctx.fillText(label, node.x, node.y + size + 2 + fontSize);
        })
        .nodeLabel(node => `<div style="background: rgba(15,23,42,0.9); padding: 8px; border-radius: 4px; border: 1px solid #334155; font-size: 12px; color: white;">
          <strong>${node.id}</strong><br/>
          Bank: ${node.bank_id}<br/>
          Type: ${node.account_type}<br/>
          Risk: ${node.risk_score}
        </div>`)
        .onNodeClick(node => {
          if (onNodeSelect) onNodeSelect(node);
        })
        .onLinkClick(link => {
          if (onEdgeSelect) onEdgeSelect(link);
        })
        .onBackgroundClick(() => {
          if (onNodeSelect) onNodeSelect(null);
          if (onEdgeSelect) onEdgeSelect(null);
        })
        .linkColor(() => 'rgba(203, 213, 225, 0.4)')
        .linkWidth(1)
        .linkDirectionalArrowLength(3.5)
        .linkDirectionalArrowRelPos(1);
    }

    return () => {
      if (graphRef.current) {
        graphRef.current._destructor && graphRef.current._destructor();
        if (containerRef.current) containerRef.current.innerHTML = '';
      }
    };
  }, [elements]);

  const controlBtnStyle = {
    background: 'rgba(15,23,42,0.85)', color: '#cbd5e1', border: '1px solid #334155', 
    borderRadius: '6px', width: '32px', height: '32px', cursor: 'pointer', 
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px',
    transition: 'all 0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  };

  return (
    <div style={{ position: 'relative', width: '100%', flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', height: '100%', 
          backgroundColor: '#0f172a', 
          backgroundImage: 'radial-gradient(#334155 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          borderRadius: '8px', 
          border: '1px solid #334155', 
          minHeight: '400px', 
          overflow: 'hidden' 
        }} 
      />

      {/* Graph Overlay Controls */}
      <div style={{ position: 'absolute', top: '16px', left: '16px', display: 'flex', flexDirection: 'column', gap: '8px', zIndex: 5 }}>
        <button 
          title="Zoom In"
          onClick={() => graphRef.current?.zoom(graphRef.current.zoom() * 1.3, 400)} 
          style={controlBtnStyle}
          onMouseOver={(e) => e.target.style.color = '#fff'}
          onMouseOut={(e) => e.target.style.color = '#cbd5e1'}
        >+</button>
        <button 
          title="Zoom Out"
          onClick={() => graphRef.current?.zoom(graphRef.current.zoom() / 1.3, 400)} 
          style={controlBtnStyle}
          onMouseOver={(e) => e.target.style.color = '#fff'}
          onMouseOut={(e) => e.target.style.color = '#cbd5e1'}
        >−</button>
        <button 
          title="Fit to Screen"
          onClick={() => graphRef.current?.zoomToFit(400)} 
          style={controlBtnStyle}
          onMouseOver={(e) => e.target.style.color = '#fff'}
          onMouseOut={(e) => e.target.style.color = '#cbd5e1'}
        >⛶</button>
      </div>

      {/* Legend */}
      <div style={{ position: 'absolute', bottom: '16px', left: '16px', display: 'flex', gap: '16px', background: 'rgba(15,23,42,0.9)', padding: '10px 16px', borderRadius: '8px', border: '1px solid #334155', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
        <div style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 600, marginRight: '4px', display: 'flex', alignItems: 'center' }}>RISK:</div>
        {[['#ef4444', 'CRITICAL'], ['#f97316', 'HIGH'], ['#eab308', 'MED'], ['#22c55e', 'NORMAL']].map(([c, l]) => (
          <div key={l} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#cbd5e1', fontWeight: 500 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: c, boxShadow: `0 0 8px ${c}` }} /> {l}
          </div>
        ))}
        <div style={{ width: '1px', height: '14px', background: '#334155', margin: '0 4px' }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: '#cbd5e1', fontWeight: 500 }}>
          <div style={{ width: 12, height: 12, clipPath: 'polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%)', background: '#ef4444', boxShadow: '0 0 8px #ef4444' }} /> OFF-RAMP
        </div>
      </div>
    </div>
  );
};

export const NetworkExplorer = () => {
  const [networks, setNetworks] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState(null);
  const [error, setError] = useState(null);
  const [selectedElementInfo, setSelectedElementInfo] = useState(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const networkIdParam = searchParams.get('id') || searchParams.get('network_id');

  const graphCache = useRef({});

  useEffect(() => {
    const fetchNetworks = async () => {
      try {
        setLoading(true);
        const data = await api.getNetworks();
        setNetworks(data.networks || []);
      } catch (err) {
        console.error('Failed to fetch networks:', err);
        setError('Unable to load networks');
      } finally {
        setLoading(false);
      }
    };
    fetchNetworks();
  }, []);

  useEffect(() => {
    if (networkIdParam && networks.length > 0) {
      const matchedNetwork = networks.find(n => n.network_id === networkIdParam);
      if (matchedNetwork && (!selectedNetwork || selectedNetwork.network_id !== networkIdParam)) {
        handleSelectNetwork(matchedNetwork);
      }
    }
  }, [networkIdParam, networks]);

  const handleSelectNetwork = async (network) => {
    setSelectedNetwork(network);
    setSelectedElementInfo(null);
    setGraphError(null);

    if (graphCache.current[network.network_id]) {
      setGraphData(graphCache.current[network.network_id]);
      return;
    }

    try {
      setGraphLoading(true);
      setGraphData(null);
      const data = await api.getNetworkGraph(network.network_id);
      graphCache.current[network.network_id] = data;
      setGraphData(data);
    } catch (err) {
      console.error('Failed to fetch graph:', err);
      setGraphError('Failed to load graph data.');
    } finally {
      setGraphLoading(false);
    }
  };

  if (loading) return <PageContainer title="Network Explorer"><Loader message="Detecting mule networks..." /></PageContainer>;
  if (error) return <PageContainer title="Network Explorer"><EmptyState title="Error" description={error} icon={AlertCircle} /></PageContainer>;

  return (
    <PageContainer title="Network Explorer">
      <div style={{ display: 'flex', gap: '24px', height: 'calc(100vh - 140px)' }}>

        {/* Left pane: List of networks */}
        <div style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '4px 0' }}>
            {networks.length} mule networks detected
          </div>
          {networks.map(net => (
            <div
              key={net.network_id}
              onClick={() => handleSelectNetwork(net)}
              className="card"
              style={{
                cursor: 'pointer', padding: '14px',
                border: selectedNetwork?.network_id === net.network_id ? '2px solid var(--accent-yellow)' : '1px solid var(--border-subtle)',
                transition: 'all 0.15s',
                borderLeft: selectedNetwork?.network_id === net.network_id 
                  ? '2px solid var(--accent-yellow)'
                  : net.risk_level === 'CRITICAL' ? '3px solid var(--risk-critical)'
                  : net.risk_level === 'HIGH' ? '3px solid var(--risk-high)'
                  : '3px solid var(--risk-medium)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ margin: 0, fontSize: '12px', fontFamily: 'monospace' }}>{net.network_id}</h4>
                <Badge variant={net.risk_level?.toLowerCase()}>{net.risk_level}</Badge>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
                <div>Accounts: <strong style={{ color: 'var(--text-main)' }}>{net.accounts}</strong></div>
                <div>Banks: <strong style={{ color: 'var(--text-main)' }}>{net.banks}</strong></div>
                <div>Off-Ramps: <strong style={{ color: 'var(--risk-critical)' }}>{net.off_ramps}</strong></div>
                <div>Vol: <strong style={{ color: 'var(--text-main)' }}>₹{(net.total_amount / 1e6).toFixed(1)}M</strong></div>
              </div>
            </div>
          ))}
        </div>

        {/* Right pane: Graph visualization */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '20px' }}>
          {!selectedNetwork ? (
            <EmptyState title="No Network Selected" description="Select a mule network from the list to visualize its transaction graph." icon={Network} />
          ) : (
            <>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexShrink: 0 }}>
                <div>
                  <h3 style={{ margin: '0 0 4px 0', fontSize: '15px' }}>{selectedNetwork.network_id}</h3>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', display: 'flex', gap: '16px' }}>
                    <span>{selectedNetwork.accounts} accounts</span>
                    <span>{selectedNetwork.banks} banks</span>
                    <span style={{ color: 'var(--risk-critical)' }}>{selectedNetwork.off_ramps} off-ramps</span>
                    {graphData && <span style={{ color: '#64748b' }}>(showing top {graphData.nodes?.length || 0} by risk)</span>}
                  </div>
                </div>
                <button
                  onClick={() => navigate(`/investigations?network_id=${selectedNetwork.network_id}`)}
                  style={{ padding: '8px 16px', backgroundColor: 'var(--bg-dark)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'flex', gap: '8px', alignItems: 'center', fontSize: '13px', fontWeight: 600, flexShrink: 0 }}
                >
                  Open Investigation <ArrowRight size={14} />
                </button>
              </div>

              {/* Graph Area */}
              <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                {graphLoading ? (
                  <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0f172a', borderRadius: '8px' }}>
                    <Loader message="Building graph..." />
                  </div>
                ) : graphError ? (
                  <EmptyState title="Graph Error" description={graphError} icon={AlertCircle} />
                ) : graphData && graphData.nodes?.length > 0 ? (
                  <GraphVisualization
                    elements={graphData}
                    onNodeSelect={(data) => setSelectedElementInfo(data ? { type: 'node', data } : null)}
                    onEdgeSelect={(data) => setSelectedElementInfo(data ? { type: 'edge', data } : null)}
                  />
                ) : graphData ? (
                  <EmptyState title="No graph data" description="No transactions found between accounts in this network." icon={Info} />
                ) : null}

                {/* Floating info card */}
                {selectedElementInfo && (
                  <div style={{ position: 'absolute', top: '12px', right: '12px', width: '260px', backgroundColor: 'rgba(255,255,255,0.97)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '16px', boxShadow: '0 8px 24px rgba(0,0,0,0.12)', zIndex: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <h4 style={{ margin: 0, fontSize: '13px' }}>
                        {selectedElementInfo.type === 'node' ? '🏦 Account Details' : '💸 Transaction'}
                      </h4>
                      <button onClick={() => setSelectedElementInfo(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '16px', lineHeight: 1 }}>×</button>
                    </div>

                    {selectedElementInfo.type === 'node' ? (
                      <div style={{ fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ fontFamily: 'monospace', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>{selectedElementInfo.data.id}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Bank</span>
                          <strong>{selectedElementInfo.data.bank_id}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Type</span>
                          <strong style={{ color: selectedElementInfo.data.account_type === 'OFF_RAMP' ? 'var(--risk-critical)' : 'inherit' }}>
                            {selectedElementInfo.data.account_type || 'CUSTOMER'}
                          </strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Risk Score</span>
                          <strong style={{ color: getRiskColor(selectedElementInfo.data.risk_score) }}>
                            {Math.round(selectedElementInfo.data.risk_score || 0)}
                          </strong>
                        </div>
                        <button
                          onClick={() => navigate(`/accounts?id=${selectedElementInfo.data.id}`)}
                          style={{ marginTop: '8px', padding: '8px', width: '100%', backgroundColor: 'var(--bg-dark)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}
                        >
                          Open Account →
                        </button>
                      </div>
                    ) : (
                      <div style={{ fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Amount</span>
                          <strong>₹{(selectedElementInfo.data.amount || 0).toLocaleString()}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>From</span>
                          <code style={{ fontSize: '11px' }}>{selectedElementInfo.data.source.id || selectedElementInfo.data.source}</code>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>To</span>
                          <code style={{ fontSize: '11px' }}>{selectedElementInfo.data.target.id || selectedElementInfo.data.target}</code>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </PageContainer>
  );
};
