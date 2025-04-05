'use client';

import React, { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout';
import { Card, Button } from '@/components/ui';
import { IncidentCard } from '@/components/incidents';
import { useAppContext } from '@/contexts/AppContext';
import Link from 'next/link';

export default function Home() {
  const { state } = useAppContext();
  const [stats, setStats] = useState({
    recentIncidents: 0,
    needingVerification: 0,
    dispatchedUnits: 0
  });

  useEffect(() => {
    // Calculate stats based on incidents data
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const recentIncidents = state.incidents.filter(incident => {
      const incidentDate = new Date(incident.timestamp);
      return incidentDate >= oneDayAgo;
    }).length;

    const needingVerification = state.incidents.filter(
      incident => incident.interpretation.needs_verification
    ).length;

    // This would normally come from a backend API with real dispatch data
    // For now, we'll just use a calculated value based on dispatched incidents
    const dispatchedUnits = state.incidents.filter(
      incident => incident.status === 'dispatched'
    ).length * 2; // Assuming each dispatched incident has roughly 2 units

    setStats({
      recentIncidents,
      needingVerification,
      dispatchedUnits
    });
  }, [state.incidents]);

  // Get only the 3 most recent incidents
  const recentIncidents = [...state.incidents]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 3);

  return (
    <MainLayout>
      <div className="grid grid-cols-1 gap-8">
        <section>
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <Link href="/audio">
              <Button variant="primary">New Incident</Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card title="Recent Incidents" variant="elevated">
              <div className="text-3xl font-bold text-blue-600">{stats.recentIncidents}</div>
              <div className="text-sm text-gray-500">in the last 24 hours</div>
            </Card>

            <Card title="Requiring Verification" variant="elevated">
              <div className="text-3xl font-bold text-yellow-500">{stats.needingVerification}</div>
              <div className="text-sm text-gray-500">incidents pending verification</div>
            </Card>

            <Card title="Units Dispatched" variant="elevated">
              <div className="text-3xl font-bold text-green-600">{stats.dispatchedUnits}</div>
              <div className="text-sm text-gray-500">emergency units currently active</div>
            </Card>
          </div>
        </section>

        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Incidents</h2>
            <Link href="/incidents">
              <Button variant="secondary">View All</Button>
            </Link>
          </div>
          
          {state.isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : recentIncidents.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentIncidents.map((incident) => (
                <IncidentCard 
                  key={incident.id} 
                  incident={incident}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="text-xl text-gray-500 dark:text-gray-400">No incidents recorded yet</p>
              <Link href="/audio">
                <Button variant="primary" className="mt-4">
                  Create First Incident
                </Button>
              </Link>
            </div>
          )}
        </section>
      </div>
    </MainLayout>
  );
}
