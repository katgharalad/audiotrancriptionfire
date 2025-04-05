'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/layout';
import { Card, Button, Badge } from '@/components/ui';
import { MdMic, MdKeyboardVoice, MdFileUpload, MdCheck, MdClose } from 'react-icons/md';

export default function AudioPage() {
  const [inputType, setInputType] = useState<'live' | 'simulation' | 'upload'>('simulation');
  const [simulationText, setSimulationText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    if (!simulationText) return;
    
    setIsProcessing(true);
    
    // In a real application, this would make an API call to the audio simulation endpoint
    try {
      // Simulate an API call with timeout
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setTranscript(simulationText);
      setResult({
        interpretation: {
          incident_type: 'Structure Fire',
          incident_type_confidence: 0.89,
          address: '123 Main Street, Anytown, DE',
          address_validation: {
            address_validity: true,
            matched_address: '123 Main St, Anytown, DE 19801',
            confidence_score: 0.95
          },
          casualties: 'Two people trapped on second floor',
          casualties_confidence: 0.78,
          priority: 1,
          priority_level: 'High'
        },
        success: true
      });
    } catch (error) {
      console.error('Error simulating audio', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    
    // In a real application, this would upload the file to the API
    try {
      // Simulate an API call with timeout
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setTranscript('Fire reported at 456 Oak Avenue. Caller states there is smoke coming from the kitchen. No injuries reported.');
      setResult({
        interpretation: {
          incident_type: 'Kitchen Fire',
          incident_type_confidence: 0.92,
          address: '456 Oak Avenue, Anytown, DE',
          address_validation: {
            address_validity: true,
            matched_address: '456 Oak Ave, Anytown, DE 19801',
            confidence_score: 0.97
          },
          casualties: 'No injuries reported',
          casualties_confidence: 0.95,
          priority: 2,
          priority_level: 'Medium'
        },
        success: true
      });
    } catch (error) {
      console.error('Error uploading file', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRecording = () => {
    setIsRecording(!isRecording);
    
    if (!isRecording) {
      // Start recording logic would go here
      console.log('Started recording');
    } else {
      // Stop recording and process audio
      console.log('Stopped recording');
      setIsProcessing(true);
      
      // Simulate processing
      setTimeout(() => {
        setTranscript('Traffic accident at the intersection of Main Street and 5th Avenue. One car overturned. Possible injuries.');
        setResult({
          interpretation: {
            incident_type: 'Traffic Accident',
            incident_type_confidence: 0.85,
            address: 'Intersection of Main St and 5th Ave, Anytown, DE',
            address_validation: {
              address_validity: false,
              potential_matches: [
                'Main St & 5th Ave, Anytown, DE 19801',
                'Main St & 5th Avenue, Anytown, Delaware'
              ],
              confidence_score: 0.65,
              needs_verification: true
            },
            casualties: 'Possible injuries reported',
            casualties_confidence: 0.72,
            priority: 2,
            priority_level: 'Medium'
          },
          success: true
        });
        setIsProcessing(false);
        setIsRecording(false);
      }, 2000);
    }
  };

  const clearResults = () => {
    setTranscript('');
    setResult(null);
  };

  return (
    <MainLayout>
      <div className="grid grid-cols-1 gap-8">
        <section>
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Audio Processing</h1>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Audio Input */}
            <div>
              <Card title="Audio Input" variant="elevated">
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <Button 
                      variant={inputType === 'live' ? 'primary' : 'secondary'} 
                      onClick={() => setInputType('live')}
                      leftIcon={<MdMic />}
                    >
                      Live Input
                    </Button>
                    <Button 
                      variant={inputType === 'simulation' ? 'primary' : 'secondary'} 
                      onClick={() => setInputType('simulation')}
                      leftIcon={<MdKeyboardVoice />}
                    >
                      Simulation
                    </Button>
                    <Button 
                      variant={inputType === 'upload' ? 'primary' : 'secondary'} 
                      onClick={() => setInputType('upload')}
                      leftIcon={<MdFileUpload />}
                    >
                      Upload
                    </Button>
                  </div>
                  
                  {/* Live Input */}
                  {inputType === 'live' && (
                    <div className="space-y-4">
                      <p className="text-gray-600 text-sm">Record live audio to process an emergency call</p>
                      <div className="flex justify-center">
                        <Button
                          variant={isRecording ? 'danger' : 'primary'}
                          size="lg"
                          onClick={handleRecording}
                          className="rounded-full h-16 w-16 flex items-center justify-center"
                        >
                          <MdMic className="text-2xl" />
                        </Button>
                      </div>
                      {isRecording && (
                        <div className="text-center">
                          <Badge variant="danger">Recording</Badge>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Simulation Input */}
                  {inputType === 'simulation' && (
                    <div className="space-y-4">
                      <p className="text-gray-600 text-sm">Enter text to simulate an emergency call</p>
                      <textarea
                        className="w-full border border-gray-300 rounded-md px-3 py-2 min-h-[120px]"
                        placeholder="Enter emergency call transcript simulation..."
                        value={simulationText}
                        onChange={(e) => setSimulationText(e.target.value)}
                      />
                      <Button 
                        variant="primary" 
                        onClick={handleSimulate}
                        disabled={isProcessing || !simulationText}
                        isLoading={isProcessing && inputType === 'simulation'}
                      >
                        Process Simulation
                      </Button>
                    </div>
                  )}
                  
                  {/* File Upload */}
                  {inputType === 'upload' && (
                    <div className="space-y-4">
                      <p className="text-gray-600 text-sm">Upload an audio file of an emergency call</p>
                      <div className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center">
                        <input
                          type="file"
                          accept="audio/*"
                          className="hidden"
                          id="audio-file"
                          onChange={handleFileUpload}
                        />
                        <label htmlFor="audio-file" className="cursor-pointer">
                          <div className="flex flex-col items-center">
                            <MdFileUpload className="text-3xl text-gray-400" />
                            <span className="mt-2 text-sm text-gray-500">
                              {file ? file.name : 'Click to upload audio file'}
                            </span>
                          </div>
                        </label>
                      </div>
                      <Button 
                        variant="primary" 
                        onClick={handleUpload}
                        disabled={isProcessing || !file}
                        isLoading={isProcessing && inputType === 'upload'}
                      >
                        Process Audio File
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            </div>
            
            {/* Results */}
            <div>
              <Card title="Processing Results" variant="elevated">
                {transcript ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Transcript</h3>
                      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <p className="text-gray-800">{transcript}</p>
                      </div>
                    </div>
                    
                    {result && (
                      <div className="space-y-4">
                        <h3 className="font-medium text-gray-900 mb-2">Interpretation</h3>
                        
                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-sm text-gray-600">Incident Type</p>
                            <p className="font-medium text-gray-800">{result.interpretation.incident_type}</p>
                            <div className="mt-1 flex items-center">
                              <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-blue-600 rounded-full"
                                  style={{ width: `${Math.round(result.interpretation.incident_type_confidence * 100)}%` }}
                                />
                              </div>
                              <span className="ml-2 text-xs text-gray-500">
                                {Math.round(result.interpretation.incident_type_confidence * 100)}%
                              </span>
                            </div>
                          </div>
                          
                          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                            <p className="text-sm text-gray-600">Priority</p>
                            <p className="font-medium text-gray-800">{result.interpretation.priority_level}</p>
                            <div className="mt-1">
                              {result.interpretation.priority === 1 && (
                                <Badge variant="danger" withDot>High</Badge>
                              )}
                              {result.interpretation.priority === 2 && (
                                <Badge variant="warning" withDot>Medium</Badge>
                              )}
                              {result.interpretation.priority === 3 && (
                                <Badge variant="info" withDot>Low</Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-600">Address</p>
                          <p className="font-medium text-gray-800">{result.interpretation.address}</p>
                          
                          {result.interpretation.address_validation.address_validity ? (
                            <div className="flex items-center mt-1 text-green-600 text-sm">
                              <MdCheck className="mr-1" /> Valid
                            </div>
                          ) : (
                            <div className="flex items-center mt-1 text-red-600 text-sm">
                              <MdClose className="mr-1" /> Needs verification
                            </div>
                          )}
                          
                          {result.interpretation.address_validation.matched_address && (
                            <p className="text-sm mt-1 text-gray-500">
                              Matched: {result.interpretation.address_validation.matched_address}
                            </p>
                          )}
                        </div>
                        
                        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-600">Casualties</p>
                          <p className="font-medium text-gray-800">{result.interpretation.casualties}</p>
                          <div className="mt-1 flex items-center">
                            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-blue-600 rounded-full"
                                style={{ width: `${Math.round(result.interpretation.casualties_confidence * 100)}%` }}
                              />
                            </div>
                            <span className="ml-2 text-xs text-gray-500">
                              {Math.round(result.interpretation.casualties_confidence * 100)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex space-x-3 pt-4">
                          <Button variant="primary" fullWidth>
                            Send to Dispatch
                          </Button>
                          <Button variant="secondary" onClick={clearResults}>
                            Clear
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="py-10 text-center">
                    <p className="text-gray-500">No results to display. Process audio to see interpretation.</p>
                  </div>
                )}
              </Card>
            </div>
          </div>
        </section>
      </div>
    </MainLayout>
  );
} 