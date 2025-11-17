/**
 * Hook for managing map data
 */

import { useState, useEffect } from 'react';
import type { MapData } from '../types';
import { MapStatus } from '../types';
import { apiService } from '../services/api';
import { config } from '../config';

interface UseMapDataReturn {
  mapData: MapData | null;
  isLoading: boolean;
  error: string | null;
}

export function useMapData(): UseMapDataReturn {
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMap() {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch all maps
        const maps = await apiService.getMaps();

        if (!maps || maps.length === 0) {
          throw new Error('사용 가능한 지도가 없습니다');
        }

        // Find first processed map
        const processedMap = maps.find(
          (m) => m.preprocessing_status === MapStatus.PROCESSED
        );

        if (!processedMap) {
          throw new Error('처리된 지도가 없습니다. 지도를 먼저 업로드하고 전처리하세요.');
        }

        // Update global config
        config.defaultMapId = processedMap.id;

        setMapData(processedMap);

        if (config.debug) {
          console.log('Map data loaded:', processedMap);
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : '지도를 불러오는데 실패했습니다';
        setError(message);
        console.error('Failed to load map:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadMap();
  }, []);

  return { mapData, isLoading, error };
}
