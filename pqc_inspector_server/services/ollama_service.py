# File: pqc_inspector_server/services/ollama_service.py
# 🤖 Ollama AI 모델과 통신하는 서비스입니다.

import ollama
from typing import Dict, Any, Optional
from ..core.config import settings

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = ollama.Client(host=self.base_url)
        print("OllamaService가 초기화되었습니다.")

    async def generate_response(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Ollama 모델에게 프롬프트를 전송하고 응답을 받습니다.
        """
        try:
            print(f"🤖 Ollama 모델 호출 시작: {model}")
            print(f"📝 프롬프트 길이: {len(prompt)} characters")
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                print(f"📋 시스템 프롬프트 길이: {len(system_prompt)} characters")
            
            messages.append({
                "role": "user", 
                "content": prompt
            })

            import time
            start_time = time.time()
            
            response = self.client.chat(
                model=model,
                messages=messages,
                stream=False
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Ollama 응답 완료: {duration:.2f}초")
            print(f"📊 응답 길이: {len(response['message']['content'])} characters")
            print(f"🧠 토큰 사용량 - 입력: {response.get('prompt_eval_count', 0)}, 출력: {response.get('eval_count', 0)}")
            
            return {
                "success": True,
                "content": response['message']['content'],
                "model": model,
                "total_duration": response.get('total_duration', 0),
                "load_duration": response.get('load_duration', 0),
                "prompt_eval_count": response.get('prompt_eval_count', 0),
                "eval_count": response.get('eval_count', 0),
                "actual_duration": duration
            }
            
        except Exception as e:
            print(f"❌ Ollama 모델 '{model}' 호출 중 오류 발생: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    async def check_model_availability(self, model: str) -> bool:
        """
        지정된 모델이 사용 가능한지 확인합니다.
        """
        try:
            models = self.client.list()
            available_models = [m['name'] for m in models['models']]
            return model in available_models
        except Exception as e:
            print(f"모델 '{model}' 확인 중 오류 발생: {e}")
            return False

# 의존성 주입을 위한 함수
def get_ollama_service():
    return OllamaService()