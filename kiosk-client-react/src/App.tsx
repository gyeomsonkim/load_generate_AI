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
        // First click: set start marker
        setStartMarker(latlng, bounds);
        setInstruction('도착지를 선택하세요');
      } else if (!hasEndMarker) {
        // Second click: set end marker and find route
        const endNormalized = setEndMarker(latlng, bounds);
        setInstruction('경로를 찾는 중...');

        try {
          await findRoute(mapData.id, startMarker!.normalized, endNormalized);

          // Success - update instruction with route info
          if (route) {
            const distance = route.metadata.distance_meters.toFixed(1);
            const time = Math.ceil(route.metadata.estimated_time_seconds / 60);
            setInstruction(`경로 표시 완료 (거리: ${distance}m, 예상 시간: ${time}분)`);
          }
        } catch (error) {
          // Error - reset end marker and show message
          clearMarkers();
          setStartMarker(latlng, bounds);
          setInstruction('경로를 찾을 수 없습니다. 다시 시도해주세요.');

          setTimeout(() => {
            setInstruction('도착지를 다시 선택하세요');
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
      route,
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
