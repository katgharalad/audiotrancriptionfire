import axios from 'axios';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service for transcript-related operations
export const transcriptService = {
  // Interpret a transcript synchronously
  interpret: async (transcript: string) => {
    const response = await apiClient.post('/transcripts/interpret', { transcript });
    return response.data;
  },
  
  // Submit a transcript for asynchronous interpretation
  interpretAsync: async (transcript: string) => {
    const response = await apiClient.post('/transcripts/interpret-async', { transcript });
    return response.data;
  },
  
  // Get the result of an async interpretation task
  getTaskResult: async (taskId: string) => {
    const response = await apiClient.get(`/transcripts/results/${taskId}`);
    return response.data;
  },
};

// API service for address validation operations
export const validationService = {
  // Validate an address directly
  validateAddress: async (address: string) => {
    const response = await apiClient.post('/validation/address', { address });
    return response.data;
  },
  
  // Extract and validate an address from a transcript
  validateFromTranscript: async (transcript: string) => {
    const response = await apiClient.post('/validation/transcript', { transcript });
    return response.data;
  },
};

// API service for dispatch operations
export const dispatchService = {
  // Route an incident based on its interpretation
  routeIncident: async (interpretation: any) => {
    const response = await apiClient.post('/dispatch/route', { interpretation });
    return response.data;
  },
  
  // Get available emergency response units
  getAvailableUnits: async () => {
    const response = await apiClient.get('/dispatch/units');
    return response.data;
  },
};

// API service for audio operations
export const audioService = {
  // Process an audio file to generate a transcript
  processAudio: async (audioFile: File) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    
    const response = await apiClient.post('/audio/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // Simulate a transcript from text input
  simulateTranscript: async (text: string) => {
    const response = await apiClient.post('/audio/simulate', { text });
    return response.data;
  },
};

// Export a default API service object that includes all services
const apiService = {
  transcript: transcriptService,
  validation: validationService,
  dispatch: dispatchService,
  audio: audioService,
};

export default apiService; 