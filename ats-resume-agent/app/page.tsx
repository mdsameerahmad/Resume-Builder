'use client';

import Link from 'next/link';
import { Upload, Briefcase, Zap, FileText, CheckCircle, ArrowRight } from 'lucide-react';
import { useAppStore } from '@/lib/store';

export default function Dashboard() {
  const { resumeId, jobId, optimizedId } = useAppStore();

  const steps = [
    { 
      name: 'Upload Resume', 
      desc: 'PDF with your original design', 
      href: '/upload', 
      icon: Upload, 
      active: !resumeId,
      done: !!resumeId 
    },
    { 
      name: 'Paste Job', 
      desc: 'Analyze target JD keywords', 
      href: '/jobs', 
      icon: Briefcase, 
      active: !!resumeId && !jobId,
      done: !!jobId 
    },
    { 
      name: 'Gap Analysis', 
      desc: 'Check your current ATS score', 
      href: '/analysis', 
      icon: FileText, 
      active: !!jobId && !optimizedId,
      done: false 
    },
    { 
      name: 'Optimize', 
      desc: 'Generate tailored content', 
      href: '/optimize', 
      icon: Zap, 
      active: !!optimizedId,
      done: false 
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero */}
      <div className="text-center py-12 bg-white rounded-3xl border border-gray-100 shadow-sm px-4">
        <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 tracking-tight mb-6">
          The <span className="text-blue-600">Pro</span> ATS Resume Agent
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Optimize your resume for any job description while preserving your original design and layout. Exactly one page, every time.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link 
            href="/upload" 
            className="px-8 py-4 bg-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all flex items-center"
          >
            Get Started <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <button className="px-8 py-4 bg-white text-gray-700 border border-gray-200 rounded-xl font-bold hover:bg-gray-50 transition-all">
            View Sample
          </button>
        </div>
      </div>

      {/* Workflow Steps */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <Link 
              key={step.name} 
              href={step.href}
              className={`relative p-6 rounded-2xl border transition-all ${
                step.active 
                  ? 'border-blue-200 bg-blue-50/50 shadow-md ring-1 ring-blue-100' 
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              {step.done && (
                <div className="absolute top-4 right-4 text-green-500">
                  <CheckCircle className="h-6 w-6" />
                </div>
              )}
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                step.active ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
              }`}>
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">{step.name}</h3>
              <p className="text-sm text-gray-500">{step.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
