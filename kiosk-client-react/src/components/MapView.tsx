/**
 * Map View Component with Leaflet
 */

import React, { useEffect, useRef, useMemo } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type {
  MapData,
  MarkerData,
  PathfindingResponse,
  LatLngCoordinate,
  MapBounds,
} from '../types';
import { calculateMapBounds, denormalizeCoordinates } from '../utils/coordinates';
import { config } from '../config';
import '../styles/MapView.css';

interface MapViewProps {
  mapData: MapData;
  startMarker: MarkerData | null;
  endMarker: MarkerData | null;
  route: PathfindingResponse | null;
  onMapClick: (latlng: LatLngCoordinate, bounds: MapBounds) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  mapData,
  startMarker,
  endMarker,
  route,
  onMapClick,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const imageOverlayRef = useRef<L.ImageOverlay | null>(null);
  const startMarkerRef = useRef<L.Marker | null>(null);
  const endMarkerRef = useRef<L.Marker | null>(null);
  const startOriginalMarkerRef = useRef<L.CircleMarker | null>(null);
  const endOriginalMarkerRef = useRef<L.CircleMarker | null>(null);
  const startAdjustmentLineRef = useRef<L.Polyline | null>(null);
  const endAdjustmentLineRef = useRef<L.Polyline | null>(null);
  const routeLineRef = useRef<L.Polyline | null>(null);

  // Calculate map bounds based on image dimensions
  const bounds = useMemo(
    () => calculateMapBounds(mapData.width, mapData.height),
    [mapData.width, mapData.height]
  );

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      crs: L.CRS.Simple,
      minZoom: config.mapConfig.minZoom,
      maxZoom: config.mapConfig.maxZoom,
      zoomControl: false,
      attributionControl: false,
      dragging: true,
      touchZoom: true,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: false,
    });

    // Load image overlay - use original image for user display
    const imageUrl = mapData.original_image_url || mapData.processed_image_url;
    if (imageUrl) {
      const overlay = L.imageOverlay(imageUrl, [bounds.min, bounds.max]);
      overlay.addTo(map);
      imageOverlayRef.current = overlay;
    }

    // Fit bounds
    map.fitBounds([bounds.min, bounds.max]);
    map.setMaxBounds([
      [bounds.min[0] - 0.1, bounds.min[1] - 0.1],
      [bounds.max[0] + 0.1, bounds.max[1] + 0.1],
    ]);

    // Add click handler
    map.on('click', (e: L.LeafletMouseEvent) => {
      const latlng: LatLngCoordinate = [e.latlng.lat, e.latlng.lng];
      onMapClick(latlng, bounds);
    });

    mapInstanceRef.current = map;

    if (config.debug) {
      console.log('Map initialized with bounds:', bounds);
    }

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [mapData, bounds, onMapClick]);

  // Update start marker
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove old markers and lines
    if (startMarkerRef.current) {
      map.removeLayer(startMarkerRef.current);
      startMarkerRef.current = null;
    }
    if (startOriginalMarkerRef.current) {
      map.removeLayer(startOriginalMarkerRef.current);
      startOriginalMarkerRef.current = null;
    }
    if (startAdjustmentLineRef.current) {
      map.removeLayer(startAdjustmentLineRef.current);
      startAdjustmentLineRef.current = null;
    }

    // Add new marker
    if (startMarker) {
      const actualPosition = startMarker.adjustedPosition || startMarker.position;

      const icon = L.divIcon({
        html: `<div class="custom-marker marker-start${startMarker.wasAdjusted ? ' marker-adjusted' : ''}"></div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const marker = L.marker(actualPosition, { icon });
      marker.addTo(map);
      startMarkerRef.current = marker;

      // If coordinate was adjusted, show original click location
      if (startMarker.wasAdjusted && startMarker.position) {
        // Original click position (semi-transparent circle)
        const originalMarker = L.circleMarker(startMarker.position, {
          radius: 8,
          fillColor: '#4CAF50',
          fillOpacity: 0.3,
          color: '#4CAF50',
          weight: 2,
          opacity: 0.5,
          dashArray: '5, 5',
        });
        originalMarker.addTo(map);
        startOriginalMarkerRef.current = originalMarker;

        // Line connecting original to adjusted
        const line = L.polyline([startMarker.position, actualPosition], {
          color: '#4CAF50',
          weight: 2,
          opacity: 0.5,
          dashArray: '5, 5',
        });
        line.addTo(map);
        startAdjustmentLineRef.current = line;
      }

      if (config.debug) {
        console.log('Start marker added:', actualPosition, startMarker.wasAdjusted ? '(adjusted)' : '');
      }
    }
  }, [startMarker]);

  // Update end marker
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove old markers and lines
    if (endMarkerRef.current) {
      map.removeLayer(endMarkerRef.current);
      endMarkerRef.current = null;
    }
    if (endOriginalMarkerRef.current) {
      map.removeLayer(endOriginalMarkerRef.current);
      endOriginalMarkerRef.current = null;
    }
    if (endAdjustmentLineRef.current) {
      map.removeLayer(endAdjustmentLineRef.current);
      endAdjustmentLineRef.current = null;
    }

    // Add new marker
    if (endMarker) {
      const actualPosition = endMarker.adjustedPosition || endMarker.position;

      const icon = L.divIcon({
        html: `<div class="custom-marker marker-end${endMarker.wasAdjusted ? ' marker-adjusted' : ''}"></div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const marker = L.marker(actualPosition, { icon });
      marker.addTo(map);
      endMarkerRef.current = marker;

      // If coordinate was adjusted, show original click location
      if (endMarker.wasAdjusted && endMarker.position) {
        // Original click position (semi-transparent circle)
        const originalMarker = L.circleMarker(endMarker.position, {
          radius: 8,
          fillColor: '#F44336',
          fillOpacity: 0.3,
          color: '#F44336',
          weight: 2,
          opacity: 0.5,
          dashArray: '5, 5',
        });
        originalMarker.addTo(map);
        endOriginalMarkerRef.current = originalMarker;

        // Line connecting original to adjusted
        const line = L.polyline([endMarker.position, actualPosition], {
          color: '#F44336',
          weight: 2,
          opacity: 0.5,
          dashArray: '5, 5',
        });
        line.addTo(map);
        endAdjustmentLineRef.current = line;
      }

      if (config.debug) {
        console.log('End marker added:', actualPosition, endMarker.wasAdjusted ? '(adjusted)' : '');
      }
    }
  }, [endMarker]);

  // Update route polyline
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove old route
    if (routeLineRef.current) {
      map.removeLayer(routeLineRef.current);
      routeLineRef.current = null;
    }

    // Add new route
    if (route && route.polyline.length > 0) {
      const latlngs = route.polyline.map((coord) =>
        denormalizeCoordinates(coord, bounds)
      );

      const polyline = L.polyline(latlngs, {
        color: config.routeStyle.color,
        weight: config.routeStyle.weight,
        opacity: config.routeStyle.opacity,
        smoothFactor: config.routeStyle.smoothFactor,
      });

      polyline.addTo(map);
      routeLineRef.current = polyline;

      if (config.debug) {
        console.log('Route drawn with', route.polyline.length, 'points');
      }
    }
  }, [route, bounds]);

  return <div ref={mapContainerRef} className="map-container"></div>;
};
