// 基础枚举定义
export type Proficiency = '了解' | '熟悉' | '熟练' | '精通';

export type EducationLevel = '专科' | '本科' | '硕士' | '博士';

// 具体模型
export interface WorkExperience {
  id: string; // 唯一标识
  companyName: string;
  companyType: string;
  industry: string;
  jobTitle: string;
  startDate: string;
  endDate: string;
  isManagement: boolean;
  managementCount?: number;
  mainDuties: string[]; // 页面开发, 组件开发等
  projectTypes: string[];
  projectRole: string; // 负责人, 核心成员, 普通参与
  hasSpecificOutcome: 'YES_DATA' | 'YES_NO_DATA' | 'NOT_SURE';
  // 若有明确成果
  outcomeTypes?: string[];
  outcomeImprovement?: string; // 提升幅度
  // 若无明确成果
  implicitOutcomes?: string[]; // 效率提升，流程优化等
}

export interface Skill {
  name: string;
  level: Proficiency;
}

export interface Education {
  school: string;
  degree: EducationLevel;
  major: string;
  highlights: string[];
}

export interface ResumeQuestionnaireSchema {
  // Step 1: 目标岗位
  targetRole: string;
  targetIndustries: string[];
  targetCompanyType: string;
  currentExperienceBase: string;

  // Step 2: 优化目标
  optimizationGoals: string[]; // 最多3项
  hasJd: boolean;
  jdContent?: string; // 文字版或解析后的JD文本

  // Step 3: 工作经历
  workExperiences: WorkExperience[];

  // Step 4: 技能
  skills: Skill[];

  // Step 5: 教育背景
  education: Education;

  // Step 6: 风格与策略
  resumeStyle: string;
  optimizationStrategies: string[];

  // Step 7: 附加信息
  additionalAdvantages: string;
}
