'use client';

import { api } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle, Loader2, Upload } from 'lucide-react';
import axios from 'axios';
import { useState } from 'react';

export default function ResumeUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'extracting' | 'parsing' | 'templating' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const { setResumeId } = useAppStore();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Please upload a PDF file.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setStatus('uploading');
      const uploadRes = await api.uploadResume(file);
      const resumeId = uploadRes.data.resume_id;
      setResumeId(resumeId);

      setStatus('extracting');
      await api.extractResume(resumeId);
      setStatus('parsing');
      await api.createMasterResume(resumeId);
      setStatus('templating');
      await api.generateTemplate(resumeId);

      setStatus('success');
    } catch (err: unknown) {
      setStatus('error');
      const axiosError = axios.isAxiosError(err) ? err : null;
      setError(
        axiosError?.code === 'ECONNABORTED'
          ? 'Resume processing took too long. Please try again.'
          : axiosError?.response?.data?.detail ||
            (err instanceof Error ? err.message : 'Failed to process resume')
      );
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Upload Your Resume</h2>
        <p className="text-gray-500 mt-2">PDF format is required for layout preservation.</p>
      </div>

      <div 
        className={cn(
          "relative border-2 border-dashed rounded-lg p-12 transition-all",
          file ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400",
          status === 'error' && "border-red-400 bg-red-50"
        )}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={['uploading', 'extracting', 'parsing', 'templating'].includes(status)}
        />
        
        <div className="flex flex-col items-center justify-center space-y-4">
          {status === 'success' ? (
            <CheckCircle className="h-12 w-12 text-green-500" />
          ) : status === 'error' ? (
            <AlertCircle className="h-12 w-12 text-red-500" />
          ) : (
            <Upload className={cn("h-12 w-12", file ? "text-blue-500" : "text-gray-400")} />
          )}
          
          <div className="text-sm font-medium text-gray-700">
            {file ? file.name : "Click or drag and drop to upload PDF"}
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 text-sm rounded-md flex items-center">
          <AlertCircle className="h-4 w-4 mr-2" />
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || ['uploading', 'extracting', 'parsing', 'templating', 'success'].includes(status)}
        className={cn(
          "w-full mt-6 py-3 px-4 rounded-lg font-semibold text-white transition-all flex items-center justify-center space-x-2",
          !file || status === 'success' 
            ? "bg-gray-300 cursor-not-allowed" 
            : "bg-blue-600 hover:bg-blue-700 shadow-md"
        )}
      >
        {['uploading', 'extracting', 'parsing', 'templating'].includes(status) && (
          <Loader2 className="h-5 w-5 animate-spin" />
        )}
        <span>
          {status === 'uploading' ? 'Uploading...' : 
           status === 'extracting' ? 'Extracting Layout...' : 
           status === 'parsing' ? 'Parsing Resume with AI...' :
           status === 'templating' ? 'Building Master Template...' :
           status === 'success' ? 'Processed Successfully' : 'Start Optimization'}
        </span>
      </button>
    </div>
  );
}
