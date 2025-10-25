# File: pqc_inspector_server/services/ai_service.py
# 🤖 상용 AI API (GPT-4.1, Gemini 2.5 Flash)와 통신하는 서비스입니다.

import httpx
import json
from typing import Dict, Any, Optional
from ..core.config import settings

class AIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.google_api_key = settings.GOOGLE_API_KEY
        self.openai_base_url = "https://api.openai.com/v1"
        self.google_base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        print("AIService가 초기화되었습니다.")

    async def generate_response(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        상용 AI 모델에게 프롬프트를 전송하고 응답을 받습니다.
        """
        try:
            print(f"🤖 AI 모델 호출 시작: {model}")
            print(f"📝 프롬프트 길이: {len(prompt)} characters")

            import time
            start_time = time.time()

            if model.startswith("gpt-"):
                response = await self._call_openai(model, prompt, system_prompt)
            elif model.startswith("gemini-"):
                response = await self._call_google(model, prompt, system_prompt)
            elif ":" in model:  # Ollama 모델 (예: llama3:8b)
                response = await self._call_ollama(model, prompt, system_prompt)
            else:
                raise ValueError(f"지원하지 않는 모델: {model}")

            end_time = time.time()
            duration = end_time - start_time

            print(f"✅ AI 응답 완료: {duration:.2f}초")
            print(f"📊 응답 길이: {len(response.get('content', ''))} characters")

            response["actual_duration"] = duration
            return response

        except Exception as e:
            print(f"❌ AI 모델 '{model}' 호출 중 오류 발생: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    async def _call_openai(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """OpenAI API 호출"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.1
                },
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["choices"][0]["message"]["content"],
                    "model": model,
                    "usage": data.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"OpenAI API 오류: {response.status_code} - {response.text}",
                    "content": None
                }

    async def _call_google(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Google Gemini API 호출"""
        # Gemini API는 시스템 프롬프트를 사용자 프롬프트와 함께 처리
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.google_base_url}/models/{model}:generateContent",
                headers={
                    "Content-Type": "application/json"
                },
                params={"key": self.google_api_key},
                json={
                    "contents": [{
                        "parts": [{"text": full_prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 4096
                    }
                },
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "success": True,
                        "content": content,
                        "model": model,
                        "usage": data.get("usageMetadata", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": "Google API에서 유효한 응답을 받지 못했습니다",
                        "content": None
                    }
            else:
                return {
                    "success": False,
                    "error": f"Google API 오류: {response.status_code} - {response.text}",
                    "content": None
                }

    async def _call_ollama(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Ollama API 호출"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/chat",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.1
                    }
                },
                timeout=120.0
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["message"]["content"],
                    "model": model,
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API 오류: {response.status_code} - {response.text}",
                    "content": None
                }

# 의존성 주입을 위한 함수
def get_ai_service():
    return AIService()