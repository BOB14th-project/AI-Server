# File: pqc_inspector_server/services/reporting.py
# 📄 분석 결과를 바탕으로 사용자 친화적인 보고서를 생성하는 로직을 담은 파일입니다.

from typing import List, Dict, Any
from datetime import datetime

def generate_markdown_report(analysis_results: List[Dict[str, Any]]) -> str:
    """
    DB에서 가져온 여러 분석 결과들을 종합하여 마크다운 형식의 보고서를 생성합니다.
    """
    if not analysis_results:
        return "# 분석 결과 보고서\n\n해당 기간의 분석 결과가 없습니다."

    report_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    total_files = len(analysis_results)
    non_pqc_count = sum(1 for r in analysis_results if r.get("pqc_status") == "non-pqc")

    # 보고서 헤더 생성
    report = f"# PQC Inspector 분석 결과 보고서\n\n"
    report += f"- **보고서 생성 시각**: {report_time}\n"
    report += f"- **총 분석 파일 수**: {total_files}개\n"
    report += f"- **Non-PQC 탐지 수**: {non_pqc_count}개\n\n"
    report += "---\n\n"

    # 각 탐지 항목 상세 정보 추가
    report += "## 📝 상세 탐지 내역\n\n"
    report += "| 파일명 | 파일 타입 | 탐지 상태 | 탐지 알고리즘 | 근거 |\n"
    report += "|---|---|---|---|---|\n"

    for result in analysis_results:
        file_name = result.get('file_name', 'N/A')
        file_type = result.get('file_type', 'N/A')
        pqc_status = result.get('pqc_status', 'N/A')
        algorithm = result.get('detected_algorithm', 'N/A')
        evidence = result.get('evidence', 'N/A').replace('\n', '<br>')
        report += f"| {file_name} | {file_type} | **{pqc_status}** | {algorithm} | {evidence} |\n"
    
    return report