'use client';

import ResumeUploader from '@/components/resume/ResumeUploader';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function UploadPage() {
  return (
    <div className="space-y-8">
      <Link 
        href="/" 
        className="inline-flex items-center text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4 mr-1.5" /> Back to Dashboard
      </Link>
      
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">Step 1: Your Original Resume</h1>
          <p className="text-lg text-gray-600">
            Upload your existing resume. Our engine will extract your design, layout, and content to create a master template.
          </p>
        </div>

        <ResumeUploader />

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
            <h4 className="font-bold text-gray-900 mb-1 text-sm">Design Preservation</h4>
            <p className="text-xs text-gray-500">Your fonts, colors, and layout are captured precisely.</p>
          </div>
          <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
            <h4 className="font-bold text-gray-900 mb-1 text-sm">Link Extraction</h4>
            <p className="text-xs text-gray-500">LinkedIn, GitHub, and Portfolio links are kept clickable.</p>
          </div>
          <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
            <h4 className="font-bold text-gray-900 mb-1 text-sm">Master Template</h4>
            <p className="text-xs text-gray-500">We create a reusable base for all future job applications.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
