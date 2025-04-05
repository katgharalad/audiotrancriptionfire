import { useEffect, useRef, useState, useCallback } from 'react';
import { useAppContext } from '@/contexts/AppContext';

// Enum for WebSocket connection status
export enum WebSocketStatus {
  CONNECTING = 'connecting',
  OPEN = 'open',
  CLOSED = 'closed',
  ERROR = 'error'
}

// WebSocket message types
export type WebSocketMessage = {
  type: 'incident_created' | 'incident_updated' | 'incident_deleted' | 'dispatch_update' | 'system_message';
  payload: any;
  timestamp: string;
};

/**
 * Hook for managing WebSocket connection
 * @param url WebSocket URL
 * @returns WebSocket status and methods
 */
export function useWebSocket(url: string = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws') {
  const { dispatch } = useAppContext();
  const socket = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<WebSocketStatus>(WebSocketStatus.CLOSED);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;
  
  // Connect to WebSocket
  const connect = useCallback(() => {
    if (socket.current?.readyState === WebSocket.OPEN) return;
    
    try {
      setStatus(WebSocketStatus.CONNECTING);
      socket.current = new WebSocket(url);
      
      socket.current.onopen = () => {
        console.log('WebSocket connected');
        setStatus(WebSocketStatus.OPEN);
        setReconnectAttempts(0);
      };
      
      socket.current.onclose = (event) => {
        console.log('WebSocket closed:', event);
        setStatus(WebSocketStatus.CLOSED);
        
        // Attempt to reconnect if not closed cleanly
        if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
          console.log(`Attempting to reconnect in ${timeout}ms...`);
          
          setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, timeout);
        }
      };
      
      socket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStatus(WebSocketStatus.ERROR);
      };
      
      socket.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(message);
          
          // Process incoming message based on type
          switch (message.type) {
            case 'incident_created':
              dispatch({ type: 'ADD_INCIDENT', payload: message.payload });
              break;
              
            case 'incident_updated':
              dispatch({ 
                type: 'UPDATE_INCIDENT', 
                payload: { 
                  id: message.payload.id, 
                  data: message.payload 
                } 
              });
              break;
              
            case 'incident_deleted':
              dispatch({ type: 'DELETE_INCIDENT', payload: message.payload.id });
              break;
              
            case 'dispatch_update':
              // Handle dispatch updates
              console.log('Dispatch update received:', message.payload);
              break;
              
            case 'system_message':
              console.log('System message:', message.payload);
              break;
              
            default:
              console.warn('Unknown message type:', message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setStatus(WebSocketStatus.ERROR);
    }
  }, [url, reconnectAttempts, dispatch]);
  
  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (socket.current) {
      socket.current.close();
      socket.current = null;
      setStatus(WebSocketStatus.CLOSED);
    }
  }, []);
  
  // Send message to WebSocket
  const sendMessage = useCallback((message: any) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);
  
  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  return {
    status,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
    reconnectAttempts,
  };
}

// Singleton WebSocket service (alternative to the hook for non-component code)
class WebSocketService {
  private static instance: WebSocketService;
  private socket: WebSocket | null = null;
  private url: string;
  private listeners: Map<string, ((message: WebSocketMessage) => void)[]> = new Map();
  
  private constructor(url: string = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws') {
    this.url = url;
  }
  
  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }
  
  public connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN) return;
    
    try {
      this.socket = new WebSocket(this.url);
      
      this.socket.onopen = () => {
        console.log('WebSocket service connected');
        this.notifyListeners('system', { type: 'system_message', payload: { message: 'Connected' }, timestamp: new Date().toISOString() });
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket service disconnected');
        this.notifyListeners('system', { type: 'system_message', payload: { message: 'Disconnected' }, timestamp: new Date().toISOString() });
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket service error:', error);
        this.notifyListeners('error', { type: 'system_message', payload: { message: 'Error' }, timestamp: new Date().toISOString() });
      };
      
      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          this.notifyListeners('message', message);
          this.notifyListeners(message.type, message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }
  
  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
  
  public sendMessage(message: any): boolean {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }
  
  public addListener(event: string, callback: (message: WebSocketMessage) => void): void {
    const listeners = this.listeners.get(event) || [];
    listeners.push(callback);
    this.listeners.set(event, listeners);
  }
  
  public removeListener(event: string, callback: (message: WebSocketMessage) => void): void {
    const listeners = this.listeners.get(event) || [];
    const index = listeners.indexOf(callback);
    if (index !== -1) {
      listeners.splice(index, 1);
      this.listeners.set(event, listeners);
    }
  }
  
  private notifyListeners(event: string, message: WebSocketMessage): void {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach(callback => callback(message));
  }
}

export default WebSocketService.getInstance(); 