/**
 * Hook for managing map markers
 */

import { useState, useCallback } from 'react';
import type { MarkerData, LatLngCoordinate, NormalizedCoordinate, MapBounds } from '../types';
import { MarkerType } from '../types';
import { normalizeCoordinates } from '../utils/coordinates';
import { config } from '../config';

interface UseMarkersReturn {
  startMarker: MarkerData | null;
  endMarker: MarkerData | null;
  setStartMarker: (
    position: LatLngCoordinate,
    bounds: MapBounds,
    adjustedPosition?: LatLngCoordinate,
    adjustedNormalized?: NormalizedCoordinate
  ) => NormalizedCoordinate;
  setEndMarker: (
    position: LatLngCoordinate,
    bounds: MapBounds,
    adjustedPosition?: LatLngCoordinate,
    adjustedNormalized?: NormalizedCoordinate
  ) => NormalizedCoordinate;
  clearMarkers: () => void;
  hasStartMarker: boolean;
  hasEndMarker: boolean;
}

export function useMarkers(): UseMarkersReturn {
  const [startMarker, setStartMarkerState] = useState<MarkerData | null>(null);
  const [endMarker, setEndMarkerState] = useState<MarkerData | null>(null);

  const setStartMarker = useCallback(
    (
      position: LatLngCoordinate,
      bounds: MapBounds,
      adjustedPosition?: LatLngCoordinate,
      adjustedNormalized?: NormalizedCoordinate
    ) => {
      const normalized = normalizeCoordinates(position, bounds);

      const markerData: MarkerData = {
        type: MarkerType.START,
        position,
        normalized,
        adjustedPosition,
        adjustedNormalized,
        wasAdjusted: !!adjustedPosition,
      };

      setStartMarkerState(markerData);

      if (config.debug) {
        console.log('Start marker set:', markerData);
      }

      return normalized;
    },
    []
  );

  const setEndMarker = useCallback(
    (
      position: LatLngCoordinate,
      bounds: MapBounds,
      adjustedPosition?: LatLngCoordinate,
      adjustedNormalized?: NormalizedCoordinate
    ) => {
      const normalized = normalizeCoordinates(position, bounds);

      const markerData: MarkerData = {
        type: MarkerType.END,
        position,
        normalized,
        adjustedPosition,
        adjustedNormalized,
        wasAdjusted: !!adjustedPosition,
      };

      setEndMarkerState(markerData);

      if (config.debug) {
        console.log('End marker set:', markerData);
      }

      return normalized;
    },
    []
  );

  const clearMarkers = useCallback(() => {
    setStartMarkerState(null);
    setEndMarkerState(null);

    if (config.debug) {
      console.log('Markers cleared');
    }
  }, []);

  return {
    startMarker,
    endMarker,
    setStartMarker,
    setEndMarker,
    clearMarkers,
    hasStartMarker: !!startMarker,
    hasEndMarker: !!endMarker,
  };
}
