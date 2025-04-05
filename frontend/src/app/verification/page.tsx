'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/components/layout';
import { Button, Card, Badge } from '@/components/ui';
import { useAppContext } from '@/contexts/AppContext';
import { IncidentCard } from '@/components/incidents';

export default function VerificationPage() {
  const { state, dispatch } = useAppContext();
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [notes, setNotes] = useState('');

  // Filter incidents that need verification
  const incidentsNeedingVerification = state.incidents.filter(
    incident => incident.interpretation.needs_verification && incident.status !== 'verified'
  );

  // Get the selected incident
  const selectedIncident = selectedIncidentId 
    ? state.incidents.find(incident => incident.id === selectedIncidentId) 
    : null;

  // When the verification page loads, select the first incident if available
  useEffect(() => {
    if (incidentsNeedingVerification.length > 0 && !selectedIncidentId) {
      setSelectedIncidentId(incidentsNeedingVerification[0].id);
    }
  }, [incidentsNeedingVerification, selectedIncidentId]);

  const handleIncidentSelect = (id: string) => {
    setSelectedIncidentId(id);
    setNotes('');
  };

  const handleVerifyIncident = () => {
    if (selectedIncidentId) {
      dispatch({
        type: 'UPDATE_INCIDENT',
        payload: {
          id: selectedIncidentId,
          data: {
            status: 'verified',
            interpretation: {
              ...selectedIncident?.interpretation,
              needs_verification: false,
              verification_notes: notes,
              verified_by: state.user?.name || 'Unknown',
              verified_at: new Date().toISOString()
            }
          }
        }
      });
      
      // Select the next incident if available
      const currentIndex = incidentsNeedingVerification.findIndex(inc => inc.id === selectedIncidentId);
      if (currentIndex < incidentsNeedingVerification.length - 1) {
        setSelectedIncidentId(incidentsNeedingVerification[currentIndex + 1].id);
      } else if (incidentsNeedingVerification.length > 1) {
        setSelectedIncidentId(incidentsNeedingVerification[0].id);
      } else {
        setSelectedIncidentId(null);
      }
      
      setNotes('');
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Incident Verification</h1>
        
        {state.isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : incidentsNeedingVerification.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-xl text-gray-500 dark:text-gray-400">No incidents need verification</p>
            <Button variant="primary" className="mt-4" onClick={() => window.location.href = '/incidents'}>
              View All Incidents
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left sidebar - List of incidents */}
            <div className="md:col-span-1">
              <h2 className="text-lg font-semibold mb-4">Pending Verification</h2>
              <div className="space-y-4 overflow-auto max-h-[calc(100vh-240px)]">
                {incidentsNeedingVerification.map(incident => (
                  <div 
                    key={incident.id} 
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedIncidentId === incident.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => handleIncidentSelect(incident.id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium">{incident.interpretation.incident_type}</h3>
                      <Badge variant={
                        incident.interpretation.priority === 1 ? 'danger' : 
                        incident.interpretation.priority === 2 ? 'warning' : 'info'
                      }>
                        {incident.interpretation.priority_level}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">{incident.interpretation.address}</p>
                    <div className="text-xs text-gray-500">
                      {new Date(incident.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Right panel - Selected incident details and verification form */}
            <div className="md:col-span-2">
              {selectedIncident ? (
                <Card variant="elevated" className="p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h2 className="text-xl font-semibold">{selectedIncident.interpretation.incident_type}</h2>
                    <Badge variant={
                      selectedIncident.interpretation.priority === 1 ? 'danger' : 
                      selectedIncident.interpretation.priority === 2 ? 'warning' : 'info'
                    } size="lg">
                      {selectedIncident.interpretation.priority_level}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-1">Address</h3>
                      <p className="text-gray-900 dark:text-gray-100">{selectedIncident.interpretation.address}</p>
                      <div className="mt-2">
                        <Badge variant={selectedIncident.interpretation.address_validation.address_validity ? 'success' : 'danger'}>
                          {selectedIncident.interpretation.address_validation.address_validity ? 'Validated' : 'Needs Address Verification'}
                        </Badge>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-1">Time Reported</h3>
                      <p className="text-gray-900 dark:text-gray-100">{new Date(selectedIncident.timestamp).toLocaleString()}</p>
                      <h3 className="text-sm font-medium text-gray-500 mt-3 mb-1">Status</h3>
                      <Badge variant={
                        selectedIncident.status === 'dispatched' ? 'success' : 
                        selectedIncident.status === 'processing' ? 'warning' : 'info'
                      }>
                        {selectedIncident.status.charAt(0).toUpperCase() + selectedIncident.status.slice(1)}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-1">Casualties</h3>
                    <p className="text-gray-900 dark:text-gray-100 mb-2">{selectedIncident.interpretation.casualties}</p>
                    <div className="flex space-x-2">
                      {selectedIncident.interpretation.casualties_structured.trapped && (
                        <Badge variant="danger">People Trapped</Badge>
                      )}
                      {selectedIncident.interpretation.casualties_structured.injured && (
                        <Badge variant="warning">Injuries Reported</Badge>
                      )}
                    </div>
                  </div>
                  
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Verification Notes</h3>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full border rounded-lg p-3 min-h-[120px]"
                      placeholder="Add any verification notes, corrections, or additional information..."
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3">
                    <Button variant="secondary" onClick={() => setSelectedIncidentId(null)}>
                      Cancel
                    </Button>
                    <Button variant="primary" onClick={handleVerifyIncident}>
                      Verify & Dispatch
                    </Button>
                  </div>
                </Card>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-gray-500 dark:text-gray-400">Select an incident to verify</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
} 