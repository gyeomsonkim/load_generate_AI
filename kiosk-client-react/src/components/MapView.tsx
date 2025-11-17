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
  const routeLineRef = useRef<L.Polyline | null>(null);

  useEffect(() => {
    console.log('mapData---------', mapData);
  }, [mapData]);

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

    // Load image overlay
    const imageUrl = mapData.processed_image_url || mapData.original_image_url;
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

    // Remove old marker
    if (startMarkerRef.current) {
      map.removeLayer(startMarkerRef.current);
      startMarkerRef.current = null;
    }

    // Add new marker
    if (startMarker) {
      const icon = L.divIcon({
        html: `<div class="custom-marker marker-start"></div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const marker = L.marker(startMarker.position, { icon });
      marker.addTo(map);
      startMarkerRef.current = marker;

      if (config.debug) {
        console.log('Start marker added:', startMarker.position);
      }
    }
  }, [startMarker]);

  // Update end marker
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Remove old marker
    if (endMarkerRef.current) {
      map.removeLayer(endMarkerRef.current);
      endMarkerRef.current = null;
    }

    // Add new marker
    if (endMarker) {
      const icon = L.divIcon({
        html: `<div class="custom-marker marker-end"></div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const marker = L.marker(endMarker.position, { icon });
      marker.addTo(map);
      endMarkerRef.current = marker;

      if (config.debug) {
        console.log('End marker added:', endMarker.position);
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
