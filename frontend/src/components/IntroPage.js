import React from 'react';
import { useNavigate } from 'react-router-dom';
import './IntroPage.css';

const IntroPage = () => {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate('/upload');
  };

  return (
    <div className="intro-page">
      <div className="intro-background">
        <div className="gradient-overlay"></div>
        <div className="animated-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>
      
      <div className="intro-content">
        <div className="container">
          <div className="row justify-content-center align-items-center min-vh-100">
            <div className="col-lg-8 col-md-10 text-center">
              <div className="intro-card">
                <div className="logo-container">
                  <img
                    className="logo-image"
                    src="https://ik.imagekit.io/pep5hasnd/image/ChatGPT_Image_Jan_23..._imresizer-removebg-preview.png"
                    alt="QuestGen AI"
                  />
                </div>
                
                <h1 className="intro-title">
                  <span className="title-main">QuestGen</span>
                  <span className="title-ai">AI</span>
                </h1>
                
                <p className="intro-subtitle">
                  AI-Powered Question Paper Generation & CO-PO Mapping System
                </p>
                
                <div className="intro-description">
                  <p>
                    Transform your exam preparation process with cutting-edge artificial intelligence. 
                    QuestGen AI automates the creation of comprehensive question papers while ensuring 
                    proper Course Outcome (CO) and Program Outcome (PO) mapping.
                  </p>
                  <div className="features-list">
                    <div className="feature-item">
                      <i className="feature-icon">✨</i>
                      <span>Intelligent Question Generation</span>
                    </div>
                    <div className="feature-item">
                      <i className="feature-icon">🎯</i>
                      <span>Automated CO-PO Mapping</span>
                    </div>
                    <div className="feature-item">
                      <i className="feature-icon">⚡</i>
                      <span>Fast & Efficient Processing</span>
                    </div>
                  </div>
                </div>
                
                <button 
                  className="btn-start"
                  onClick={handleStart}
                >
                  <span className="btn-text">Get Started</span>
                  <span className="btn-arrow">→</span>
                </button>
                
                <p className="intro-footer">
                  Powered by Advanced AI Technology
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntroPage;

