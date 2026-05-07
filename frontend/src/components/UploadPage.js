import React, { useState } from 'react';
import { jsPDF } from 'jspdf';
import apiService from '../services/api';
import Loader from './Loader';
import QuestionGenerationLoader from './QuestionGenerationLoader';
import './UploadPage.css';
import './Loader.css';
import './QuestionGenerationLoader.css';

const UploadPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showQuestions, setShowQuestions] = useState(false);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [formData, setFormData] = useState({
    previousPapers: [],
    coPoFile: null,
    syllabusFile: null
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingQuestions, setIsGeneratingQuestions] = useState(false);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [questionPatterns, setQuestionPatterns] = useState([]);
  const [questionCounts, setQuestionCounts] = useState({});

  const totalSteps = 5;

  const handlePreviousPaperUpload = async (index, file) => {
    const newPapers = [...formData.previousPapers];
    newPapers[index] = file;
    setFormData({ ...formData, previousPapers: newPapers });
    
    setLoading(true);
    setError(null);
    try {
      await apiService.uploadPreviousPapers([...newPapers]);
      setSuccess(`File "${file.name}" uploaded successfully!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message || 'Failed to upload file');
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleRemovePreviousPaper = (index) => {
    const newPapers = [...formData.previousPapers];
    newPapers.splice(index, 1);
    setFormData({ ...formData, previousPapers: newPapers });
  };

  const handleCoPoUpload = async (file) => {
    setFormData({ ...formData, coPoFile: file });
    
    setLoading(true);
    setError(null);
    try {
      await apiService.uploadCoPo(file);
      setSuccess(`CO/PO file "${file.name}" uploaded successfully!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message || 'Failed to upload CO/PO file');
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleSyllabusUpload = async (file) => {
    setFormData({ ...formData, syllabusFile: file });
    
    setLoading(true);
    setError(null);
    try {
      await apiService.uploadSyllabus(file);
      setSuccess(`Syllabus "${file.name}" uploaded successfully!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message || 'Failed to upload syllabus');
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentStep === 4 && currentStep < totalSteps) {
      setIsAnalyzing(true);
      setError(null);
      try {
        setSuccess('Analyzing question patterns from previous papers...');
        const patternsResponse = await apiService.analyzeQuestionPatterns();
        const patterns = patternsResponse.patterns || [];
        setQuestionPatterns(patterns);
        
        const counts = {};
        patterns.forEach(pattern => {
          counts[pattern.marks] = 0;
        });
        setQuestionCounts(counts);
        
        setSuccess('Patterns analyzed successfully!');
        setTimeout(() => setSuccess(null), 2000);
        setCurrentStep(5);
      } catch (err) {
        setError(err.message || 'Failed to analyze question patterns');
        setTimeout(() => setError(null), 5000);
        return;
      } finally {
        setIsAnalyzing(false);
        setLoading(false);
      }
    } else if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleQuestionCountChange = (marks, value) => {
    if (value === '' || /^\d+$/.test(value)) {
      setQuestionCounts({
        ...questionCounts,
        [marks]: value === '' ? '' : parseInt(value, 10)
      });
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const downloadAsPDF = () => {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    const margin = 15;
    const pageWidth = doc.internal.pageSize.getWidth();
    const maxWidth = pageWidth - (margin * 2);
    let yPos = 20;
    
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(18);
    doc.text('GENERATED QUESTION PAPER', pageWidth / 2, yPos, { align: 'center' });
    yPos += 10;
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, margin, yPos);
    doc.line(margin, yPos + 3, pageWidth - margin, yPos + 3);
    yPos += 15;
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(11);
    
    generatedQuestions.forEach((q, index) => {
      const questionText = `Q${index + 1}. ${q.question_text} [${q.marks} Marks]`;
      const splitText = doc.splitTextToSize(questionText, maxWidth - 10);
      
      const questionHeight = splitText.length * 7; 
      if (yPos + questionHeight > 270) { 
        doc.addPage();
        yPos = 20;
      }
      
      doc.setFont(undefined, 'bold');
      doc.text(splitText, margin + 5, yPos);
      yPos += (splitText.length * 7) + 5;
      
      doc.setFont(undefined, 'normal');
      const coText = `COs: ${Array.isArray(q.co_mapping) ? q.co_mapping.join(', ') : q.co_mapping}`;
      doc.text(coText, margin + 10, yPos);
      yPos += 7;
      
      const metaText = `Type: ${q.question_type} | Difficulty: ${q.difficulty_level} | Topic: ${q.topic}`;
      doc.text(metaText, margin + 10, yPos);
      yPos += 10;
      
      doc.setDrawColor(200, 200, 200);
      doc.line(margin, yPos, pageWidth - margin, yPos);
      yPos += 15;
    });
    
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(10);
      doc.text(
        `Page ${i} of ${pageCount}`,
        pageWidth - margin,
        287, 
        { align: 'right' }
      );
    }
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    doc.save(`question-paper-${timestamp}.pdf`);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const questionCount = Object.values(questionCounts).reduce((sum, count) => sum + (count || 0), 0);
      setTotalQuestions(questionCount);
      
      if (questionCount === 0) {
        setError('Please specify at least one question count');
        setTimeout(() => setError(null), 5000);
        setLoading(false);
        return;
      }
      
      setIsGeneratingQuestions(true);
      
      try {
        const questionsResponse = await apiService.generateQuestions(questionCounts);
        console.log('Questions generated:', questionsResponse);
        
        if (questionsResponse && questionsResponse.questions) {
          setGeneratedQuestions(questionsResponse.questions);
          setShowQuestions(true);
          setSuccess(`Successfully generated ${questionsResponse.questions.length} questions!`);
          setTimeout(() => setSuccess(null), 3000);
        } else {
          throw new Error('No questions were generated. Please try again.');
        }
      } finally {
        setIsGeneratingQuestions(false);
      }
      
    } catch (err) {
      console.error('Error generating questions:', err);
      setError(err.message || 'Failed to generate questions. Please try again.');
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return true; 
      case 2:
        return formData.previousPapers.length >= 1; 
      case 3:
        return formData.coPoFile !== null; 
      case 4:
        return formData.syllabusFile !== null; 
      case 5:
        return Object.values(questionCounts).some(count => count > 0);
      default:
        return false;
    }
  };

  return (
    <div className="upload-page">
      {isAnalyzing && <Loader message="Analyzing question patterns. This may take a moment..." />}
      {isGeneratingQuestions && <QuestionGenerationLoader count={totalQuestions} />}
      <div className="upload-container">
        <div className="progress-section">
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            ></div>
          </div>
          <div className="step-indicators">
            {[1, 2, 3, 4, 5].map((step) => (
              <div 
                key={step} 
                className={`step-indicator ${currentStep >= step ? 'active' : ''} ${currentStep === step ? 'current' : ''}`}
              >
                <div className="step-number">{step}</div>
                <div className="step-label">
                  {step === 1 && 'Introduction'}
                  {step === 2 && 'Question Papers'}
                  {step === 3 && 'CO/PO File'}
                  {step === 4 && 'Syllabus'}
                  {step === 5 && 'Configure'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span> {error}
          </div>
        )}
        {success && (
          <div className="alert alert-success">
            <span>✓</span> {success}
          </div>
        )}

        <div className="step-content">
          {currentStep === 1 && (
            <IntroStep />
          )}
          
          {currentStep === 2 && (
            <PreviousPapersStep
              papers={formData.previousPapers}
              onUpload={handlePreviousPaperUpload}
              onRemove={handleRemovePreviousPaper}
              loading={loading}
            />
          )}
          
          {currentStep === 3 && (
            <CoPoStep
              file={formData.coPoFile}
              onUpload={handleCoPoUpload}
              loading={loading}
            />
          )}
          
          {currentStep === 4 && (
            <SyllabusStep
              file={formData.syllabusFile}
              onUpload={handleSyllabusUpload}
              loading={loading}
            />
          )}
          
          {currentStep === 5 && (
            <QuestionConfigStep
              patterns={questionPatterns}
              questionCounts={questionCounts}
              onCountChange={handleQuestionCountChange}
              loading={loading}
            />
          )}
        </div>

        <div className="navigation-buttons">
          <button
            className="btn-nav btn-previous"
            onClick={handlePrevious}
            disabled={currentStep === 1}
          >
            ← Previous
          </button>
          
          {currentStep < totalSteps ? (
            <button
              className="btn-nav btn-next"
              onClick={handleNext}
              disabled={!canProceed() || loading}
            >
              {loading ? 'Processing...' : 'Next →'}
            </button>
          ) : (
            <button
              className="btn-nav btn-submit"
              onClick={handleSubmit}
              disabled={!canProceed() || loading}
            >
              {loading ? 'Generating...' : 'Generate Questions'}
            </button>
          )}
        </div>
      </div>
      
      {showQuestions && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Generated Questions</h2>
              <button 
                className="close-button" 
                onClick={() => setShowQuestions(false)}
                disabled={loading}
              >
                ×
              </button>
            </div>
            <div className="questions-container">
              {generatedQuestions.map((q, index) => (
                <div key={index} className="question-card">
                  <div className="question-header">
                    <span className="question-number">Q{index + 1}.</span>
                    <span className="question-marks">[{q.marks} marks]</span>
                    <span className="question-type">{q.question_type}</span>
                    <span className="question-difficulty">({q.difficulty_level})</span>
                    <button 
                      className={`copy-button ${copiedIndex === index ? 'copied' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(q.question_text, index);
                      }}
                      title="Copy question"
                    >
                      {copiedIndex === index ? '✓' : '⎘'}
                    </button>
                  </div>
                  <div className="question-text">{q.question_text}</div>
                  <div className="question-meta">
                    <span className="question-topic">Topic: {q.topic}</span>
                    <span className="question-co">COs: {Array.isArray(q.co_mapping) ? q.co_mapping.join(', ') : q.co_mapping}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="modal-actions">
              <button 
                className="btn-primary"
                onClick={downloadAsPDF}
              >
                Download as PDF
              </button>
              <button 
                className="btn-secondary"
                onClick={() => setShowQuestions(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const IntroStep = () => {
  return (
    <div className="step-card">
      <div className="step-header">
        <h2>Welcome to QuestGen AI</h2>
        <p className="step-subtitle">Let's get started with your question paper generation</p>
      </div>
      
      <div className="intro-content-step">
        <div className="info-box">
          <div className="info-icon">📋</div>
          <h3>What You'll Need</h3>
          <p>To generate the perfect question paper, we'll need a few documents from you:</p>
        </div>

        <div className="requirements-list">
          <div className="requirement-item">
            <div className="requirement-number">1</div>
            <div className="requirement-content">
              <h4>Previous Question Papers</h4>
              <p>Upload 1 to 3 previous question papers to help our AI understand the question pattern and style.</p>
            </div>
          </div>

          <div className="requirement-item">
            <div className="requirement-number">2</div>
            <div className="requirement-content">
              <h4>CO/PO Mapping File</h4>
              <p>Upload the Course Outcome (CO) and Program Outcome (PO) mapping document for proper alignment.</p>
            </div>
          </div>

          <div className="requirement-item">
            <div className="requirement-number">3</div>
            <div className="requirement-content">
              <h4>Course Syllabus</h4>
              <p>Upload the course syllabus to ensure questions cover all relevant topics and learning objectives.</p>
            </div>
          </div>
        </div>

        <div className="info-note">
          <p>💡 <strong>Tip:</strong> Make sure all PDF files are clear and readable for best results.</p>
        </div>
      </div>
    </div>
  );
};

const PreviousPapersStep = ({ papers, onUpload, onRemove, loading }) => {
  const fileInputRef = React.useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'application/pdf') {
        const newIndex = papers.length;
        onUpload(newIndex, file);
      } else {
        alert('Please upload a PDF file');
      }
    }
    if (event.target) {
      event.target.value = '';
    }
  };

  const addNewUpload = () => {
    if (papers.length < 3) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="step-card">
      <div className="step-header">
        <h2>Upload Previous Question Papers</h2>
        <p className="step-subtitle">Upload 1 to 3 previous question papers (PDF format)</p>
      </div>

      <div className="upload-section">
        {papers.map((paper, index) => (
          <div key={index} className="file-upload-item">
            <div className="file-info">
              <div className="file-icon">📄</div>
              <div className="file-details">
                <div className="file-name">{paper.name}</div>
                <div className="file-size">{(paper.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            </div>
            <button
              className="btn-remove"
              onClick={() => onRemove(index)}
            >
              ✕
            </button>
          </div>
        ))}

        {papers.length < 3 && (
          <>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
            <div className="upload-box" onClick={addNewUpload}>
              <div className="upload-icon">📤</div>
              <p className="upload-text">
                {papers.length === 0 
                  ? 'Click to upload previous question paper (PDF)' 
                  : 'Click to upload another question paper (PDF)'}
              </p>
              <p className="upload-hint">Maximum 3 files allowed</p>
            </div>
          </>
        )}

        {papers.length === 0 && (
          <div className="upload-note">
            <p>⚠️ At least one previous question paper is required</p>
          </div>
        )}
      </div>
    </div>
  );
};

const CoPoStep = ({ file, onUpload, loading }) => {
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        onUpload(selectedFile);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  return (
    <div className="step-card">
      <div className="step-header">
        <h2>Upload CO/PO Mapping File</h2>
        <p className="step-subtitle">Upload the Course Outcome and Program Outcome mapping document (PDF format)</p>
      </div>

      <div className="upload-section">
        {file ? (
          <div className="file-upload-item">
            <div className="file-info">
              <div className="file-icon">📊</div>
              <div className="file-details">
                <div className="file-name">{file.name}</div>
                <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            </div>
            <button
              className="btn-remove"
              onClick={() => onUpload(null)}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="upload-box">
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              id="coPoUpload"
              style={{ display: 'none' }}
            />
            <label htmlFor="coPoUpload" className="upload-label">
              <div className="upload-icon">📊</div>
              <p className="upload-text">Click to upload CO/PO mapping file (PDF)</p>
              <p className="upload-hint">This file should contain the course and program outcome mappings</p>
            </label>
          </div>
        )}
      </div>
    </div>
  );
};

const SyllabusStep = ({ file, onUpload, loading }) => {
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        onUpload(selectedFile);
      } else {
        alert('Please upload a PDF file');
      }
    }
  };

  return (
    <div className="step-card">
      <div className="step-header">
        <h2>Upload Course Syllabus</h2>
        <p className="step-subtitle">Upload the course syllabus document (PDF format)</p>
      </div>

      <div className="upload-section">
        {file ? (
          <div className="file-upload-item">
            <div className="file-info">
              <div className="file-icon">📚</div>
              <div className="file-details">
                <div className="file-name">{file.name}</div>
                <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            </div>
            <button
              className="btn-remove"
              onClick={() => onUpload(null)}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="upload-box">
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              id="syllabusUpload"
              style={{ display: 'none' }}
            />
            <label htmlFor="syllabusUpload" className="upload-label">
              <div className="upload-icon">📚</div>
              <p className="upload-text">Click to upload course syllabus (PDF)</p>
              <p className="upload-hint">This file should contain the complete course syllabus</p>
            </label>
          </div>
        )}
      </div>
    </div>
  );
};

const QuestionConfigStep = ({ patterns, questionCounts, onCountChange, loading }) => {
  const getPatternDescription = (pattern) => {
    if (pattern.type === 'either_or') {
      return `${pattern.description} (Answer any one)`;
    } else if (pattern.type === 'split') {
      return `${pattern.description} (Split from ${pattern.parent_marks} marks)`;
    }
    return pattern.description;
  };

  const totalQuestions = Object.values(questionCounts).reduce((sum, count) => sum + (count || 0), 0);

  return (
    <div className="step-card">
      <div className="step-header">
        <h2>Configure Question Paper</h2>
        <p className="step-subtitle">Specify the number of questions for each mark category</p>
      </div>

      {patterns.length === 0 ? (
        <div className="loading-state">
          <p>Analyzing question patterns...</p>
        </div>
      ) : (
        <>
          <div className="pattern-info">
            <p>Based on the previous question papers, we found the following mark patterns:</p>
          </div>

          <div className="question-config-section">
            {patterns.map((pattern, index) => (
              <div key={index} className="question-config-item">
                <div className="config-header">
                  <div className="marks-badge">{pattern.marks} Marks</div>
                  <div className="pattern-type">
                    {pattern.type === 'either_or' && '📋 Either/Or'}
                    {pattern.type === 'split' && '✂️ Split'}
                    {pattern.type === 'direct' && '📝 Direct'}
                  </div>
                </div>
                <p className="pattern-description">{getPatternDescription(pattern)}</p>
                <div className="count-input-group">
                  <label>Number of Questions:</label>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={questionCounts[pattern.marks] || ''}
                    onChange={(e) => onCountChange(pattern.marks, e.target.value)}
                    className="count-input"
                    onBlur={(e) => {
                      if (e.target.value === '') {
                        onCountChange(pattern.marks, '0');
                      }
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="total-summary">
            <div className="total-box">
              <span className="total-label">Total Questions:</span>
              <span className="total-value">{totalQuestions}</span>
            </div>
          </div>

          {totalQuestions === 0 && (
            <div className="config-note">
              <p>⚠️ Please specify at least one question count to proceed</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default UploadPage;

