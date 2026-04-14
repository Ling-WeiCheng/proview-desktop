"""
Prompt 验证工具
用于验证生成的 sysprompt 是否符合要求
"""

class PromptValidator:
    """Prompt 验证器"""
    
    def __init__(self):
        # 必须包含的关键部分
        self.required_sections = [
            "角色定义",
            "禁止捏造",
            "禁止自问自答",
            "禁止编造技术",
            "面试节奏",
            "输出格式"
        ]
        
        # 必须保留的反幻觉规则
        self.required_rules = [
            "禁止捏造经历",
            "禁止自问自答", 
            "禁止编造技术事实",
            "禁止出戏"
        ]
        
        # 建议包含的部分
        self.recommended_sections = [
            "开场白",
            "自我介绍",
            "回应与过渡",
            "收尾话术",
            "话术多样性",
            "追问策略"
        ]
    
    def validate_structure(self, prompt_text: str) -> dict:
        """验证结构完整性"""
        results = {
            "required_sections": {},
            "recommended_sections": {},
            "overall_score": 0,
            "issues": [],
            "passed": True
        }
        
        # 检查必须包含的部分
        print("📋 必选部分检查:")
        for section in self.required_sections:
            found = section in prompt_text
            results["required_sections"][section] = found
            if found:
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section}")
                results["issues"].append(f"缺少必选部分：{section}")
                results["passed"] = False
        
        # 检查推荐包含的部分
        print("\n📋 推荐部分检查:")
        for section in self.recommended_sections:
            found = section in prompt_text
            results["recommended_sections"][section] = found
            if found:
                print(f"   ✅ {section}")
            else:
                print(f"   ⚠️ 建议添加：{section}")
        
        # 计算得分
        required_count = sum(results["required_sections"].values())
        recommended_count = sum(results["recommended_sections"].values())
        
        total_required = len(self.required_sections)
        total_recommended = len(self.recommended_sections)
        
        results["overall_score"] = (required_count / total_required * 70 + 
                                    recommended_count / total_recommended * 30)
        
        print(f"\n📊 结构完整性得分: {results['overall_score']:.1f}/100")
        
        return results
    
    def validate_rules(self, prompt_text: str, your_example: str = None) -> dict:
        """验证规则保留情况"""
        results = {
            "rules_found": {},
            "overall_score": 0,
            "issues": [],
            "passed": True
        }
        
        print("📋 反幻觉规则检查:")
        for rule in self.required_rules:
            found = rule in prompt_text
            results["rules_found"][rule] = found
            if found:
                print(f"   ✅ {rule}")
            else:
                print(f"   ❌ {rule}")
                results["issues"].append(f"规则丢失：{rule}")
                results["passed"] = False
        
        # 计算得分
        rules_count = sum(results["rules_found"].values())
        results["overall_score"] = rules_count / len(self.required_rules) * 100
        
        print(f"\n📊 规则保留得分: {results['overall_score']:.1f}/100")
        
        return results
    
    def validate_style(self, prompt_text: str, your_example: str = None) -> dict:
        """验证风格一致性（如果提供了示例）"""
        results = {
            "similarities": {},
            "overall_score": 0,
            "passed": True
        }
        
        if not your_example:
            print("⚠️ 未提供示例，跳过风格一致性检查")
            results["passed"] = None
            return results
        
        print("📋 风格一致性检查:")
        
        # 检查关键表达模式
        patterns = [
            ("面试官", "面试官相关描述"),
            ("候选人", "候选人相关描述"),
            ("问题", "问题设计相关"),
            ("回答", "回答处理相关")
        ]
        
        for pattern, desc in patterns:
            in_example = pattern in your_example
            in_generated = pattern in prompt_text
            
            if in_example and in_generated:
                print(f"   ✅ {desc}: 风格一致")
                results["similarities"][desc] = True
            elif in_example and not in_generated:
                print(f"   ❌ {desc}: 示例中有，生成结果中丢失")
                results["similarities"][desc] = False
                results["passed"] = False
            else:
                print(f"   ⚠️ {desc}: 示例中也没有，跳过")
        
        # 计算得分
        valid_patterns = [v for v in results["similarities"].values() if v is not None]
        if valid_patterns:
            results["overall_score"] = sum(valid_patterns) / len(valid_patterns) * 100
        else:
            results["overall_score"] = 100
        
        print(f"\n📊 风格一致性得分: {results['overall_score']:.1f}/100")
        
        return results
    
    def validate_content(self, prompt_text: str, job_title: str = None) -> dict:
        """验证内容针对性"""
        results = {
            "job_specific": {},
            "overall_score": 0,
            "issues": [],
            "passed": True
        }
        
        print("📋 内容针对性检查:")
        
        if not job_title:
            print("⚠️ 未提供岗位信息，跳过针对性检查")
            results["passed"] = None
            return results
        
        # 检查是否包含岗位相关内容
        # 这里只是一个简单的示例，实际应根据岗位类型设计更详细的检查
        tech_keywords = ["开发", "工程师", "技术", "架构", "系统"]
        
        keyword_found = False
        for keyword in tech_keywords:
            if keyword in prompt_text:
                keyword_found = True
                break
        
        if keyword_found:
            print(f"   ✅ 包含技术相关内容")
            results["job_specific"]["tech_content"] = True
        else:
            print(f"   ❌ 缺少技术相关内容")
            results["job_specific"]["tech_content"] = False
            results["issues"].append("缺少技术相关内容")
            results["passed"] = False
        
        # 检查是否有具体的考察维度
        dimension_keywords = ["考察", "维度", "方面", "技能", "能力"]
        
        dimension_found = False
        for keyword in dimension_keywords:
            if keyword in prompt_text:
                dimension_found = True
                break
        
        if dimension_found:
            print(f"   ✅ 包含考察维度设计")
            results["job_specific"]["dimension_design"] = True
        else:
            print(f"   ⚠️ 建议添加考察维度设计")
            results["job_specific"]["dimension_design"] = False
        
        # 计算得分
        results["overall_score"] = 50  # 基础分
        if results["job_specific"].get("tech_content"):
            results["overall_score"] += 25
        if results["job_specific"].get("dimension_design"):
            results["overall_score"] += 25
        
        print(f"\n📊 内容针对性得分: {results['overall_score']:.1f}/100")
        
        return results
    
    def validate_full(self, prompt_text: str, your_example: str = None, 
                      job_title: str = None) -> dict:
        """完整验证"""
        print("=" * 80)
        print("🔍 开始完整验证")
        print("=" * 80)
        
        # 各维度验证
        structure_results = self.validate_structure(prompt_text)
        rules_results = self.validate_rules(prompt_text, your_example)
        style_results = self.validate_style(prompt_text, your_example)
        content_results = self.validate_content(prompt_text, job_title)
        
        # 综合得分
        scores = [
            structure_results["overall_score"],
            rules_results["overall_score"],
            style_results.get("overall_score", 100),
            content_results.get("overall_score", 100)
        ]
        
        final_score = sum(scores) / len([s for s in scores if s is not None])
        
        print("\n" + "=" * 80)
        print(f"📊 综合得分: {final_score:.1f}/100")
        print("=" * 80)
        
        # 总体评估
        if final_score >= 80:
            print("✅ 验证通过！生成的 prompt 质量良好")
        elif final_score >= 60:
            print("⚠️ 验证基本通过，但有一些建议改进的地方")
        else:
            print("❌ 验证未通过，建议重新生成或使用 Iterative Refinement 优化")
        
        # 收集所有问题
        all_issues = []
        all_issues.extend(structure_results.get("issues", []))
        all_issues.extend(rules_results.get("issues", []))
        
        if all_issues:
            print("\n📝 需要改进的问题:")
            for issue in all_issues:
                print(f"   - {issue}")
        
        return {
            "final_score": final_score,
            "structure": structure_results,
            "rules": rules_results,
            "style": style_results,
            "content": content_results,
            "all_issues": all_issues
        }


def quick_validate(prompt_text: str):
    """快速验证"""
    validator = PromptValidator()
    return validator.validate_full(prompt_text)


# 使用示例
if __name__ == "__main__":
    # 示例生成的 prompt
    sample_prompt = """
# 角色定义 (Persona)
你现在是「ProView AI 面试官」，一位拥有10年大厂经验的资深面试考官...

# 反幻觉规则
1. 【禁止捏造经历】严格基于真实简历内容或用户回答提问
2. 【禁止自问自答】每次只抛 1-2 个问题后立即停止
3. 【禁止编造技术事实】严禁瞎编不存在的框架、API、技术名词
4. 【禁止出戏】严禁出现"作为 AI 模型"等免责声明

# 面试节奏控制
- 总题量：12-18 题
- 追问深度：3-4 轮

# 输出格式
- 每次回复控制在 200 字以内
- 只提 1-2 个问题后立即停止
"""
    
    # 运行验证
    result = quick_validate(sample_prompt)
