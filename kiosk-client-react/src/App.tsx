/**
 * Main Application Component
 */

import { useState, useCallback } from 'react';
import type { LatLngCoordinate, MapBounds } from './types';
import { StatusBar } from './components/StatusBar';
import { LoadingOverlay } from './components/LoadingOverlay';
import { MapView } from './components/MapView';
import { useMapData } from './hooks/useMapData';
import { useMarkers } from './hooks/useMarkers';
import { usePathfinding } from './hooks/usePathfinding';
import { denormalizeCoordinates, normalizeCoordinates } from './utils/coordinates';
import { apiService } from './services/api';
import { config } from './config';
import './styles/App.css';

function App() {
  const { mapData, isLoading: mapLoading, error: mapError } = useMapData();
  const {
    startMarker,
    endMarker,
    setStartMarker,
    setEndMarker,
    clearMarkers,
    hasStartMarker,
    hasEndMarker,
  } = useMarkers();
  const { route, isProcessing, findRoute, clearRoute } = usePathfinding();

  const [instruction, setInstruction] = useState('지도를 터치하여 출발지를 선택하세요');

  // Handle map click
  const handleMapClick = useCallback(
    async (latlng: LatLngCoordinate, bounds: MapBounds) => {
      if (isProcessing) {
        if (config.debug) console.log('Processing... click ignored');
        return;
      }

      if (!mapData) {
        console.error('Map data not loaded');
        return;
      }

      if (!hasStartMarker) {
        // First click: validate and set start marker
        setInstruction('출발지 확인 중...');

        try {
          const normalized = normalizeCoordinates(latlng, bounds);
          const validation = await apiService.validatePoint(mapData.id, normalized);

          if (validation.was_adjusted) {
            // Coordinate was adjusted - show both original and adjusted
            const adjustedLatLng = denormalizeCoordinates(validation.adjusted_point, bounds);
            setStartMarker(latlng, bounds, adjustedLatLng, validation.adjusted_point);
            setInstruction(`출발지 설정 완료 (${validation.adjustment_distance?.toFixed(0)}px 보정) - 도착지를 선택하세요`);
          } else {
            // Valid point - use as-is
            setStartMarker(latlng, bounds);
            setInstruction('도착지를 선택하세요');
          }
        } catch (error) {
          console.error('Failed to validate start point:', error);
          setInstruction('출발지를 설정할 수 없습니다. 다시 선택해주세요.');
          setTimeout(() => setInstruction('지도를 터치하여 출발지를 선택하세요'), 2000);
        }
      } else if (!hasEndMarker) {
        // Second click: validate end point and find route
        setInstruction('도착지 확인 중...');

        try {
          const normalized = normalizeCoordinates(latlng, bounds);
          const validation = await apiService.validatePoint(mapData.id, normalized);

          let endNormalized = normalized;
          let endLatLng = latlng;

          if (validation.was_adjusted) {
            // Coordinate was adjusted
            endNormalized = validation.adjusted_point;
            endLatLng = denormalizeCoordinates(validation.adjusted_point, bounds);
            setEndMarker(latlng, bounds, endLatLng, validation.adjusted_point);
          } else {
            // Valid point
            setEndMarker(latlng, bounds);
          }

          // Find route with validated coordinates
          setInstruction('경로를 찾는 중...');
          const routeResult = await findRoute(
            mapData.id,
            startMarker!.adjustedNormalized || startMarker!.normalized,
            endNormalized
          );

          // Build success message
          const distance = routeResult.metadata.distance_meters.toFixed(1);
          const time = Math.ceil(routeResult.metadata.estimated_time_seconds / 60);
          let message = `경로 표시 완료 (거리: ${distance}m, 예상 시간: ${time}분)`;

          if (startMarker!.wasAdjusted || validation.was_adjusted) {
            message += ' - 좌표 보정됨';
          }

          setInstruction(message);
        } catch (error) {
          console.error('Failed to find route:', error);
          // Error - reset and show message
          clearMarkers();
          setInstruction('경로를 찾을 수 없습니다. 다시 시도해주세요.');

          setTimeout(() => {
            setInstruction('지도를 터치하여 출발지를 선택하세요');
          }, 3000);
        }
      } else {
        // Route already exists - ignore
        if (config.debug) console.log('Route exists. Use reset button.');
      }
    },
    [
      isProcessing,
      mapData,
      hasStartMarker,
      hasEndMarker,
      startMarker,
      setStartMarker,
      setEndMarker,
      findRoute,
      clearMarkers,
    ]
  );

  // Handle reset
  const handleReset = useCallback(() => {
    clearMarkers();
    clearRoute();
    setInstruction('지도를 터치하여 출발지를 선택하세요');

    if (config.debug) {
      console.log('Application reset');
    }
  }, [clearMarkers, clearRoute]);

  // Loading state
  if (mapLoading) {
    return <LoadingOverlay isVisible={true} message="지도를 불러오는 중..." />;
  }

  // Error state
  if (mapError || !mapData) {
    return (
      <div className="error-container">
        <h2>오류 발생</h2>
        <p>{mapError || '지도를 불러올 수 없습니다'}</p>
        <button onClick={() => window.location.reload()}>새로고침</button>
      </div>
    );
  }

  return (
    <div className="app">
      <StatusBar
        instruction={instruction}
        showResetButton={hasEndMarker && !!route}
        onReset={handleReset}
      />

      <MapView
        mapData={mapData}
        startMarker={startMarker}
        endMarker={endMarker}
        route={route}
        onMapClick={handleMapClick}
      />

      <LoadingOverlay isVisible={isProcessing} message="경로를 찾는 중..." />
    </div>
  );
}

export default App;
