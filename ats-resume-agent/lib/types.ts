export interface ContactInfo {
  full_name: string;
  email: string;
  phone: string;
  location: string;
}

export interface ExtractedLinks {
  linkedin?: string;
  github?: string;
  portfolio?: string;
  leetcode?: string;
  gfg?: string;
}

export interface ResumeData {
  contact: ContactInfo;
  links: ExtractedLinks;
  summary: string;
  skills: string[];
  experience: any[];
  projects: any[];
  education: any[];
}

export interface JDAnalysis {
  job_title: string;
  required_skills: string[];
  ats_keywords: string[];
  responsibilities: string[];
  technologies: string[];
}

export interface ProjectRanking {
  title: string;
  relevance_score: number;
  rank: number;
}

export interface RelevantExperience {
  company: string;
  relevance_score: number;
}

export interface SemanticMatch {
  jd_term: string;
  resume_term: string;
  confidence: number;
}

export interface ScoreBreakdown {
  skills: number;
  keywords: number;
  projects: number;
  experience: number;
  education: number;
  certifications: number;
}

export interface GapAnalysis {
  ats_score: number;
  coverage_score: number;
  matched_skills: string[];
  missing_skills: string[];
  matched_keywords: string[];
  missing_keywords: string[];
  project_rankings: ProjectRanking[];
  relevant_experience: RelevantExperience[];
  semantic_matches: SemanticMatch[];
  matching_confidence: number;
  strengths: string[];
  weaknesses: string[];
  score_breakdown: ScoreBreakdown;
  optimization_recommendations: string[];
}

export interface GapAnalysisResponse {
  analysis: GapAnalysis;
}

export interface OptimizationMetadata {
  ats_keywords_used: string[];
  projects_prioritized: string[];
  optimization_score: number;
}

export interface OptimizedResume {
  contact: Record<string, any>;
  links: Record<string, any>;
  summary: string;
  skills: string[];
  projects: any[];
  experience: any[];
  education: any[];
  certifications: string[];
  achievements: string[];
  optimization_metadata: OptimizationMetadata;
}

export interface GenerateOptimizedResponse {
  optimized_resume_id: string;
  optimization_score: number;
  status: string;
  created_at: string;
}

export interface OptimizedResumeDetailResponse {
  id: string;
  resume_id: string;
  job_id: string;
  user_id: string;
  optimized_resume: OptimizedResume;
  created_at: string;
}

export interface GeneratedPDF {
  generated_resume_id: string;
  pdf_url: string;
  html_url: string;
  page_count: number;
  is_one_page: boolean;
  status: string;
  created_at: string;
}
