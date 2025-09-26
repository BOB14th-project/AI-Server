# File: pqc_inspector_server/services/model_loader.py
# 🧠 LLM 모델을 메모리에 로드하고 관리하는 파일입니다.
# 무거운 모델을 한 번만 로드하여 재사용함으로써 성능을 최적화합니다.

from functools import lru_cache
from typing import Any

# 가상의 모델 객체를 시뮬레이션하기 위한 클래스
class MockLanguageModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        print(f"'{self.model_path}'에서 무거운 모델을 로딩합니다... (시뮬레이션)")
        # 실제로는 여기서 transformers 라이브러리 등을 사용하여 모델을 로드합니다.
        # from transformers import AutoModelForCausalLM, AutoTokenizer
        # self.model = AutoModelForCausalLM.from_pretrained(model_path)
        # self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("모델 로딩 완료.")
    
    def predict(self, text: str) -> str:
        print(f"모델 '{self.model_path}'로 예측 수행: {text[:50]}...")
        return "모델의 예측 결과 (시뮬레이션)"

@lru_cache(maxsize=4) # 최대 4개의 모델을 캐싱
def get_model(model_path: str) -> Any:
    """
    주어진 경로의 언어 모델을 로드하고 캐싱합니다.
    동일한 경로의 모델은 다시 로드하지 않고 캐시된 객체를 반환합니다.
    """
    return MockLanguageModel(model_path)
