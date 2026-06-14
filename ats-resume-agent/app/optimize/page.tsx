'use client';

import { api } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { OptimizedResume } from '@/lib/types';
import { AlertCircle, ArrowRight, Check, Sparkles, Zap } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function OptimizePage() {
  const { resumeId, jobId, setOptimizedId } = useAppStore();
  const [data, setData] = useState<OptimizedResume | null>(null);
  const [optimizationScore, setOptimizationScore] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const generateOptimization = async () => {
      if (!resumeId || !jobId) {
        setError("Missing resume or job ID.");
        setIsLoading(false);
        return;
      }

      try {
        const generateRes = await api.generateOptimized(resumeId, jobId);
        setOptimizedId(generateRes.data.optimized_resume_id);
        setOptimizationScore(generateRes.data.optimization_score);

        const detailRes = await api.getOptimizedResume(generateRes.data.optimized_resume_id);
        setData(detailRes.data.optimized_resume);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || "Failed to generate optimization");
      } finally {
        setIsLoading(false);
      }
    };

    generateOptimization();
  }, [resumeId, jobId, setOptimizedId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Sparkles className="h-12 w-12 text-blue-600 animate-pulse" />
        <p className="text-gray-600 font-medium">Our AI is tailoring your content...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-8 bg-red-50 rounded-2xl text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            Optimization Preview
            <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 text-xs font-black rounded-full uppercase tracking-widest">
              AI Generated
            </span>
          </h1>
        </div>
        <Link 
          href="/pdf" 
          className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-all flex items-center"
        >
          Generate Final PDF <ArrowRight className="ml-2 h-5 w-5" />
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Summary & Skills */}
        <div className="lg:col-span-2 space-y-8">
          {/* Summary */}
          <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Optimized Summary</h3>
            <p className="text-gray-700 leading-relaxed italic border-l-4 border-blue-500 pl-4 py-2">
              "{data!.summary}"
            </p>
          </div>

          {/* Experience */}
          <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Experience & Bullet Points</h3>
            <div className="space-y-8">
              {data!.experience.map((exp: any, i: number) => (
                <div key={i} className="space-y-3">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-gray-900">{exp.role}</h4>
                    <span className="text-sm text-gray-500">{exp.duration}</span>
                  </div>
                  <p className="text-sm font-medium text-blue-600">{exp.company}</p>
                  <ul className="space-y-2">
                    {exp.responsibilities.map((bullet: string, j: number) => (
                      <li key={j} className="text-sm text-gray-600 flex items-start">
                        <Check className="h-4 w-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                        {bullet}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Skills & Stats */}
        <div className="space-y-8">
          <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Prioritized Skills</h3>
            <div className="flex flex-wrap gap-2">
              {data!.skills.map((skill: string, i: number) => (
                <span key={i} className="px-3 py-1.5 bg-gray-50 text-gray-700 text-xs font-bold rounded-lg border border-gray-200">
                  {skill}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-blue-600 p-8 rounded-2xl text-white shadow-xl shadow-blue-200">
            <Zap className="h-8 w-8 mb-4 text-blue-200" />
            <h3 className="text-xl font-bold mb-2">Optimization Score</h3>
            <div className="text-5xl font-black mb-4">
              {optimizationScore ?? data?.optimization_metadata.optimization_score ?? '--'}%
            </div>
            <p className="text-blue-100 text-sm leading-relaxed">
              Your resume is now highly tailored to the target job description. We've optimized keywords, prioritized relevant experience, and formatted content for maximum ATS readability.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
