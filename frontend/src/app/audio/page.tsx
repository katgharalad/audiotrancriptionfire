'use client';

import React, { useState, useRef } from 'react';
import { MainLayout } from '@/components/layout';
import { Button, Card } from '@/components/ui';
import { useAppContext } from '@/contexts/AppContext';
import apiService from '@/services/api';

type InputType = 'text' | 'recording' | 'file';

export default function AudioPage() {
  const { dispatch } = useAppContext();
  const [inputType, setInputType] = useState<InputType>('text');
  const [textInput, setTextInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interpretation, setInterpretation] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInputTypeChange = (type: InputType) => {
    setInputType(type);
    setTranscript('');
    setInterpretation(null);
    setError(null);
  };

  const processTranscript = async (text: string) => {
    try {
      setIsProcessing(true);
      setError(null);
      
      // Get interpretation from API
      const result = await apiService.transcript.interpret(text);
      
      if (result?.data?.interpretation) {
        setInterpretation(result.data.interpretation);
        
        // Create a new incident based on the interpretation
        const newIncident = {
          id: `incident-${Date.now()}`,
          interpretation: result.data.interpretation,
          timestamp: new Date().toISOString(),
          status: 'pending' as const,
        };
        
        // Add to global state
        dispatch({ type: 'ADD_INCIDENT', payload: newIncident });
        
        return result.data.interpretation;
      } else if (result?.error) {
        setError(result.error.message || 'Error processing transcript');
        return null;
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process transcript');
      console.error('Error processing transcript:', err);
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text');
      return;
    }
    
    setTranscript(textInput);
    await processTranscript(textInput);
  };

  const handleRecordingToggle = () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      
      // Simulate getting audio transcript (in a real app, this would use the Web Audio API)
      setIsProcessing(true);
      setTimeout(async () => {
        const simulatedTranscript = "This is a simulated transcript from recorded audio.";
        setTranscript(simulatedTranscript);
        await processTranscript(simulatedTranscript);
      }, 1500);
    } else {
      // Start recording
      setIsRecording(true);
      setTranscript('');
      setInterpretation(null);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    setAudioFile(file);
    
    // Process the audio file
    try {
      setIsProcessing(true);
      setError(null);
      
      // Get transcription from audio file
      const result = await apiService.audio.processAudio(file);
      
      if (result?.data?.result?.transcript) {
        const audioTranscript = result.data.result.transcript;
        setTranscript(audioTranscript);
        
        // Now process this transcript for interpretation
        await processTranscript(audioTranscript);
      } else if (result?.error) {
        setError(result.error.message || 'Error processing audio file');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process audio file');
      console.error('Error processing audio file:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const simulateAudio = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text to simulate');
      return;
    }
    
    try {
      setIsProcessing(true);
      setError(null);
      
      // Use the simulation API
      const result = await apiService.audio.simulateTranscript(textInput);
      
      if (result?.data?.result?.transcript) {
        const simulatedTranscript = result.data.result.transcript;
        setTranscript(simulatedTranscript);
        
        // Now process this transcript for interpretation
        await processTranscript(simulatedTranscript);
      } else if (result?.error) {
        setError(result.error.message || 'Error simulating audio');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to simulate audio');
      console.error('Error simulating audio:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Audio Input</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Button 
            variant={inputType === 'text' ? 'primary' : 'secondary'}
            onClick={() => handleInputTypeChange('text')}
            className="flex items-center justify-center"
          >
            <span className="mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8 3a1 1 0 11-2 0V7a1 1 0 112 0v6z" clipRule="evenodd" />
              </svg>
            </span>
            Text Input
          </Button>
          
          <Button 
            variant={inputType === 'recording' ? 'primary' : 'secondary'}
            onClick={() => handleInputTypeChange('recording')}
            className="flex items-center justify-center"
          >
            <span className="mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            </span>
            Live Recording
          </Button>
          
          <Button 
            variant={inputType === 'file' ? 'primary' : 'secondary'}
            onClick={() => handleInputTypeChange('file')}
            className="flex items-center justify-center"
          >
            <span className="mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
            </span>
            Upload File
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <Card title="Input" variant="elevated">
            {inputType === 'text' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Enter emergency call transcript</label>
                  <textarea 
                    className="w-full h-40 px-3 py-2 border rounded-md"
                    placeholder="Enter the transcript text here..."
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                  />
                </div>
                <div className="flex gap-3">
                  <Button 
                    variant="primary" 
                    onClick={handleTextSubmit}
                    disabled={isProcessing || !textInput.trim()}
                    isLoading={inputType === 'text' && isProcessing}
                  >
                    Process Transcript
                  </Button>
                  <Button 
                    variant="secondary" 
                    onClick={simulateAudio}
                    disabled={isProcessing || !textInput.trim()}
                    isLoading={inputType === 'text' && isProcessing}
                  >
                    Simulate Audio
                  </Button>
                </div>
              </div>
            )}
            
            {inputType === 'recording' && (
              <div className="space-y-4">
                <div className="flex flex-col items-center justify-center h-48">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center cursor-pointer ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-500'}`} onClick={handleRecordingToggle}>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="mt-4 text-center">
                    {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
                  </p>
                </div>
              </div>
            )}
            
            {inputType === 'file' && (
              <div className="space-y-4">
                <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-gray-300 rounded-md">
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    accept="audio/*" 
                    className="hidden" 
                  />
                  
                  {audioFile ? (
                    <div className="text-center">
                      <p className="text-lg font-medium">{audioFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <Button
                        variant="secondary"
                        className="mt-4"
                        onClick={handleFileSelect}
                        disabled={isProcessing}
                      >
                        Select Different File
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="mt-2 text-sm text-gray-500">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">
                        MP3, WAV, M4A up to 10MB
                      </p>
                      <Button 
                        variant="secondary" 
                        className="mt-4"
                        onClick={handleFileSelect}
                      >
                        Select File
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
                {error}
              </div>
            )}
          </Card>
          
          {/* Result Section */}
          <Card title="Result" variant="elevated">
            <div className="space-y-6">
              {isProcessing ? (
                <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
              ) : transcript ? (
                <div>
                  <h3 className="text-lg font-medium mb-2">Transcript</h3>
                  <div className="p-3 bg-gray-50 rounded-md border border-gray-200 mb-4">
                    <p className="whitespace-pre-wrap">{transcript}</p>
                  </div>
                  
                  {interpretation && (
                    <div>
                      <h3 className="text-lg font-medium mb-2">Interpretation</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-500 mb-1">Incident Type</h4>
                          <p className="font-medium">{interpretation.incident_type}</p>
                          <p className="text-xs text-gray-500">
                            Confidence: {Math.round(interpretation.incident_type_confidence * 100)}%
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-500 mb-1">Priority</h4>
                          <p className="font-medium">{interpretation.priority_level}</p>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-500 mb-1">Address</h4>
                          <p className="font-medium">{interpretation.address}</p>
                          <div className="mt-1">
                            {interpretation.address_validation?.address_validity ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                Valid Address
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                Address Needs Verification
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-500 mb-1">Casualties</h4>
                          <p className="font-medium">{interpretation.casualties || 'None reported'}</p>
                          <p className="text-xs text-gray-500">
                            Confidence: {Math.round((interpretation.casualties_confidence || 0) * 100)}%
                          </p>
                        </div>
                      </div>
                      
                      <div className="mt-4 text-right">
                        <Button 
                          variant="primary"
                          onClick={() => window.location.href = '/incidents'}
                        >
                          View All Incidents
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                  <p>Submit audio or text to see results</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
} 