// ===== 简历生成器类型定义 =====

/** 模板 ID */
export type TemplateId = 'classic' | 'modern' | 'minimal'
  | 'fresh' | 'tech' | 'creative' | 'executive' | 'compact' | 'elegant'

/** 模板设置 */
export interface TemplateSettings {
  templateId: TemplateId
  themeColor: string
  fontFamily: 'default' | 'serif' | 'mono'
  fontSize: number
  lineHeight: number
  marginMm: number
  photoShow: boolean
}

/** 个人信息 */
export interface BasicInfo {
  name: string
  gender: '' | '男' | '女'
  birthday: string
  email: string
  mobile: string
  location: string
  workYears: string
  photoUrl: string
}

/** 时间线条目（教育/工作/项目/实习/校园经历通用） */
export interface TimeRangeEntry {
  id: string
  timeStart: string
  timeEnd: string
  isCurrent: boolean
  orgName: string
  role: string
  detail: string
}

/** 技能条 */
export interface SkillBarEntry {
  id: string
  name: string
  level: number
}

/** 求职意向 */
export interface JobIntention {
  targetJob: string
  targetCity: string
  salary: string
  availableDate: string
}

/** 模块类型 */
export type ModuleType =
  | 'intention'
  | 'education'
  | 'work'
  | 'project'
  | 'internship'
  | 'campus'
  | 'skills'
  | 'certificates'
  | 'evaluation'
  | 'hobbies'
  | 'custom'

/** 模块类型元信息 */
export const MODULE_TYPE_META: Record<ModuleType, { label: string; icon: string; hasEntries: boolean }> = {
  intention:    { label: '求职意向', icon: 'Target',       hasEntries: false },
  education:    { label: '教育背景', icon: 'GraduationCap', hasEntries: true },
  work:         { label: '工作经验', icon: 'Briefcase',    hasEntries: true },
  project:      { label: '项目经验', icon: 'FolderGit2',   hasEntries: true },
  internship:   { label: '实习经验', icon: 'Building2',    hasEntries: true },
  campus:       { label: '校园经历', icon: 'School',       hasEntries: true },
  skills:       { label: '技能特长', icon: 'Wrench',       hasEntries: false },
  certificates: { label: '荣誉证书', icon: 'Award',        hasEntries: false },
  evaluation:   { label: '自我评价', icon: 'User',         hasEntries: false },
  hobbies:      { label: '兴趣爱好', icon: 'Heart',        hasEntries: false },
  custom:       { label: '自定义模块', icon: 'Plus',       hasEntries: false },
}

/** 简历模块 */
export interface ResumeModule {
  id: string
  type: ModuleType
  title: string
  visible: boolean
  sortIndex: number
  entries?: TimeRangeEntry[]
  intention?: JobIntention
  skillBars?: SkillBarEntry[]
  content?: string
  tags?: string[]
}

/** AI 润色建议 */
export interface FieldPolishSuggestion {
  id: string
  moduleId: string
  entryId?: string
  fieldPath: string
  originalText: string
  suggestedText: string
  reason: string
  status: 'pending' | 'accepted' | 'rejected'
}

/** 顶层简历文档 */
export interface ResumeDocument {
  id: string
  mode: 'general' | 'targeted'
  targetJd: string
  settings: TemplateSettings
  basicInfo: BasicInfo
  modules: ResumeModule[]
  polishSuggestions: FieldPolishSuggestion[]
}

/** 本地模板预设 */
export interface TemplatePreset {
  id: string
  name: string
  settings: TemplateSettings
  savedAt: number
}

/** 预设颜色列表 */
export const PRESET_COLORS = [
  '#333333', '#284967', '#4e7282', '#3978a3', '#1575bf',
  '#0e88ad', '#5695c3', '#609ef3', '#a08f75', '#c19f67',
  '#ed7d31', '#67a886', '#76ba31', '#f36c6c', '#a05fca',
]
