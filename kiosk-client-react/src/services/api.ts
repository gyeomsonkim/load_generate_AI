/**
 * API Service Layer
 */

import type {
  MapData,
  MapsListResponse,
  PathfindingRequest,
  PathfindingResponse,
  NormalizedCoordinate,
} from '../types';
import { API, config } from '../config';

class ApiService {
  /**
   * Fetch all maps
   */
  async getMaps(): Promise<MapsListResponse> {
    try {
      const response = await fetch(API.maps.list());

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const maps = await response.json();

      if (config.debug) {
        console.log('Maps loaded:', maps);
      }

      return maps;
    } catch (error) {
      console.error('Failed to fetch maps:', error);
      throw error;
    }
  }

  /**
   * Fetch specific map
   */
  async getMap(mapId: string): Promise<MapData> {
    try {
      const response = await fetch(API.maps.get(mapId));

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const map = await response.json();

      if (config.debug) {
        console.log('Map loaded:', map);
      }

      return map;
    } catch (error) {
      console.error('Failed to fetch map:', error);
      throw error;
    }
  }

  /**
   * Find route between two points
   */
  async findRoute(
    mapId: string,
    start: NormalizedCoordinate,
    end: NormalizedCoordinate
  ): Promise<PathfindingResponse> {
    try {
      if (config.debug) {
        console.log('Finding route:', { mapId, start, end });
      }

      const requestBody: PathfindingRequest = {
        map_id: mapId,
        start,
        end,
        options: {},
      };

      const response = await fetch(API.pathfinding.route(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (config.debug) {
        console.log('Route found:', result);
      }

      return result;
    } catch (error) {
      console.error('Failed to find route:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();
