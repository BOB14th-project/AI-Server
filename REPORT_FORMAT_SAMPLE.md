# PQC Inspector 보고서 형식 샘플

**프론트엔드 개발팀을 위한 보고서 구조 가이드**

---

## 🎯 개요

이 문서는 AI Server가 생성하는 보고서의 정확한 형식을 보여줍니다.
프론트엔드에서는 이 3개 카테고리를 파싱하여 UI에 표시하면 됩니다.

**3개 주요 카테고리:**
1. `# 1. 스캔 대상` - 파일 정보와 검사 범위
2. `# 2. 상세 내용` - 발견된 취약점과 기술 분석
3. `# 3. 전환 가이드` - 실행 가능한 조치 사항

---

## 📄 실제 보고서 예시

아래는 AI Orchestrator가 생성하는 실제 보고서 형식입니다:

---

# 1. 스캔 대상

**File ID**: 1
**Scan ID**: 1

## 1.1 파일 정보
- **분석 대상 파일**: weakcrypto_win.exe
- **파일 타입**: 어셈블리 바이너리 (x86-64)
- **파일 크기**: 147,244 bytes
- **분석 일시**: 2025-11-19 15:27:00 (KST)

## 1.2 검사 범위
- **검사한 암호 알고리즘**: RSA, AES, DES, ECDSA, SHA, MD5
- **분석 레벨**: 어셈블리 레벨 (바이너리 디스어셈블)
- **사용된 AI 에이전트**: AssemblyBinaryAgent

## 1.3 전체 요약
- **보안 상태**: 위험 ⚠️
- **PQC 취약점 발견**: 예
- **위험도 등급**: High
- **종합 신뢰도**: 0.85

---

# 2. 상세 내용

## 2.1 발견된 취약점

### 취약점 #1: RSA-2048
- **심각도**: High
- **발견 위치**: 어셈블리 코드 (OpenSSL 라이브러리 호출)
- **탐지 근거**:
  ```c
  RSA_generate_key_ex() 함수 호출 패턴 발견
  2048비트 키 생성 확인
  ```
- **양자컴퓨터 위협**: Shor 알고리즘에 의해 다항 시간 내 인수분해 가능
- **예상 피해**:
  - 암호화된 통신 내용 노출
  - 전자서명 위조 가능
  - 중간자 공격(MITM)에 취약

### 취약점 #2: AES-128
- **심각도**: Medium
- **발견 위치**: 어셈블리 코드
- **탐지 근거**: AES 암호화 루틴 탐지 (128비트 키)
- **양자컴퓨터 위협**: Grover 알고리즘으로 실효 키 길이 64비트로 감소
- **예상 피해**:
  - 양자컴퓨터 환경에서 브루트포스 공격 시간 단축
  - 장기 보안성 부족

## 2.2 기술적 분석

### 어셈블리 레벨 분석
- **분석 결과**:
  - OpenSSL libcrypto.so.3 라이브러리 사용 확인
  - RSA_new(), BN_set_word(), RSA_generate_key_ex() 함수 호출 발견
  - 2048비트 키 길이 상수 확인
- **암호 함수 호출**:
  - `RSA_generate_key_ex@OPENSSL_3.0.0`
  - `BN_set_word@OPENSSL_3.0.0`
  - `RSA_free@OPENSSL_3.0.0`
- **코드 패턴**: 표준 OpenSSL RSA 키 생성 패턴 사용

### 소스코드 레벨 분석
- **분석 결과**: 소스코드 데이터 없음
- **라이브러리 사용**: N/A
- **구현 방식**: N/A

### 로그/설정 분석
- **분석 결과**: 로그 데이터 없음
- **설정 이슈**: N/A
- **로그 패턴**: N/A

## 2.3 종합 평가
- **전반적 보안 수준**: 현재 클래식 컴퓨터 환경에서는 안전하나, 양자컴퓨터 시대에는 취약
- **주요 위험 요소**:
  - RSA-2048 의존도가 높음
  - 양자내성 암호 적용 계획 없음
- **긍정적 요소**:
  - OpenSSL 최신 버전 사용 (3.0.0)
  - 표준 라이브러리 활용으로 구현 안정성 확보

---

# 3. 전환 가이드

## 3.1 즉시 조치 필요 사항 (High Priority)
1. **RSA-2048 키 교환 프로토콜 개선**:
   - 현재: RSA-2048 키 교환
   - 조치: 하이브리드 방식 도입 (RSA-2048 + CRYSTALS-Kyber)
   - 예상 기간: 1-2개월

2. **AES-128 → AES-256 전환**:
   - 현재: AES-128 (양자컴퓨터 환경에서 64비트 실효 보안)
   - 조치: AES-256으로 즉시 전환 (128비트 실효 보안 확보)
   - 예상 기간: 1주일

## 3.2 양자내성 암호 전환 로드맵

### 단기 계획 (1-3개월)
1. **현재 암호 → PQC 암호 매핑**
   - RSA-2048 → CRYSTALS-Kyber-768 (키 교환)
   - ECDSA → CRYSTALS-Dilithium-3 (전자서명)
   - AES-128 → AES-256 (대칭키 강화)

2. **마이그레이션 우선순위**
   - [High] 키 교환 프로토콜 (TLS 핸드셰이크)
   - [Medium] 전자서명 검증 시스템
   - [Low] 레거시 API 호환성 유지

### 중기 계획 (3-6개월)
1. **하이브리드 암호 시스템 도입**
   - 기존 RSA + PQC Kyber 병행 운영
   - 점진적 전환을 통한 안정성 확보
   - 상호운용성 테스트 완료

