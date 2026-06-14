'use client';

import { useEffect, useRef, useState } from 'react';
import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { GeneratedPDF } from '@/lib/types';
import { FileDown, Loader2, AlertCircle, CheckCircle, Layout, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import axios from 'axios';

export default function PDFPage() {
  const { optimizedId, setGeneratedId } = useAppStore();
  const [data, setData] = useState<GeneratedPDF | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const generationStarted = useRef(false);

  useEffect(() => {
    if (generationStarted.current) return;
    generationStarted.current = true;

    const generatePDF = async () => {
      if (!optimizedId) {
        setError("Missing optimized resume ID.");
        setIsLoading(false);
        return;
      }

      try {
        const res = await api.generatePDF(optimizedId);
        setData(res.data);
        setGeneratedId(res.data.generated_resume_id);
      } catch (err: unknown) {
        const axiosError = axios.isAxiosError(err) ? err : null;
        setError(
          axiosError?.response?.data?.detail ||
          (err instanceof Error ? err.message : "Failed to generate PDF")
        );
      } finally {
        setIsLoading(false);
      }
    };

    generatePDF();
  }, [optimizedId, setGeneratedId]);

  const handleDownload = () => {
    if (data) {
      const url = api.downloadPDF(data.generated_resume_id);
      window.open(url, '_blank');
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6 text-center">
        <div className="relative">
          <Loader2 className="h-16 w-16 text-blue-600 animate-spin" />
          <Layout className="h-6 w-6 text-blue-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-gray-900">Generating Your PDF</h2>
          <p className="text-gray-500 max-w-xs mx-auto">
            Our engine is injecting optimized content into your original layout and validating one-page constraints.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-12 bg-white rounded-3xl border border-gray-200 text-center shadow-sm">
        <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-6" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">PDF Generation Error</h2>
        <p className="text-gray-600 mb-8">{error}</p>
        <Link 
          href="/optimize" 
          className="inline-flex items-center text-blue-600 font-bold hover:underline"
        >
          <ArrowLeft className="h-5 w-5 mr-2" /> Back to Optimization
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <div className="text-center">
        <div className="bg-green-100 p-3 rounded-full w-fit mx-auto mb-6">
          <CheckCircle className="h-10 w-10 text-green-600" />
        </div>
        <h1 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">Your ATS Resume is Ready!</h1>
        <p className="text-xl text-gray-600">Layout preserved. One page guaranteed. ATS optimized.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Preview Card */}
        <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-sm flex flex-col items-center text-center">
          <div className="bg-gray-50 rounded-2xl mb-6 w-full h-96 overflow-hidden border border-gray-100">
            <iframe
              src={api.previewPDF(data!.generated_resume_id)}
              title="Generated resume preview"
              className="w-full h-full bg-white"
            />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Structure Validated</h3>
          <div className="flex items-center space-x-4 mt-2">
            <span className="flex items-center text-sm font-bold text-green-600 bg-green-50 px-3 py-1 rounded-lg">
              <CheckCircle className="h-4 w-4 mr-1.5" /> {data!.page_count} Page
            </span>
            <span className="flex items-center text-sm font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-lg">
              <Layout className="h-4 w-4 mr-1.5" /> Design Preserved
            </span>
          </div>
        </div>

        {/* Download Card */}
        <div className="bg-blue-600 p-8 rounded-3xl shadow-xl shadow-blue-100 flex flex-col justify-between text-white">
          <div className="space-y-4">
            <h3 className="text-2xl font-bold">Download Final PDF</h3>
            <p className="text-blue-100 leading-relaxed">
              Your optimized resume is ready for submission. We&apos;ve ensured all hyperlinks are clickable and the text is perfectly parsable by all major ATS platforms.
            </p>
          </div>
          
          <button
            onClick={handleDownload}
            className="w-full mt-8 py-5 bg-white text-blue-600 rounded-2xl font-black text-xl shadow-lg hover:bg-blue-50 transition-all flex items-center justify-center group"
          >
            <FileDown className="h-6 w-6 mr-3 group-hover:bounce" />
            Download Now
          </button>
        </div>
      </div>

      <div className="text-center pt-8">
        <button 
          onClick={() => window.location.href = '/'}
          className="text-gray-500 font-bold hover:text-gray-900 transition-colors"
        >
          Finish & Create Another
        </button>
      </div>
    </div>
  );
}
