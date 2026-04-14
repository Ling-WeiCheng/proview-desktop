export type CareerUserId = string | number

export interface CareerProfile {
  user_id: CareerUserId
  target_role: string
  current_stage: string
  interest_tags: string
  strength_tags: string
  gap_tags: string
  overall_score: number
  source_summary: string
  sessions?: number
  latest_session_id?: string | null
  resume?: Record<string, unknown> | null
}

export interface CareerRecommendation {
  type: string
  title: string
  reason: string
  url?: string
}

export interface CareerPlan {
  id: number
  user_id: CareerUserId
  target_role: string
  career_goal: string
  status: string
  horizon_months: number
  summary: string
  assessment_json: Record<string, unknown>
  recommendation_json: CareerRecommendation[]
  created_at: string
  updated_at: string
}

export interface CareerMilestone {
  id: number
  plan_id: number
  title: string
  description: string
  month_label: string
  status: string
  sort_order: number
  target_date: string
  created_at?: string
  updated_at?: string
}

export interface CareerTask {
  id: number
  milestone_id: number
  title: string
  description: string
  task_type: string
  task_type_icon?: string  // e.g. "book-open", "target", "code", "graduation-cap"
  task_type_label?: string // e.g. "技术学习", "面试准备", "项目实践", "课程学习"
  priority: number
  status: string
  progress: number
  due_date: string
  completed_at: string
  created_at?: string
  updated_at?: string
}

export interface CareerProgressLog {
  id: number
  task_id: number
  note: string
  progress_delta: number
  created_at: string
}

export interface CareerDashboardStats {
  plan_count: number
  active_task_count: number
  completed_task_count: number
  progress_rate: number
}

export interface CareerPlanningDocSection {
  heading: string
  paragraphs: string[]
  bullets: string[]
  action_items?: string[]
}

export interface CareerPlanningDocument {
  id: string
  title: string
  subtitle: string
  category: string
  categoryIcon: string
  audience: string[]
  summary: string
  cover_gradient: string
  cover_icon: string
  difficulty: '入门' | '进阶' | '中级' | '高级'
  read_time: number
  tags: string[]
  is_featured: boolean
  sections: CareerPlanningDocSection[]
  // 用户交互相关
  is_favorited?: boolean
  read_progress?: number
  last_read_at?: string
}

export interface CareerPlanningDocsCatalog {
  version: string
  updated_at: string
  documents: CareerPlanningDocument[]
}

export interface CareerDashboardData {
  profile: CareerProfile | Record<string, unknown>
  plans: CareerPlan[]
  current_plan: CareerPlan | Record<string, unknown>
  milestones: CareerMilestone[]
  tasks: CareerTask[]
  logs: CareerProgressLog[]
  recommendations: CareerRecommendation[]
  stats: CareerDashboardStats
}

export interface CareerDashboardResponse {
  status: string
  data: CareerDashboardData
  message?: string
}

export interface CareerDocsResponse {
  status: string
  data: CareerPlanningDocsCatalog
  message?: string
}

export interface CareerDocumentResponse {
  status: string
  data: CareerPlanningDocument
  message?: string
}

export interface CareerListPlansResponse {
  status: string
  data: {
    plans: CareerPlan[]
  }
  message?: string
}

export interface CareerPlanDetailResponse {
  status: string
  data: {
    plan: CareerPlan
    milestones: CareerMilestone[]
    tasks: CareerTask[]
    logs: CareerProgressLog[]
  }
  message?: string
}

export interface GenerateCareerPlanPayload {
  target_role?: string
  career_goal?: string
  horizon_months?: number
  refresh?: boolean
}

export interface UpdateCareerTaskPayload {
  status?: string
  progress?: number
  note?: string
}
