"""
快速使用示例 - Few-Shot Learning 生成 Sysprompt

演示如何使用 Few-Shot Learning 方案将你的 sysprompt 融合到 DeepSeek 生成过程中
"""

from core.prompt_generator_enhanced import PromptGeneratorEnhanced
from core.prompt_manager import PromptManager

# ========== 步骤 1: 准备你的示例 prompt ==========
print("=" * 80)
print("步骤 1: 从 prompt_manager 获取示例 prompt")
print("=" * 80)

pm = PromptManager()
your_example_prompt = pm.generate_system_prompt(
    job_title="高级前端开发工程师",
    interview_type="technical",
    difficulty="senior",
    style="strict",
    feature_vad=True,
    feature_deep=True,
    resume_summary="""
候选人简历摘要：
- 5 年前端开发经验
- 精通 Vue.js、React 及其生态系统
- 主导过多个大型电商平台的前端架构设计
- 熟悉 TypeScript、Webpack、Vite 等工具链
- 有性能优化经验，曾将首屏加载时间从 3s 优化到 1s
- 熟悉 Node.js，有全栈开发经验
"""
)

print(f"✅ 示例 prompt 长度：{len(your_example_prompt)} 字符")
print(f"✅ 示例 prompt 包含的关键部分:")
if "角色定义" in your_example_prompt:
    print("   - ✅ 角色定义")
if "反幻觉" in your_example_prompt:
    print("   - ✅ 反幻觉规则")
if "面试节奏" in your_example_prompt:
    print("   - ✅ 面试节奏控制")
if "话术" in your_example_prompt:
    print("   - ✅ 话术示例")

# ========== 步骤 2: 初始化 PromptGenerator ==========
print("\n" + "=" * 80)
print("步骤 2: 初始化 PromptGeneratorEnhanced")
print("=" * 80)

# 替换为你的实际 API 配置
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

generator = PromptGeneratorEnhanced(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

print("✅ PromptGeneratorEnhanced 已初始化")
print(f"   - Model: deepseek-chat")
print(f"   - API: {DEEPSEEK_BASE_URL}")

# ========== 步骤 3: 使用 Few-Shot Learning 生成 ==========
print("\n" + "=" * 80)
print("步骤 3: 使用 Few-Shot Learning 生成新的 prompt")
print("=" * 80)

# 当前面试配置（可以与示例不同）
current_config = {
    "job_title": "高级 Python 后端开发工程师",  # 👈 不同的岗位
    "interview_type": "technical",
    "difficulty": "senior",
    "style": "strict",
    "resume_summary": """
候选人简历摘要：
- 6 年 Python 开发经验
- 精通 Django、Flask、FastAPI 框架
- 有高并发系统设计经验，日活百万级
- 熟悉 MySQL、PostgreSQL、Redis 等数据库
- 熟悉 Docker、Kubernetes 等容器化技术
- 有团队管理经验，带领过 5 人技术团队
"""
}

print(f"📌 当前面试配置:")
print(f"   - 岗位：{current_config['job_title']}")
print(f"   - 轮次：{current_config['interview_type']}")
print(f"   - 难度：{current_config['difficulty']}")
print(f"   - 风格：{current_config['style']}")

print("\n🚀 开始生成...")

try:
    generated_prompt = generator.generate_few_shot(
        job_title=current_config["job_title"],
        interview_type=current_config["interview_type"],
        difficulty=current_config["difficulty"],
        style=current_config["style"],
        resume_summary=current_config["resume_summary"],
        user_example=your_example_prompt  # 👈 你的示例
    )
    
    print("\n✅ 生成成功!")
    print(f"   - 生成 prompt 长度：{len(generated_prompt)} 字符")
    print(f"   - 预计 token 数：~{len(generated_prompt) // 4}")
    
    # ========== 步骤 4: 验证生成结果 ==========
    print("\n" + "=" * 80)
    print("步骤 4: 验证生成结果")
    print("=" * 80)
    
    # 结构完整性检查
    required_sections = [
        "角色定义",
        "反幻觉",
        "面试节奏",
        "输出格式",
        "收尾话术"
    ]
    
    print("📋 结构完整性检查:")
    missing = []
    for section in required_sections:
        if section in generated_prompt:
            print(f"   - ✅ {section}")
        else:
            print(f"   - ❌ {section}")
            missing.append(section)
    
    # 风格一致性检查
    print("\n🎨 风格一致性检查:")
    key_rules = [
        "禁止捏造经历",
        "禁止自问自答",
        "禁止编造技术事实"
    ]
    
    for rule in key_rules:
        if rule in your_example_prompt and rule in generated_prompt:
            print(f"   - ✅ 保留了：{rule}")
        else:
            print(f"   - ⚠️ 可能丢失：{rule}")
    
    # 岗位针对性检查
    print("\n🎯 岗位针对性检查:")
    if "Python" in generated_prompt or "Django" in generated_prompt or "Flask" in generated_prompt:
        print("   - ✅ 包含 Python 相关技术栈")
    if "后端" in generated_prompt:
        print("   - ✅ 明确后端岗位定位")
    if "架构" in generated_prompt or "高并发" in generated_prompt:
        print("   - ✅ 包含高级岗位要求")
    
    # ========== 步骤 5: 保存或使用 ==========
    print("\n" + "=" * 80)
    print("步骤 5: 保存或使用生成的 prompt")
    print("=" * 80)
    
    # 保存到文件
    output_file = "generated_prompt.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(generated_prompt)
    print(f"✅ 已保存到：{output_file}")
    
    # 或者直接用于面试
    print("\n💡 下一步:")
    print("   1. 将生成的 prompt 集成到 app.py 的 _try_generate_prompt() 函数中")
    print("   2. 启动面试服务进行测试")
    print("   3. 根据实际效果进行迭代优化")
    
    # 显示前 500 字符预览
    print("\n" + "=" * 80)
    print("生成的 prompt 预览（前 500 字符）:")
    print("=" * 80)
    print(generated_prompt[:500])
    print("...")
    
except Exception as e:
    print(f"\n❌ 生成失败：{e}")
    print("\n💡 建议:")
    print("   1. 检查 API Key 是否正确")
    print("   2. 检查网络连接")
    print("   3. 检查 DeepSeek API 状态")
    print("   4. 尝试降低 max_tokens 或调整 temperature")

# ========== 其他方案示例 ==========
print("\n\n" + "=" * 80)
print("其他方案示例")
print("=" * 80)

print("\n1. Hybrid Generation 模式:")
print("   generator.generate_hybrid(")
print("       job_title='高级前端开发工程师',")
print("       interview_type='technical',")
print("       difficulty='senior',")
print("       style='strict',")
print("       resume_summary='...',")
print("       user_template=your_template  # 👈 你的模板框架")
print("   )")

print("\n2. Iterative Refinement 模式:")
print("   generator.refine_iterative(")
print("       current_prompt=current_prompt,")
print("       user_feedback='''")
print("       我对当前 prompt 的以下方面不满意：")
print("       1. 考察维度不够具体...")
print("       2. 面试节奏控制不够严格...")
print("       3. 话术示例太少...")
print("       '''")
print("   )")

print("\n" + "=" * 80)
print("演示完成!")
print("=" * 80)
