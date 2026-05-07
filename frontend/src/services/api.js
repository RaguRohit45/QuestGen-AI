const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://questgen-ai-iqt2.onrender.com/apigit add .';

class ApiService {
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  async uploadPreviousPapers(files) {
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await fetch(`${API_BASE_URL}/upload/previous-papers`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload previous papers failed:', error);
      throw error;
    }
  }

  async uploadCoPo(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload/copo`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload CO/PO failed:', error);
      throw error;
    }
  }

  async uploadSyllabus(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload/syllabus`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload syllabus failed:', error);
      throw error;
    }
  }

  async processPDFs() {
    try {
      const response = await fetch(`${API_BASE_URL}/process/read-pdfs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Processing failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Process PDFs failed:', error);
      throw error;
    }
  }

  async analyzeQuestionPatterns() {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/question-patterns`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Pattern analysis failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Analyze question patterns failed:', error);
      throw error;
    }
  }

  async generateQuestions(questionCounts, query = 'Generate exam questions based on the uploaded documents') {
    try {
      const response = await fetch(`${API_BASE_URL}/generate/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          question_counts: questionCounts
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Question generation failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Generate questions failed:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;

