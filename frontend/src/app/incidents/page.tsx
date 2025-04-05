"use client";

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout';
import { Button, Badge, Card } from '@/components/ui';
import { IncidentCard } from '@/components/incidents';
import { useAppContext } from '@/contexts/AppContext';

export default function IncidentsPage() {
  const { state } = useAppContext();
  const [filteredIncidents, setFilteredIncidents] = useState(state.incidents);
  const [priorityFilter, setPriorityFilter] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [verificationFilter, setVerificationFilter] = useState<boolean | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Re-apply filters when state.incidents changes
  useEffect(() => {
    applyFilters();
  }, [state.incidents, priorityFilter, statusFilter, verificationFilter, searchTerm]);

  const applyFilters = () => {
    let filtered = [...state.incidents];

    // Apply priority filter
    if (priorityFilter !== null) {
      filtered = filtered.filter(incident => incident.interpretation.priority === priorityFilter);
    }

    // Apply status filter
    if (statusFilter) {
      filtered = filtered.filter(incident => incident.status === statusFilter);
    }

    // Apply verification filter
    if (verificationFilter !== null) {
      filtered = filtered.filter(incident => incident.interpretation.needs_verification === verificationFilter);
    }

    // Apply search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(incident => 
        incident.interpretation.incident_type.toLowerCase().includes(term) ||
        incident.interpretation.address.toLowerCase().includes(term)
      );
    }

    setFilteredIncidents(filtered);
  };

  const resetFilters = () => {
    setPriorityFilter(null);
    setStatusFilter(null);
    setVerificationFilter(null);
    setSearchTerm('');
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">All Incidents</h1>
          <div className="flex gap-2">
            <Button onClick={resetFilters} variant="secondary">Reset Filters</Button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Search</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search incidents..."
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select
                value={priorityFilter === null ? '' : priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value ? Number(e.target.value) : null)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="">All Priorities</option>
                <option value="1">High</option>
                <option value="2">Medium</option>
                <option value="3">Low</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select
                value={statusFilter || ''}
                onChange={(e) => setStatusFilter(e.target.value || null)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="verified">Verified</option>
                <option value="dispatched">Dispatched</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Verification</label>
              <select
                value={verificationFilter === null ? '' : verificationFilter.toString()}
                onChange={(e) => {
                  if (e.target.value === '') {
                    setVerificationFilter(null);
                  } else {
                    setVerificationFilter(e.target.value === 'true');
                  }
                }}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="">All</option>
                <option value="true">Needs Verification</option>
                <option value="false">Verified</option>
              </select>
            </div>
          </div>
        </div>

        {state.isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredIncidents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredIncidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-xl text-gray-500 dark:text-gray-400">No incidents match your filters</p>
            <Button onClick={resetFilters} variant="primary" className="mt-4">
              Clear Filters
            </Button>
          </div>
        )}
      </div>
    </MainLayout>
  );
} 