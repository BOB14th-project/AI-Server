# File: pqc_inspector_server/services/preprocessing.py
# 🛠️ 바이너리 파일 분석을 위한 전처리 유틸리티 파일입니다.

import subprocess
import platform

def extract_strings_from_binary(binary_content: bytes) -> str:
    """
    바이너리 데이터에서 의미 있는 문자열들을 추출합니다.
    실제 환경에서는 'strings' 유틸리티를 사용하거나 순수 파이썬으로 구현할 수 있습니다.
    """
    print("바이너리에서 문자열 추출 중...")
    try:
        # OS에 따라 다른 인코딩 사용
        encoding = 'utf-8' if platform.system() != 'Windows' else 'latin-1'
        
        # 임시 파일 없이 메모리에서 처리 (더 안전하고 효율적)
        process = subprocess.Popen(['strings'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=binary_content)
        
        if process.returncode != 0:
            print(f"Strings 명령어 에러: {stderr.decode(encoding, errors='ignore')}")
            return "" # 실패 시 빈 문자열 반환

        return stdout.decode(encoding, errors='ignore')
    except FileNotFoundError:
        print("'strings' 명령어를 찾을 수 없습니다. 간단한 파이썬 기반 추출을 시도합니다.")
        # 'strings'가 없을 경우를 대비한 간단한 폴백(fallback) 로직
        import re
        printable_chars = re.compile(b'[\x20-\x7E]{4,}') # 4글자 이상의 출력 가능한 ASCII 문자열
        found_strings = printable_chars.findall(binary_content)
        return "\n".join(s.decode('ascii', errors='ignore') for s in found_strings)
    except Exception as e:
        print(f"문자열 추출 중 예외 발생: {e}")
        return ""