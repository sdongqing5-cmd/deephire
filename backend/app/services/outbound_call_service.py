"""AI-powered outbound call conversation service"""

from typing import Dict, Any, List, Optional
from openai import OpenAI
from datetime import datetime

from app.core.config import settings


class OutboundCallService:
    """AI-powered outbound call conversation service"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    def generate_call_script(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str,
        recruiter_name: str,
        candidate_background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate personalized outbound call script

        Args:
            candidate_name: Candidate's name
            job_title: Job position title
            company_name: Company name
            recruiter_name: Recruiter's name
            candidate_background: Optional candidate background info

        Returns:
            Call script with opening, key points, and closing
        """
        prompt = f"""
你是一位专业的招聘顾问，需要为以下场景生成一个电话沟通脚本：

候选人信息：
- 姓名：{candidate_name}
- 背景：{candidate_background or '资深专业人士'}

职位信息：
- 职位：{job_title}
- 公司：{company_name}

招聘顾问：{recruiter_name}

请生成一个专业、友好的电话沟通脚本，包括：
1. 开场白（自我介绍、说明来意）
2. 职位介绍要点（3-5个亮点）
3. 询问候选人意向的问题（2-3个）
4. 结束语（下一步安排）

要求：
- 语气专业但不生硬
- 突出职位吸引力
- 尊重候选人时间
- 留有互动空间

以JSON格式返回，包含：opening, key_points, questions, closing
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位经验丰富的招聘顾问，擅长与候选人进行专业、友好的沟通。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            import json
            script = json.loads(response.choices[0].message.content)

            return {
                "success": True,
                "script": script,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def simulate_conversation(
        self,
        script: Dict[str, Any],
        candidate_responses: List[str],
    ) -> Dict[str, Any]:
        """
        Simulate AI conversation based on script and candidate responses

        Args:
            script: Generated call script
            candidate_responses: List of candidate's responses

        Returns:
            Conversation history and analysis
        """
        conversation_history = []

        # Build conversation
        system_prompt = """
你是一位专业的招聘顾问，正在与候选人进行电话沟通。
你需要：
1. 根据候选人的回应灵活调整对话
2. 保持专业和友好的态度
3. 识别候选人的兴趣程度
4. 适时推进对话或结束通话
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": script.get("opening", "")},
        ]

        for response in candidate_responses:
            messages.append({"role": "user", "content": response})

            # Get AI response
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                )

                ai_response = completion.choices[0].message.content
                messages.append({"role": "assistant", "content": ai_response})

                conversation_history.append({
                    "candidate": response,
                    "recruiter": ai_response,
                })

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                }

        # Analyze conversation
        analysis = self._analyze_conversation(conversation_history)

        return {
            "success": True,
            "conversation": conversation_history,
            "analysis": analysis,
        }

    def _analyze_conversation(
        self,
        conversation: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze conversation to determine candidate interest level

        Args:
            conversation: Conversation history

        Returns:
            Analysis results
        """
        # Build analysis prompt
        conversation_text = "\n".join([
            f"候选人: {turn['candidate']}\n招聘顾问: {turn['recruiter']}"
            for turn in conversation
        ])

        prompt = f"""
分析以下招聘电话对话，评估候选人的兴趣程度和下一步建议：

对话内容：
{conversation_text}

请以JSON格式返回分析结果，包括：
1. interest_level: 兴趣程度（high/medium/low）
2. key_signals: 关键信号（正面和负面）
3. next_steps: 建议的下一步行动
4. notes: 其他备注
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位招聘分析专家，擅长从对话中识别候选人的真实意向。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            return {
                "interest_level": "unknown",
                "error": str(e),
            }


# Global service instance
outbound_call_service = OutboundCallService()
