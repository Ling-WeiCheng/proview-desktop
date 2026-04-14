import type { BasicInfo, ResumeModule, TemplateId } from './resume-builder'

export interface ResumeSection {
  id: string
  type: 'personal_info' | 'education' | 'experience' | 'skills' | 'projects' | 'certifications' | 'other'
  title: string
  content: string
}

export interface ResumeSuggestion {
  suggestionId: string
  targetBlockId: string
  targetField: string
  issueType: string
  issueLabel: string
  originalText: string
  suggestedText: string
  reason: string
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED'
}

export interface ResumeReportEvaluation {
  dimension: string
  score: number
  comment: string
}

export interface ResumeReportContext {
  sessionId: string
  position?: string | null
  avgScore?: number
  summary?: string
  strengths?: string
  weaknesses?: string
  evaluations: ResumeReportEvaluation[]
  questionnaireContext?: string
}

export interface BuilderData {
  detectedTemplate: TemplateId
  basicInfo: BasicInfo
  modules: ResumeModule[]
}

export interface ResumeAnalyzeResponse {
  status: string
  token: string
  ocr_text: string
  sections: ResumeSection[]
  suggestions: ResumeSuggestion[]
  builder_data?: BuilderData
  images?: Record<string, string>  // filename -> data:image/...;base64,...
}
