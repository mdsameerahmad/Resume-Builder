import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  resumeId: string | null;
  jobId: string | null;
  optimizedId: string | null;
  generatedId: string | null;
  
  setResumeId: (id: string | null) => void;
  setJobId: (id: string | null) => void;
  setOptimizedId: (id: string | null) => void;
  setGeneratedId: (id: string | null) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      resumeId: null,
      jobId: null,
      optimizedId: null,
      generatedId: null,
      
      setResumeId: (id) => set({ resumeId: id }),
      setJobId: (id) => set({ jobId: id }),
      setOptimizedId: (id) => set({ optimizedId: id }),
      setGeneratedId: (id) => set({ generatedId: id }),
      reset: () => set({ 
        resumeId: null, 
        jobId: null, 
        optimizedId: null, 
        generatedId: null 
      }),
    }),
    {
      name: 'ats-resume-storage',
    }
  )
);
