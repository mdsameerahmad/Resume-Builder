'use client';

import { useState } from 'react';
import { Briefcase, Loader2, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

export default function JDInput() {
  const [jdText, setJdText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setJobId } = useAppStore();
  const router = useRouter();

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      const res = await api.analyzeJD(jdText);
      setJobId(res.data.job_id);
      router.push('/analysis');
    } catch (err: any) {
      setError(err.message || 'Failed to analyze job description');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white rounded-2xl border border-gray-200 shadow-sm">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-blue-100 p-2 rounded-lg">
          <Briefcase className="h-6 w-6 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Job Description Analysis</h2>
      </div>

      <p className="text-gray-600 mb-6">
        Paste the full job description below. Our AI will extract key skills, requirements, and technologies for optimization.
      </p>

      <textarea
        value={jdText}
        onChange={(e) => setJdText(e.target.value)}
        placeholder="Paste JD here..."
        className="w-full h-80 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none text-gray-700"
      />

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-xl flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={isLoading || !jdText.trim()}
        className="w-full mt-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-bold rounded-xl shadow-lg transition-all flex items-center justify-center space-x-2"
      >
        {isLoading ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <span>Analyze Job Description</span>
        )}
      </button>
    </div>
  );
}
