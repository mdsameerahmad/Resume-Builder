'use client';

import { api } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { GapAnalysis } from '@/lib/types';
import { li } from 'framer-motion/client';
import { AlertCircle, ArrowRight, BarChart2, CheckCircle, Loader2, XCircle } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function AnalysisPage() {
  const { resumeId, jobId } = useAppStore();
  const [analysis, setAnalysis] = useState<GapAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!resumeId || !jobId) {
        setError("Missing resume or job ID. Please complete previous steps.");
        setIsLoading(false);
        return;
      }

      try {
        const res = await api.analyzeGap(resumeId, jobId);
        setAnalysis(res.data.analysis);
      } catch (err: any) {
        setError(err.message || "Failed to fetch gap analysis");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [resumeId, jobId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
        <p className="text-gray-600 font-medium">Running deep gap analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-8 bg-red-50 rounded-2xl border border-red-100 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-red-900 mb-2">Analysis Failed</h2>
        <p className="text-red-700 mb-6">{error}</p>
        <Link href="/" className="text-blue-600 font-bold hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="max-w-2xl mx-auto p-8 bg-yellow-50 rounded-2xl border border-yellow-100 text-center">
        <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-yellow-900 mb-2">No Analysis Available</h2>
        <p className="text-yellow-700 mb-6">The gap analysis result was not returned. Please try again.</p>
        <Link href="/" className="text-blue-600 font-bold hover:underline">Return to Dashboard</Link>
      </div>
    );
  }

  const atsScore = analysis.ats_score ?? 0;
  const coverageScore = analysis.coverage_score ?? 0;
  const recommendations = analysis.optimization_recommendations ?? [];
  const matchedSkills = analysis.matched_skills ?? [];
  const missingSkills = analysis.missing_skills ?? [];
  const matchedKeywords = analysis.matched_keywords ?? [];
  const missingKeywords = analysis.missing_keywords ?? [];
  const projectRankings = analysis.project_rankings ?? [];
  const strengths = analysis.strengths ?? [];
  const weaknesses = analysis.weaknesses ?? [];
  const scoreBreakdown = analysis.score_breakdown ?? {
    skills: 0,
    keywords: 0,
    projects: 0,
    experience: 0,
    education: 0,
    certifications: 0,
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gap Analysis</h1>
          <p className="text-gray-500 mt-1">Comparing your resume with the job requirements</p>
        </div>
        <Link 
          href="/optimize" 
          className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all flex items-center"
        >
          Proceed to Optimization <ArrowRight className="ml-2 h-5 w-5" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Scores */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900">ATS Match Score</h3>
            <span className={`px-4 py-1 rounded-full text-sm font-bold ${
              atsScore > 70 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
            }`}>
              {atsScore}%
            </span>
          </div>
          <div className="w-full bg-gray-100 h-4 rounded-full overflow-hidden">
            <div 
              className="bg-blue-600 h-full transition-all duration-1000" 
              style={{ width: `${atsScore}%` }}
            />
          </div>

          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-gray-900">Keyword Coverage</h3>
            <span className="px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-bold">
              {coverageScore}%
            </span>
          </div>
          <div className="w-full bg-gray-100 h-4 rounded-full overflow-hidden">
            <div 
              className="bg-green-500 h-full transition-all duration-1000" 
              style={{ width: `${coverageScore}%` }}
            />
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
            <BarChart2 className="h-5 w-5 mr-2 text-blue-600" />
            AI Recommendations
          </h3>
          <ul className="space-y-4">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start text-sm text-gray-700">
                <div className="h-2 w-2 bg-blue-400 rounded-full mt-1.5 mr-3 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Matched Skills */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
            <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
            Matched Skills
          </h3>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.length > 0 ? matchedSkills.map((skill, i) => (
              <span key={i} className="px-3 py-1 bg-green-50 text-green-700 text-xs font-bold rounded-lg border border-green-100">
                {skill}
              </span>
            )) : <p className="text-sm text-gray-500">No matched skills found.</p>}
          </div>
        </div>

        {/* Matched Keywords */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
            <CheckCircle className="h-5 w-5 mr-2 text-blue-500" />
            Matched Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {matchedKeywords.length > 0 ? matchedKeywords.map((keyword, i) => (
              <span key={i} className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-lg border border-blue-100">
                {keyword}
              </span>
            )) : <p className="text-sm text-gray-500">No matched keywords found.</p>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Missing Skills */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center">
            <XCircle className="h-5 w-5 mr-2 text-red-500" />
            Missing Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {missingKeywords.length > 0 ? missingKeywords.map((keyword, i) => (
              <span key={i} className="px-3 py-1 bg-red-50 text-red-700 text-xs font-bold rounded-lg border border-red-100">
                {keyword}
              </span>
            )) : <p className="text-sm text-gray-500">No missing keywords found.</p>}
          </div>
        </div>

        {/* Strengths / Weaknesses */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Strengths</h3>
            <ul className="space-y-3 text-sm text-gray-700">
              {strengths.length > 0 ? strengths.map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-green-500" />
                  {item}
                </li>
              )) : <li className="text-gray-500">No strengths identified.</li>}
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Weaknesses</h3>
            <ul className="space-y-3 text-sm text-gray-700">
              {weaknesses.length > 0 ? weaknesses.map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-red-500" />
                  {item}
                </li>
              )) : <li className="text-gray-500">No weaknesses identified.</li>}
            </ul>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Project Rankings</h3>
          <div className="space-y-4">
            {projectRankings.length > 0 ? projectRankings.map((project, i) => (
              <div key={i} className="rounded-2xl border border-gray-100 p-4 bg-slate-50">
                <div className="flex items-center justify-between gap-4">
                  <p className="font-semibold text-gray-900">{project.rank}. {project.title}</p>
                  <span className="text-sm text-gray-600">Score: {project.relevance_score}</span>
                </div>
              </div>
            )) : <p className="text-sm text-gray-500">No ranked projects available.</p>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Score Breakdown</h3>
          <div className="grid grid-cols-1 gap-3 text-sm text-gray-700">
            {Object.entries(scoreBreakdown).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span className="capitalize text-gray-800">{key.replace('_', ' ')}</span>
                <span className="font-semibold text-gray-900">{value}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Relevant Experience</h3>
          <div className="space-y-4 text-sm text-gray-700">
            {analysis.relevant_experience.length > 0 ? analysis.relevant_experience.map((item, i) => (
              <div key={i} className="rounded-2xl border border-gray-100 p-4 bg-slate-50">
                <div className="flex items-center justify-between">
                  <p className="font-semibold">{item.company}</p>
                  <span className="text-gray-600">{item.relevance_score}</span>
                </div>
              </div>
            )) : <p className="text-gray-500">No relevant experience was identified.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
