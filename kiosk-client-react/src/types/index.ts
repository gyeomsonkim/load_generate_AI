/**
 * TypeScript Type Definitions
 */

// ===== Map Types =====
export interface MapData {
  id: string;
  name: string;
  description: string | null;
  map_type: string;
  width: number;
  height: number;
  scale_meters_per_pixel: number;
  preprocessing_status: MapStatus;
  original_image_url: string | null;
  processed_image_url: string | null;
  thumbnail_url?: string | null;
  created_at: string;
  updated_at: string;
}

export type MapStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

export const MapStatus = {
  UPLOADED: 'uploaded' as const,
  PROCESSING: 'processing' as const,
  PROCESSED: 'processed' as const,
  FAILED: 'failed' as const,
};

// ===== Coordinate Types =====
export type NormalizedCoordinate = [number, number]; // [x, y] in 0-1 range
export type LatLngCoordinate = [number, number]; // [lat, lng] for Leaflet

export interface MapBounds {
  min: LatLngCoordinate;
  max: LatLngCoordinate;
}

// ===== Pathfinding Types =====
export interface PathfindingRequest {
  map_id: string;
  start: NormalizedCoordinate;
  end: NormalizedCoordinate;
  options?: Record<string, unknown>;
}

export interface PathMetadata {
  distance_pixels: number;
  distance_meters: number;
  estimated_time_seconds: number;
  difficulty: PathDifficulty;
  accessibility_score: number;
  turn_count: number;
}

export type PathDifficulty = 'easy' | 'moderate' | 'hard';

export const PathDifficulty = {
  EASY: 'easy' as const,
  MODERATE: 'moderate' as const,
  HARD: 'hard' as const,
};

export interface PathfindingResponse {
  path_id: string;
  map_id: string;
  polyline: NormalizedCoordinate[];
  svg_path: string;
  metadata: PathMetadata;
  alternatives?: PathfindingResponse[];
  cached: boolean;
  processing_time: number;
}

export interface ValidatePointRequest {
  map_id: string;
  point: NormalizedCoordinate;
}

export interface ValidatePointResponse {
  is_valid: boolean;
  original_point: NormalizedCoordinate;
  adjusted_point: NormalizedCoordinate;
  was_adjusted: boolean;
  adjustment_distance: number | null;
}

// ===== Marker Types =====
export type MarkerType = 'start' | 'end';

export const MarkerType = {
  START: 'start' as const,
  END: 'end' as const,
};

export interface MarkerData {
  type: MarkerType;
  position: LatLngCoordinate;
  normalized: NormalizedCoordinate;
  // Coordinates adjusted by backend (if different from original click)
  adjustedPosition?: LatLngCoordinate;
  adjustedNormalized?: NormalizedCoordinate;
  wasAdjusted?: boolean;
}

// ===== Application State =====
export interface AppState {
  currentMap: MapData | null;
  startMarker: MarkerData | null;
  endMarker: MarkerData | null;
  route: PathfindingResponse | null;
  isLoading: boolean;
  error: string | null;
  instruction: string;
}

// ===== API Response Types =====
export interface ApiError {
  detail: string;
}

export interface MapsListResponse extends Array<MapData> {}

// ===== Configuration Types =====
export interface AppConfig {
  apiBaseUrl: string;
  apiPrefix: string;
  defaultMapId: string | null;
  mapConfig: {
    minZoom: number;
    maxZoom: number;
  };
  markers: {
    start: {
      color: string;
      label: string;
    };
    end: {
      color: string;
      label: string;
    };
  };
  routeStyle: {
    color: string;
    weight: number;
    opacity: number;
    smoothFactor: number;
  };
  debug: boolean;
}
