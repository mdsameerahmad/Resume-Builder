'use client';

import JDInput from '@/components/jobs/JDInput';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function JobsPage() {
  return (
    <div className="space-y-8">
      <Link 
        href="/" 
        className="inline-flex items-center text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4 mr-1.5" /> Back to Dashboard
      </Link>
      
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">Step 2: The Job Description</h1>
          <p className="text-lg text-gray-600">
            Paste the job you're applying for. We'll extract the exact keywords and skills the company's ATS is looking for.
          </p>
        </div>

        <JDInput />
      </div>
    </div>
  );
}
