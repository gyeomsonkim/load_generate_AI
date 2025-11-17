/**
 * Loading Overlay Component
 */

import React from 'react';
import '../styles/LoadingOverlay.css';

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isVisible,
  message = '경로를 찾는 중...',
}) => {
  if (!isVisible) return null;

  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
};
