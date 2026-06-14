import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  // Processing duration varies with storage, AI retries and PDF complexity.
  // Individual lightweight calls can opt into a shorter timeout if needed.
  timeout: 0,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Callers surface API failures in the UI. Avoid triggering Next.js's
    // development error overlay for handled request errors.
    console.warn('API request failed:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  // Resume
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/v1/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
  },
  extractResume: (resumeId: string) =>
    apiClient.post(`/api/v1/resume/extract/${resumeId}`, {}, { timeout: 120000 }),
  createMasterResume: (resumeId: string) =>
    apiClient.post(`/api/v1/resume/parse/${resumeId}`, {}, { timeout: 120000 }),
  generateTemplate: (resumeId: string) =>
    apiClient.post(`/api/v1/template/generate/${resumeId}`, {}, { timeout: 120000 }),
  
  // JD
  analyzeJD: (jdText: string) =>
    apiClient.post('/api/v1/jd/analyze', { job_description: jdText }, { timeout: 120000 }),
  
  // Gap Analysis
  analyzeGap: (resumeId: string, jobId: string) => 
    apiClient.post('/api/v1/gap/analyze', { resume_id: resumeId, job_id: jobId }, { timeout: 120000 }),
    
  // Optimization
  generateOptimized: (resumeId: string, jobId: string) => 
    apiClient.post(
      '/api/v1/optimizer/generate',
      { resume_id: resumeId, job_id: jobId },
      { timeout: 120000 }
    ),
  getOptimizedResume: (optimizedId: string) =>
    apiClient.get(`/api/v1/optimizer/${optimizedId}`, { timeout: 120000 }),
    
  // PDF
  generatePDF: (optimizedId: string) => 
    apiClient.post('/api/v1/pdf/generate', { optimized_resume_id: optimizedId }, { timeout: 120000 }),
    
  downloadPDF: (generatedId: string) => 
    `${API_URL}/api/v1/pdf/${generatedId}/download`,

  previewPDF: (generatedId: string) =>
    `${API_URL}/api/v1/pdf/${generatedId}/preview`,
};
