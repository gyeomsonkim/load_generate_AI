/**
 * Hook for pathfinding operations
 */

import { useState, useCallback } from 'react';
import type { PathfindingResponse, NormalizedCoordinate } from '../types';
import { apiService } from '../services/api';
import { config } from '../config';

interface UsePathfindingReturn {
  route: PathfindingResponse | null;
  isProcessing: boolean;
  error: string | null;
  findRoute: (mapId: string, start: NormalizedCoordinate, end: NormalizedCoordinate) => Promise<void>;
  clearRoute: () => void;
}

export function usePathfinding(): UsePathfindingReturn {
  const [route, setRoute] = useState<PathfindingResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const findRoute = useCallback(
    async (mapId: string, start: NormalizedCoordinate, end: NormalizedCoordinate) => {
      if (isProcessing) {
        if (config.debug) console.log('Already processing, ignoring request');
        return;
      }

      setIsProcessing(true);
      setError(null);

      try {
        const result = await apiService.findRoute(mapId, start, end);
        setRoute(result);

        if (config.debug) {
          console.log('Route set:', result);
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : '경로를 찾을 수 없습니다';
        setError(message);
        console.error('Pathfinding error:', err);
        throw err; // Re-throw to allow component handling
      } finally {
        setIsProcessing(false);
      }
    },
    [isProcessing]
  );

  const clearRoute = useCallback(() => {
    setRoute(null);
    setError(null);

    if (config.debug) {
      console.log('Route cleared');
    }
  }, []);

  return {
    route,
    isProcessing,
    error,
    findRoute,
    clearRoute,
  };
}
