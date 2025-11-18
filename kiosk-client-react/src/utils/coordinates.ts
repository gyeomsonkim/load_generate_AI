/**
 * Coordinate transformation utilities
 */

import type { NormalizedCoordinate, LatLngCoordinate, MapBounds } from '../types';

/**
 * Convert map click coordinates to normalized (0-1) coordinates
 */
export function normalizeCoordinates(
  latlng: LatLngCoordinate,
  bounds: MapBounds
): NormalizedCoordinate {
  const [lat, lng] = latlng;
  const [[minLat, minLng], [maxLat, maxLng]] = [bounds.min, bounds.max];

  const x = (lng - minLng) / (maxLng - minLng);
  const y = (lat - minLat) / (maxLat - minLat);

  // Clamp to 0-1 range and invert Y axis
  const normalizedX = Math.max(0, Math.min(1, x));
  const normalizedY = Math.max(0, Math.min(1, 1 - y));

  return [normalizedX, normalizedY];
}

/**
 * Convert normalized coordinates to map coordinates
 */
export function denormalizeCoordinates(
  normalized: NormalizedCoordinate,
  bounds: MapBounds
): LatLngCoordinate {
  const [x, y] = normalized;
  const [[minLat, minLng], [maxLat, maxLng]] = [bounds.min, bounds.max];

  const lng = minLng + x * (maxLng - minLng);
  const lat = minLat + (1 - y) * (maxLat - minLat);

  return [lat, lng];
}

/**
 * Calculate map bounds based on image dimensions
 * Uses actual pixel dimensions for Leaflet CRS.Simple
 */
export function calculateMapBounds(width: number, height: number): MapBounds {
  // Leaflet CRS.Simple expects pixel coordinates
  // [lat, lng] corresponds to [y, x] in image coordinates
  return {
    min: [0, 0],
    max: [height, width],
  };
}
