"""
使用 Few-Shot Learning 生成定制化 Prompt
基于 prompt_manager.py 的完整示例，生成针对特定岗位的定制化 prompt
"""

from core.prompt_generator_enhanced import PromptGeneratorEnhanced
from core.complete_example_prompt import COMPLETE_EXAMPLE_PROMPT

# ========== 配置 API 参数 ==========
# 请替换为你的实际 API 配置
DEEPSEEK_API_KEY = "sk-your-api-key-here"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# ========== 当前面试配置 ==========
current_config = {
    "job_title": "高级 Python 后端开发工程师",
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
- 主导过微服务架构改造，将单体应用拆分为 10+ 个微服务
- 熟悉消息队列（Kafka、RabbitMQ）
- 有性能优化经验，曾将 API 响应时间从 500ms 优化到 50ms
"""
}

# ========== 生成定制化 Prompt ==========

print("=" * 80)
print("🚀 使用 Few-Shot Learning 生成定制化 Prompt")
print("=" * 80)

print(f"\n📌 当前面试配置:")
print(f"   - 岗位：{current_config['job_title']}")
print(f"   - 轮次：{current_config['interview_type']}")
print(f"   - 难度：{current_config['difficulty']}")
print(f"   - 风格：{current_config['style']}")

print(f"\n📌 示例 Prompt 长度：{len(COMPLETE_EXAMPLE_PROMPT)} 字符")
print(f"   - 预计 token 数：~{len(COMPLETE_EXAMPLE_PROMPT) // 4}")

# 初始化 Generator
generator = PromptGeneratorEnhanced(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

print("\n✅ PromptGeneratorEnhanced 已初始化")
print(f"   - Model: deepseek-chat")
print(f"   - Temperature: 0.5 (Few-Shot Learning 模式)")

# 生成定制化 Prompt
print("\n⏳ 正在生成定制化 Prompt...")
print("   - 使用 Few-Shot Learning 模式")
print("   - 学习示例 Prompt 的结构、风格和规则设计")
print("   - 根据当前岗位配置进行调整")

try:
    generated_prompt = generator.generate_few_shot(
        job_title=current_config["job_title"],
        interview_type=current_config["interview_type"],
        difficulty=current_config["difficulty"],
        style=current_config["style"],
        resume_summary=current_config["resume_summary"],
        user_example=COMPLETE_EXAMPLE_PROMPT  # 👈 使用完整示例
    )
    
    print("\n✅ 生成成功!")
    print(f"   - 生成 prompt 长度：{len(generated_prompt)} 字符")
    print(f"   - 预计 token 数：~{len(generated_prompt) // 4}")
    
    # 保存生成的 prompt
    output_file = "generated_custom_prompt.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(generated_prompt)
    
    print(f"\n💾 已保存到：{output_file}")
    
    # 显示前 1000 字符预览
    print("\n" + "=" * 80)
    print("生成的定制化 Prompt 预览（前 1000 字符）:")
    print("=" * 80)
    print(generated_prompt[:1000])
    print("...")
    print("=" * 80)
    
    # 验证生成的 prompt
    print("\n🔍 开始验证生成的 Prompt")
    print("=" * 80)
    
    from utils.prompt_validator import PromptValidator
    
    validator = PromptValidator()
    result = validator.validate_full(
        generated_prompt,
        COMPLETE_EXAMPLE_PROMPT,
        current_config["job_title"]
    )
    
    print(f"\n📊 综合得分：{result['final_score']:.1f}/100")
    
    if result['final_score'] >= 80:
        print("✅ 验证通过！生成的 prompt 质量良好")
    elif result['final_score'] >= 60:
        print("⚠️ 验证基本通过，但有一些建议改进的地方")
    else:
        print("❌ 验证未通过，建议重新生成或使用 Iterative Refinement 优化")
    
    # 显示需要改进的问题
    if result.get('all_issues'):
        print("\n📝 需要改进的问题:")
        for issue in result['all_issues']:
            print(f"   - {issue}")
    
    print("\n" + "=" * 80)
    print("✨ 生成完成!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 生成失败：{e}")
    print("\n💡 建议:")
    print("   1. 检查 API Key 是否正确")
    print("   2. 检查网络连接")
    print("   3. 检查 DeepSeek API 状态")
    print("   4. 尝试降低 max_tokens 或调整 temperature")
