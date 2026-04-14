"""
Prompt Generator Agent（增强版 - 支持 Few-Shot Learning）
根据面试配置动态生成高质量的面试官 System Prompt。
使用 Few-Shot Learning 方式，将用户设计的优质 prompt 作为示例指导生成。
"""
from openai import OpenAI


class PromptGeneratorEnhanced:
    """
    增强版 Prompt Generator：
    1. 支持 Few-Shot Learning - 使用用户提供的优质 prompt 作为示例
    2. 支持 Hybrid Generation - 基于用户模板进行优化
    3. 支持 Iterative Refinement - 多轮迭代优化
    """

    # ===== Few-Shot Learning 元提示词 =====
    META_PROMPT_FEW_SHOT = """你是一个面试 Prompt 工程师。你的任务是根据用户提供的参考示例，为 AI 面试官生成高质量的 System Prompt。

## 参考示例（用户设计的优质 prompt）
{user_example_prompt}

## 当前面试配置
- 目标岗位：{job_title}
- 面试轮次：{interview_type}
- 难度级别：{difficulty}
- 面试风格：{style}
- 候选人简历摘要：{resume_summary}
- 岗位要求 / 职位描述：{job_requirements}

## 生成要求
请**学习参考示例的结构、风格和规则设计**，根据当前面试配置生成一个新的 System Prompt。

### 必须学习参考示例的以下方面：
1. **结构框架**：参考示例的章节划分和组织逻辑
2. **角色定义方式**：如何描述面试官人设和背景
3. **规则表达风格**：规则的措辞方式、语气强度
4. **考察维度设计**：如何根据岗位设计考察点
5. **节奏控制机制**：题目数量、追问深度、阶段划分
6. **话术示例**：具体的开场白、过渡语、收尾话术

### 必须根据当前配置调整的方面：
1. **岗位针对性**：根据{job_title}调整考察重点和技术栈
2. **面试轮次**：根据{interview_type}调整考察维度
3. **难度级别**：根据{difficulty}调整题目深度和数量
4. **面试风格**：根据{style}调整语气和互动方式
5. **简历深挖**：根据{resume_summary}设计针对性问题方向
6. **岗位要求融合**：根据{job_requirements}调整考察重点和评分标准，但不能把它当成候选人事实

### 强制约束（不可违反）：
1. 【禁止捏造经历】严格基于真实简历内容或用户回答提问
2. 【禁止自问自答】每次只抛 1-2 个问题后立即停止
3. 【禁止编造技术事实】严禁瞎编不存在的框架、API、技术名词
4. 【禁止出戏】严禁出现"作为 AI 模型"等免责声明
5. 【输出格式】每次回复控制在 200 字以内，只提 1-2 个问题

## 输出
直接输出生成的 System Prompt 文本，不要包含任何解释或元信息。"""

    # ===== Hybrid Generation 元提示词 =====
    META_PROMPT_HYBRID = """你是一个面试 Prompt 优化专家。你的任务是基于用户提供的模板，进行优化和补充。

## 用户提供的模板（核心框架）
{user_template}

## 当前面试配置
- 目标岗位：{job_title}
- 面试轮次：{interview_type}
- 难度级别：{difficulty}
- 面试风格：{style}
- 候选人简历摘要：{resume_summary}
- 岗位要求 / 职位描述：{job_requirements}

## 优化任务
请在**保留用户模板核心框架和关键规则**的前提下，进行以下优化：

### 必须保留的内容（不可修改）：
1. 用户模板中的角色定义核心
2. 用户模板中的反幻觉规则
3. 用户模板中的面试节奏控制
4. 用户模板中的话术示例风格

### 需要优化的内容：
1. **岗位针对性**：将通用描述替换为{job_title}相关的具体内容
2. **考察维度**：根据{interview_type}补充 3-5 个具体考察维度
3. **难度适配**：根据{difficulty}调整题目数量和追问深度
4. **风格调整**：根据{style}调整语气和互动方式
5. **简历深挖**：根据{resume_summary}设计 2-3 个针对性深挖方向
6. **岗位要求融合**：根据{job_requirements}补充考察重点和评分基准，但不能把这部分内容当成候选人事实

### 补充内容（如果用户模板缺失）：
1. 如果缺少"回应与过渡"规则，请补充
2. 如果缺少"话术多样性"要求，请补充
3. 如果缺少"面试收尾话术"，请补充
4. 如果缺少"语音输入纠错"说明，请补充

## 输出
直接输出优化后的 System Prompt 文本，不要包含任何解释或元信息。"""

    # ===== Iterative Refinement 元提示词 =====
    META_PROMPT_ITERATIVE = """你是一个面试 Prompt 优化专家。你的任务是根据用户反馈，对现有 prompt 进行迭代优化。

## 当前 prompt 版本
{current_prompt}

## 用户反馈
{user_feedback}

## 优化要求
请根据用户反馈，对当前 prompt 进行针对性优化：

1. **保留优点**：保持当前 prompt 中用户满意的部分
2. **修复问题**：针对用户指出的问题进行修改
3. **增强效果**：根据用户建议补充新内容或调整现有内容

## 输出
直接输出优化后的 System Prompt 文本，不要包含任何解释或元信息。"""

    STYLE_MAP = {
        "default": "标准专业型（客观中立、专业均衡）",
        "strict": "严肃高压型（冷峻专业、施加压力、刁钻追问）",
        "friendly": "温和引导型（友善鼓励、循循善诱）",
    }

    TYPE_MAP = {
        "technical": "技术面/专业面",
        "hr": "HR 面/综合素质面",
        "manager": "主管面/业务面",
    }

    DIFFICULTY_MAP = {
        "junior": "初级（基础概念、常见 API）",
        "mid": "中级（实战经验、原理理解）",
        "senior": "高级（架构设计、底层源码）",
    }

    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate_few_shot(self, job_title: str, interview_type: str, difficulty: str,
                          style: str, resume_summary: str, user_example: str,
                          job_requirements: str = "") -> str:
        """
        Few-Shot Learning 模式：使用用户提供的优质 prompt 作为示例
        
        Args:
            user_example: 用户设计的优质 prompt（来自 prompt_manager 或其他来源）
        
        Returns:
            生成的 System Prompt
        """
        prompt = self.META_PROMPT_FEW_SHOT.format(
            user_example_prompt=user_example,
            job_title=job_title,
            interview_type=self.TYPE_MAP.get(interview_type, interview_type),
            difficulty=self.DIFFICULTY_MAP.get(difficulty, difficulty),
            style=self.STYLE_MAP.get(style, style),
            resume_summary=resume_summary if resume_summary else "未提供简历",
            job_requirements=job_requirements if job_requirements else "未提供岗位要求",
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,  # 降低 temperature，更接近示例风格
            max_tokens=2500,
            top_p=0.9
        )
        return response.choices[0].message.content

    def generate_hybrid(self, job_title: str, interview_type: str, difficulty: str,
                        style: str, resume_summary: str, user_template: str,
                        job_requirements: str = "") -> str:
        """
        Hybrid Generation 模式：基于用户模板进行优化
        
        Args:
            user_template: 用户提供的模板框架（来自 prompt_manager）
        
        Returns:
            优化后的 System Prompt
        """
        prompt = self.META_PROMPT_HYBRID.format(
            user_template=user_template,
            job_title=job_title,
            interview_type=self.TYPE_MAP.get(interview_type, interview_type),
            difficulty=self.DIFFICULTY_MAP.get(difficulty, difficulty),
            style=self.STYLE_MAP.get(style, style),
            resume_summary=resume_summary if resume_summary else "未提供简历",
            job_requirements=job_requirements if job_requirements else "未提供岗位要求",
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,  # 中等 temperature，平衡创新和遵循
            max_tokens=2500,
            top_p=0.9
        )
        return response.choices[0].message.content

    def refine_iterative(self, current_prompt: str, user_feedback: str) -> str:
        """
        Iterative Refinement 模式：根据用户反馈迭代优化
        
        Args:
            current_prompt: 当前 prompt 版本
            user_feedback: 用户反馈（自然语言描述）
        
        Returns:
            优化后的 System Prompt
        """
        prompt = self.META_PROMPT_ITERATIVE.format(
            current_prompt=current_prompt,
            user_feedback=user_feedback
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,  # 降低 temperature，更忠实于反馈
            max_tokens=2500,
            top_p=0.9
        )
        return response.choices[0].message.content

    def generate(self, job_title: str, interview_type: str, difficulty: str,
                 style: str, resume_summary: str = "", job_requirements: str = "") -> str:
        """
        兼容旧版本的默认方法（使用 Few-Shot 模式，示例来自 prompt_manager）
        """
        # 自动从 prompt_manager 获取示例
        from core.prompt_manager import PromptManager
        pm = PromptManager()
        example_prompt = pm.generate_system_prompt(
            job_title=job_title,
            interview_type=interview_type,
            difficulty=difficulty,
            style=style,
            feature_vad=False,
            feature_deep=False,
            resume_summary=resume_summary if resume_summary else "未提供简历",
            job_requirements=job_requirements,
        )
        
        # 使用 Few-Shot 模式生成
        return self.generate_few_shot(
            job_title=job_title,
            interview_type=interview_type,
            difficulty=difficulty,
            style=style,
            resume_summary=resume_summary,
            user_example=example_prompt,
            job_requirements=job_requirements,
        )
