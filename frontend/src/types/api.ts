// Transcript-related interfaces
export interface TranscriptRequest {
  transcript: string;
}

export interface InterpretationResult {
  incident_type: string;
  incident_type_confidence: number;
  address: string;
  address_validation: Record<string, any>;
  casualties: string;
  casualties_confidence: number;
  casualties_structured: Record<string, boolean>;
  priority: number;
  priority_level: string;
  needs_verification: boolean;
}

export interface TranscriptResponse {
  interpretation: Record<string, any>;
  processed: boolean;
}

export interface AsyncTaskResponse {
  task_id: string;
  status: string;
}

export interface TaskResultResponse {
  status: string;
  interpretation?: Record<string, any>;
}

// Validation-related interfaces
export interface AddressRequest {
  address: string;
}

export interface ValidationResult {
  address_validity: boolean;
  matched_address?: string;
  matched_landmark?: string;
  confidence_score: number;
  zip_code?: string;
  jurisdiction?: string;
  needs_verification: boolean;
  processing_time_ms?: number;
  extracted_address?: string;
  error?: string;
}

export interface ValidationResponse {
  validation_result: ValidationResult;
}

// Dispatch-related interfaces
export interface IncidentInterpretation {
  incident_type: string;
  address: string;
  casualties?: string;
  priority: number;
  priority_level: string;
}

export interface DispatchRequest {
  interpretation: Record<string, any>;
}

export interface DispatchResult {
  incident_id: string;
  interpretation: Record<string, any>;
  resources: string[];
  units: string[];
  estimated_response_time: number;
  message: string;
}

export interface DispatchResponse {
  dispatch_result: DispatchResult;
}

export interface AvailableUnitsResponse {
  units: Record<string, string[]>;
}

// Audio-related interfaces
export interface TextRequest {
  text: string;
}

export interface ProcessAudioResult {
  transcript: string;
  confidence: number;
  duration_seconds?: number;
  speakers_detected?: number;
}

export interface SimulationResult {
  transcript: string;
  simulated: boolean;
}

export interface AudioResponse {
  result: Record<string, any>;
}

// Generic API response interface
export interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  meta: Record<string, any>;
} 