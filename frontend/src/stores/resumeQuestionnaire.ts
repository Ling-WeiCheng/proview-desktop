import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ResumeQuestionnaireSchema, EducationLevel } from '../types/resume-questionnaire';

export const useResumeQuestionnaireStore = defineStore('resumeQuestionnaire', () => {
  const currentStep = ref(1);

  const initialFormState: ResumeQuestionnaireSchema = {
    targetRole: '',
    targetIndustries: [],
    targetCompanyType: '',
    currentExperienceBase: '',
    optimizationGoals: [],
    hasJd: false,
    workExperiences: [],
    skills: [],
    education: {
      school: '',
      degree: '本科' as EducationLevel,
      major: '',
      highlights: []
    },
    resumeStyle: '简洁专业（外企风格）',
    optimizationStrategies: [],
    additionalAdvantages: ''
  };

  const formData = ref<ResumeQuestionnaireSchema>(JSON.parse(JSON.stringify(initialFormState)));

  function nextStep() {
    if (currentStep.value < 7) currentStep.value++;
  }

  function prevStep() {
    if (currentStep.value > 1) currentStep.value--;
  }

  function addWorkExperience() {
    formData.value.workExperiences.push({
      id: Date.now().toString(),
      companyName: '',
      companyType: '',
      industry: '',
      jobTitle: '',
      startDate: '',
      endDate: '',
      isManagement: false,
      mainDuties: [],
      projectTypes: [],
      projectRole: '核心成员',
      hasSpecificOutcome: 'NOT_SURE',
      implicitOutcomes: []
    });
  }

  function removeWorkExperience(id: string) {
    formData.value.workExperiences = formData.value.workExperiences.filter(exp => exp.id !== id);
  }

  function reset() {
    currentStep.value = 1;
    formData.value = JSON.parse(JSON.stringify(initialFormState));
  }

  return { currentStep, formData, nextStep, prevStep, addWorkExperience, removeWorkExperience, reset };
});
