/**
 * Status Bar Component
 */

import React from 'react';
import '../styles/StatusBar.css';

interface StatusBarProps {
  instruction: string;
  showResetButton: boolean;
  onReset: () => void;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  instruction,
  showResetButton,
  onReset,
}) => {
  return (
    <div className="status-bar">
      <div className="instruction">{instruction}</div>
      {showResetButton && (
        <button className="reset-btn" onClick={onReset}>
          다시 시작
        </button>
      )}
    </div>
  );
};
