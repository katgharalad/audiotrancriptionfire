'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { InterpretationResult } from '@/types/api';

// Define types for our application state
type Incident = {
  id: string;
  interpretation: InterpretationResult;
  timestamp: string;
  status: 'pending' | 'processing' | 'verified' | 'dispatched';
};

type AppState = {
  incidents: Incident[];
  selectedIncidentId: string | null;
  isLoading: boolean;
  error: string | null;
  user: {
    id: string;
    name: string;
    role: string;
  } | null;
};

// Define action types
type ActionType =
  | { type: 'SET_INCIDENTS'; payload: Incident[] }
  | { type: 'ADD_INCIDENT'; payload: Incident }
  | { type: 'UPDATE_INCIDENT'; payload: { id: string; data: Partial<Incident> } }
  | { type: 'DELETE_INCIDENT'; payload: string }
  | { type: 'SELECT_INCIDENT'; payload: string | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_USER'; payload: AppState['user'] }
  | { type: 'LOGOUT' };

// Initial state
const initialState: AppState = {
  incidents: [],
  selectedIncidentId: null,
  isLoading: false,
  error: null,
  user: {
    id: '123',
    name: 'Test Dispatcher',
    role: 'dispatcher',
  },
};

// Sample incidents for testing
const sampleIncidents: Incident[] = [
  {
    id: '1a2b3c4d5e6f7g8h',
    interpretation: {
      incident_type: 'Structure Fire',
      incident_type_confidence: 0.95,
      address: '123 Main Street, Anytown, DE',
      address_validation: { address_validity: true },
      casualties: 'Two people trapped on the second floor',
      casualties_confidence: 0.85,
      casualties_structured: { trapped: true, injured: false },
      priority: 1,
      priority_level: 'High',
      needs_verification: false,
    } as InterpretationResult,
    timestamp: '2023-04-05T12:30:45',
    status: 'dispatched',
  },
  {
    id: '2b3c4d5e6f7g8h9i',
    interpretation: {
      incident_type: 'Medical Emergency',
      incident_type_confidence: 0.88,
      address: '456 Oak Avenue, Anytown, DE',
      address_validation: { address_validity: true },
      casualties: 'Elderly person experiencing chest pain',
      casualties_confidence: 0.92,
      casualties_structured: { trapped: false, injured: true },
      priority: 2,
      priority_level: 'Medium',
      needs_verification: true,
    } as InterpretationResult,
    timestamp: '2023-04-05T13:15:20',
    status: 'processing',
  },
  {
    id: '3c4d5e6f7g8h9i0j',
    interpretation: {
      incident_type: 'Traffic Accident',
      incident_type_confidence: 0.75,
      address: 'Intersection of Main St and 5th Ave, Anytown, DE',
      address_validation: { address_validity: false, needs_verification: true },
      casualties: 'No apparent injuries reported',
      casualties_confidence: 0.65,
      casualties_structured: { trapped: false, injured: false },
      priority: 3,
      priority_level: 'Low',
      needs_verification: true,
    } as InterpretationResult,
    timestamp: '2023-04-05T14:05:10',
    status: 'pending',
  },
];

// Create the context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<ActionType>;
}>({
  state: initialState,
  dispatch: () => null,
});

// Reducer function to handle state changes
const appReducer = (state: AppState, action: ActionType): AppState => {
  switch (action.type) {
    case 'SET_INCIDENTS':
      return {
        ...state,
        incidents: action.payload,
      };
    case 'ADD_INCIDENT':
      return {
        ...state,
        incidents: [...state.incidents, action.payload],
      };
    case 'UPDATE_INCIDENT':
      return {
        ...state,
        incidents: state.incidents.map(incident =>
          incident.id === action.payload.id
            ? { ...incident, ...action.payload.data }
            : incident
        ),
      };
    case 'DELETE_INCIDENT':
      return {
        ...state,
        incidents: state.incidents.filter(incident => incident.id !== action.payload),
      };
    case 'SELECT_INCIDENT':
      return {
        ...state,
        selectedIncidentId: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
      };
    default:
      return state;
  }
};

// Context provider component
export const AppContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Load sample incidents on first render (would be an API call in a real app)
  useEffect(() => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    // Simulate API call delay
    setTimeout(() => {
      dispatch({ type: 'SET_INCIDENTS', payload: sampleIncidents });
      dispatch({ type: 'SET_LOADING', payload: false });
    }, 1000);
  }, []);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the app context
export const useAppContext = () => useContext(AppContext);

export default AppContext; 