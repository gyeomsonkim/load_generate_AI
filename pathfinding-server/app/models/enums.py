"""
Enum definitions for the application
"""
from enum import Enum


class MapType(str, Enum):
    PARK = "park"
    SCHOOL = "school"
    CAMPUS = "campus"
    BUILDING = "building"
    MALL = "mall"
    HOSPITAL = "hospital"
    AIRPORT = "airport"
    OTHER = "other"


class MapStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    READY = "ready"


class PathDifficulty(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class ObstacleType(str, Enum):
    WALL = "wall"
    WATER = "water"
    BUILDING = "building"
    RESTRICTED = "restricted"
    STAIRS = "stairs"
    ELEVATION = "elevation"
    VEGETATION = "vegetation"


class PathfindingAlgorithm(str, Enum):
    ASTAR = "astar"
    DIJKSTRA = "dijkstra"
    BFS = "bfs"
    CUSTOM_ML = "custom_ml"