2. **테스트 및 검증**
   - 성능 테스트: TLS 핸드셰이크 시간 측정
   - 호환성 검증: 기존 클라이언트와의 통신 보장
   - 보안 감사: 외부 보안 전문가 리뷰

### 장기 계획 (6-12개월)
1. **완전한 PQC 전환**
   - 모든 레거시 RSA/ECDSA 제거
   - NIST PQC 표준 완전 준수
   - 지속적 모니터링 체계 구축

## 3.3 권장 라이브러리 및 도구
- **NIST PQC 표준 라이브러리**:
  - liboqs 0.9.0+ (Open Quantum Safe)
  - PQClean (검증된 참조 구현)
  - Bouncy Castle PQC (Java 환경)

- **호환성 도구**:
  - OQS-OpenSSL 1.1.1 (OpenSSL + PQC 통합)
  - OQS-BoringSSL (Google BoringSSL 기반)

- **모니터링 도구**:
  - PQC Inspector (현재 사용 중)
  - QuantumSafe Scanner

## 3.4 추가 리소스
- **NIST PQC 프로젝트**: https://csrc.nist.gov/projects/post-quantum-cryptography
- **마이그레이션 가이드**:
  - "Transitioning to Post-Quantum Cryptography" (NIST SP 800-208)
  - Open Quantum Safe Wiki: https://openquantumsafe.org/
- **기술 지원**:
  - PQC Inspector GitHub Issues
  - Open Quantum Safe Discussion Forum

---

**리포트 작성 완료**
**생성 일시**: 2025-11-19 15:27:11 (KST)
**담당 AI**: PQC Inspector AI Orchestrator

---

## 🔧 프론트엔드 파싱 가이드

### JavaScript 파싱 예제

```javascript
// DB에서 리포트 가져오기
const reportResponse = await fetch(
  'https://harper-abler-agape.ngrok-free.dev/files/1/llm_analysis/?scan_id=1'
);
const reportData = await reportResponse.json();
const reportMarkdown = reportData[0].LLM_analysis;

// 3개 카테고리 분리
function parseReport(markdown) {
  const sections = {};

  // 1. 스캔 대상
  const scanTargetMatch = markdown.match(/# 1\. 스캔 대상([\s\S]*?)(?=# 2\. 상세 내용)/);
  sections.scanTarget = scanTargetMatch ? scanTargetMatch[1].trim() : '';

  // 2. 상세 내용
  const detailsMatch = markdown.match(/# 2\. 상세 내용([\s\S]*?)(?=# 3\. 전환 가이드)/);
  sections.details = detailsMatch ? detailsMatch[1].trim() : '';

  // 3. 전환 가이드
  const guideMatch = markdown.match(/# 3\. 전환 가이드([\s\S]*?)(?=---\s*\*\*리포트 작성 완료)/);
  sections.migrationGuide = guideMatch ? guideMatch[1].trim() : '';

  return sections;
}

// 사용 예시
const parsedReport = parseReport(reportMarkdown);
console.log('스캔 대상:', parsedReport.scanTarget);
console.log('상세 내용:', parsedReport.details);
console.log('전환 가이드:', parsedReport.migrationGuide);
```

### React 컴포넌트 예제

```jsx
import ReactMarkdown from 'react-markdown';

function SecurityReport({ reportMarkdown }) {
  const sections = parseReport(reportMarkdown);

  return (
    <div className="security-report">
      {/* 탭 UI */}
      <Tabs>
        <Tab label="스캔 대상">
          <ReactMarkdown>{sections.scanTarget}</ReactMarkdown>
        </Tab>
        <Tab label="상세 내용">
          <ReactMarkdown>{sections.details}</ReactMarkdown>
        </Tab>
        <Tab label="전환 가이드">
          <ReactMarkdown>{sections.migrationGuide}</ReactMarkdown>
        </Tab>
      </Tabs>
    </div>
  );
}
```

### 마크다운 헤더 기반 파싱 (더 안정적)

```javascript
function parseReportByHeaders(markdown) {
  const lines = markdown.split('\n');
  const sections = {
    scanTarget: [],
    details: [],
    migrationGuide: []
  };

  let currentSection = null;

  for (const line of lines) {
    if (line.startsWith('# 1. 스캔 대상')) {
      currentSection = 'scanTarget';
    } else if (line.startsWith('# 2. 상세 내용')) {
      currentSection = 'details';
    } else if (line.startsWith('# 3. 전환 가이드')) {
      currentSection = 'migrationGuide';
    } else if (line.includes('**리포트 작성 완료**')) {
      currentSection = null;
    } else if (currentSection) {
      sections[currentSection].push(line);
    }
  }

  return {
    scanTarget: sections.scanTarget.join('\n').trim(),
    details: sections.details.join('\n').trim(),
    migrationGuide: sections.migrationGuide.join('\n').trim()
  };
}
```

---

## 📊 각 카테고리 활용 방법

### 1. 스캔 대상 (Scan Target)
**UI 배치**: 대시보드 상단 요약 카드
- 파일 정보 → 테이블 형식
- 검사 범위 → 뱃지/태그 형식
- 전체 요약 → 컬러 인디케이터 (위험=빨강, 주의=노랑, 양호=초록)

### 2. 상세 내용 (Details)
**UI 배치**: 메인 콘텐츠 영역
- 발견된 취약점 → 아코디언/확장 가능 카드
- 기술적 분석 → 코드 블록 스타일
- 종합 평가 → 하이라이트 박스

### 3. 전환 가이드 (Migration Guide)
**UI 배치**: 실행 가능 액션 영역
- 즉시 조치 → 체크리스트 형식
- 로드맵 → 타임라인 차트
- 권장 라이브러리 → 링크 버튼

---

**문서 작성**: 2025-11-19 15:30 (KST)
**작성자**: PQC Inspector AI Team
