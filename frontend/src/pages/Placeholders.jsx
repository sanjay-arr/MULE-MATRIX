import React from 'react';
import { PageContainer } from '../components/layout/Layout';
import { EmptyState } from '../components/common/UI';
import { Network, Users, FileSearch, Bell, BarChart2 } from 'lucide-react';

export const NetworkExplorer = () => (
  <PageContainer title="Network Explorer">
    <EmptyState title="Network Explorer" description="Advanced network visualization will be implemented in Phase 6J+" icon={Network} />
  </PageContainer>
);

export const AccountExplorer = () => (
  <PageContainer title="Account Explorer">
    <EmptyState title="Account Explorer" description="Detailed account views and filtering" icon={Users} />
  </PageContainer>
);

export const Investigation = () => (
  <PageContainer title="Investigations">
    <EmptyState title="Investigations" description="Case management and investigation reports" icon={FileSearch} />
  </PageContainer>
);

export const Alerts = () => (
  <PageContainer title="System Alerts">
    <EmptyState title="Alerts" description="Full history of system alerts and notifications" icon={Bell} />
  </PageContainer>
);

export const Analytics = () => (
  <PageContainer title="Advanced Analytics">
    <EmptyState title="Analytics" description="Deep dive into system-wide metrics and trends" icon={BarChart2} />
  </PageContainer>
);
