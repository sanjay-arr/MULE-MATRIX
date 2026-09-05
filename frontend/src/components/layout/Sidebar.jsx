import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Activity, Network, Users, FileSearch, Bell, BarChart2 } from 'lucide-react';

export const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <Activity size={20} /> },
    { name: 'Network Explorer', path: '/networks', icon: <Network size={20} /> },
    { name: 'Account Explorer', path: '/accounts', icon: <Users size={20} /> },
    { name: 'Investigations', path: '/investigations', icon: <FileSearch size={20} /> },
    { name: 'Alerts', path: '/alerts', icon: <Bell size={20} /> },
    { name: 'Analytics', path: '/analytics', icon: <BarChart2 size={20} /> },
  ];

  return (
    <aside className="sidebar">
      <div style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid var(--border-dark)', marginBottom: '16px' }}>
        <Shield size={28} color="var(--accent-yellow)" />
        <h2 style={{ margin: 0, color: 'white', fontSize: '20px', letterSpacing: '1px' }}>MULE MATRIX</h2>
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {navItems.map((item) => (
          <NavLink 
            key={item.name} 
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span style={{ fontWeight: 500 }}>{item.name}</span>
          </NavLink>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', padding: '24px', fontSize: '12px', color: 'var(--text-muted)' }}>
        Mule Matrix Intelligence v1.0
      </div>
    </aside>
  );
};
