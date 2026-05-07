import React from 'react';
import './Loader.css';

const Loader = ({ message = "Loading..." }) => {
  return (
    <div className="loader-overlay">
      <div className="loader-spinner"></div>
      <div className="loader-text">{message}</div>
    </div>
  );
};

export default Loader;
