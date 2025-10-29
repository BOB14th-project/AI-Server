# Logs/Config 에이전트 지식 베이스 확장 자료

## 📚 추천 공식 문서 및 리소스

### 1️⃣ TLS/SSL 관련 공식 문서

#### **RFC 문서 (가장 권위있는 표준)**
- **RFC 5246** - TLS 1.2 Protocol
  - URL: https://datatracker.ietf.org/doc/html/rfc5246
  - 내용: TLS 1.2 cipher suites, handshake 프로토콜
  - 추출 가능: Cipher suite 목록, 알고리즘 매핑

- **RFC 8446** - TLS 1.3 Protocol
  - URL: https://datatracker.ietf.org/doc/html/rfc8446
  - 내용: TLS 1.3 개선사항, cipher suite 변경
  - 추출 가능: 제거된 cipher suites (RSA 키 교환 등)

- **RFC 7525** - TLS Recommendations
  - URL: https://datatracker.ietf.org/doc/html/rfc7525
  - 내용: 보안 TLS 구성 권장사항
  - 추출 가능: 취약한 cipher suites 목록

#### **IANA Registry (공식 Cipher Suite 목록)**
- **TLS Cipher Suite Registry**
  - URL: https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml
  - 내용: 공식 등록된 모든 TLS cipher suites
  - 추출 가능:
    - TLS_RSA_* (양자 취약)
    - TLS_ECDHE_RSA_* (양자 취약)
    - TLS_ECDHE_ECDSA_* (양자 취약)
    - TLS_DHE_* (양자 취약)

---

### 2️⃣ 웹 서버 설정 문서

#### **Apache HTTP Server**
- **mod_ssl 문서**
  - URL: https://httpd.apache.org/docs/current/mod/mod_ssl.html
  - 내용: SSLCipherSuite, SSLProtocol 설정
  - 추출 가능:
    ```apache
    SSLCipherSuite HIGH:!aNULL:!MD5:!3DES
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    ```

- **Apache SSL/TLS 로그**
  - URL: https://httpd.apache.org/docs/current/logs.html
  - 내용: SSL handshake 로그 형식
  - 추출 가능: 로그 패턴 예시

#### **Nginx**
- **ngx_http_ssl_module**
  - URL: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
  - 내용: ssl_protocols, ssl_ciphers 설정
  - 추출 가능:
    ```nginx
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ```

- **Nginx SSL 로그**
  - 내용: $ssl_protocol, $ssl_cipher 변수
  - 추출 가능: 로그 포맷 예시

#### **Mozilla SSL Configuration Generator**
- URL: https://ssl-config.mozilla.org/
- 내용: 최신 권장 SSL/TLS 설정
- 추출 가능:
  - Modern (TLS 1.3만)
  - Intermediate (TLS 1.2+)
  - Old (레거시)
  - 각 설정의 cipher suite 목록

---

### 3️⃣ SSH 관련 문서

#### **OpenSSH 문서**
- **sshd_config 매뉴얼**
  - URL: https://man.openbsd.org/sshd_config
  - 내용: HostKeyAlgorithms, PubkeyAcceptedKeyTypes
  - 추출 가능:
    ```ssh
    HostKeyAlgorithms ssh-rsa,ecdsa-sha2-nistp256
    PubkeyAcceptedKeyTypes ssh-rsa,ssh-dss,ecdsa-sha2-*
    KexAlgorithms diffie-hellman-*,ecdh-sha2-*
    ```

- **RFC 4253** - SSH Transport Layer Protocol
  - URL: https://datatracker.ietf.org/doc/html/rfc4253
  - 내용: SSH 프로토콜, 키 교환 알고리즘
  - 추출 가능: 알고리즘 목록

#### **SSH 로그 패턴**
- **sshd 로그 형식**
  - 위치: /var/log/auth.log, /var/log/secure
  - 패턴 예시:
    ```
    Server host key: ssh-rsa SHA256:...
    User authentication: publickey (ssh-rsa)
    Connection accepted for user@host
    ```

---

### 4️⃣ 인증서 관련 문서

#### **X.509 인증서 표준**
- **RFC 5280** - X.509 Certificate and CRL Profile
  - URL: https://datatracker.ietf.org/doc/html/rfc5280
  - 내용: 인증서 구조, 서명 알고리즘
  - 추출 가능:
    - sha256WithRSAEncryption
    - ecdsa-with-SHA256
    - rsaEncryption

#### **OpenSSL 인증서 관련**
- **OpenSSL 명령어 문서**
  - URL: https://www.openssl.org/docs/
  - 내용: 인증서 생성, 검증 로그
  - 추출 가능:
    ```
    Signature Algorithm: sha256WithRSAEncryption
    Public Key Algorithm: rsaEncryption
    RSA Public-Key: (2048 bit)
    ```

---

### 5️⃣ JWT/API 보안 문서

#### **RFC 7519** - JSON Web Token (JWT)
- URL: https://datatracker.ietf.org/doc/html/rfc7519
- 내용: JWT 구조, 알고리즘
- 추출 가능:
  ```json
  "alg": "RS256"  // RSA PKCS#1 signature (양자 취약)
  "alg": "ES256"  // ECDSA signature (양자 취약)
  "alg": "PS256"  // RSA PSS signature (양자 취약)
  ```

#### **RFC 7518** - JSON Web Algorithms (JWA)
- URL: https://datatracker.ietf.org/doc/html/rfc7518
- 내용: JWT에서 사용되는 암호화 알고리즘 목록
- 추출 가능:
  - RS256, RS384, RS512 (RSA 서명)
  - ES256, ES384, ES512 (ECDSA 서명)
  - PS256, PS384, PS512 (RSA-PSS 서명)

---

### 6️⃣ 클라우드 서비스 문서

#### **AWS KMS (Key Management Service)**
- **AWS KMS 로그**
  - URL: https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html
  - 내용: CloudTrail 로그 형식
  - 추출 가능:
    ```json
    "eventName": "CreateKey",
    "requestParameters": {
      "keySpec": "RSA_2048"  // 양자 취약
    }
    ```

#### **Azure Key Vault**
- **Azure 진단 로그**
  - URL: https://docs.microsoft.com/en-us/azure/key-vault/general/logging
  - 내용: Key Vault 로그 스키마
  - 추출 가능:
    ```json
    "properties": {
      "keyType": "RSA",
      "keySize": 2048
    }
    ```

#### **GCP Cloud KMS**
- **Cloud Audit Logs**
  - URL: https://cloud.google.com/kms/docs/audit-logging
  - 내용: KMS 작업 로그
  - 추출 가능:
    ```json
    "cryptoKeyVersion": {
      "algorithm": "RSA_SIGN_PSS_2048_SHA256"
    }
    ```

---

### 7️⃣ 데이터베이스 SSL/TLS 설정

#### **PostgreSQL**
- **SSL Support**
  - URL: https://www.postgresql.org/docs/current/ssl-tcp.html
  - 내용: ssl_ciphers, ssl_min_protocol_version
  - 추출 가능: 설정 파일 패턴

#### **MySQL/MariaDB**
- **SSL/TLS Connection**
  - URL: https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html
  - 내용: ssl-cipher, tls-version
  - 추출 가능: 설정 및 로그 패턴

#### **MongoDB**
- **TLS/SSL Configuration**
  - URL: https://www.mongodb.com/docs/manual/tutorial/configure-ssl/
  - 내용: net.tls.mode, net.tls.certificateKeyFile
  - 추출 가능: 설정 파일 형식

---

### 8️⃣ NIST 및 보안 가이드라인

#### **NIST SP 800-52 Rev.2**
- **TLS 가이드라인**
  - URL: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-52r2.pdf
  - 내용: 연방 정부 TLS 구성 권장사항
  - 추출 가능: 승인/비승인 cipher suites

#### **NIST Post-Quantum Cryptography**
- **PQC 표준화**
  - URL: https://csrc.nist.gov/projects/post-quantum-cryptography
  - 내용: 양자내성 알고리즘 표준
  - 추출 가능: 마이그레이션 가이드

#### **OWASP Transport Layer Protection**
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html
- 내용: 안전한 TLS 구성
- 추출 가능: 취약한 설정 목록

---

## 🎯 우선순위 및 구현 계획

### Phase 1: 즉시 추가 가능 (웹에서 다운로드)

#### **1. IANA TLS Cipher Suite Registry**
- **작업:** CSV/JSON 다운로드
- **추출 내용:**
  - RSA 키 교환 cipher suites
  - ECDHE-RSA cipher suites
  - ECDHE-ECDSA cipher suites
  - DHE cipher suites
- **예상 패턴 수:** 50-100개

#### **2. Mozilla SSL Configuration**
- **작업:** 웹 스크래핑 또는 수동 복사
- **추출 내용:**
  - Modern/Intermediate/Old 프로파일
  - 각 프로파일의 cipher suites
  - Apache/Nginx/HAProxy 설정 예시
- **예상 패턴 수:** 20-30개

#### **3. OpenSSH sshd_config 매뉴얼**
- **작업:** 매뉴얼 페이지에서 추출
- **추출 내용:**
  - HostKeyAlgorithms 옵션
  - PubkeyAcceptedKeyTypes 옵션
  - KexAlgorithms 옵션
- **예상 패턴 수:** 15-20개

---

### Phase 2: 로그 샘플 수집 (실제 로그)

#### **웹 서버 로그 샘플**
```
Apache SSL 로그:
[ssl:info] [pid 1234] SSL Cipher Suite: ECDHE-RSA-AES256-GCM-SHA384
[ssl:info] [pid 1234] SSL Protocol: TLSv1.2

Nginx 로그:
2024/01/01 12:00:00 [info] SSL: TLSv1.2, cipher: "ECDHE-RSA-AES256-GCM-SHA384"
```

#### **SSH 로그 샘플**
```
/var/log/auth.log:
Jan 1 12:00:00 sshd[1234]: Server listening on :: port 22.
Jan 1 12:01:00 sshd[1234]: Connection from 192.168.1.100 port 54321
Jan 1 12:01:01 sshd[1234]: Server host key: ssh-rsa SHA256:...
Jan 1 12:01:02 sshd[1234]: Accepted publickey for user from 192.168.1.100 port 54321 ssh2: RSA SHA256:...
```

#### **인증서 로그 샘플**
```
OpenSSL x509 출력:
Certificate:
    Signature Algorithm: sha256WithRSAEncryption
    Public Key Algorithm: rsaEncryption
        RSA Public-Key: (2048 bit)
```

---

### Phase 3: 클라우드 서비스 로그 (선택사항)

#### **AWS CloudTrail 로그**
```json
{
  "eventName": "CreateKey",
  "requestParameters": {
    "keySpec": "RSA_2048",
    "keyUsage": "SIGN_VERIFY"
  }
}
```

---

## 📝 구현 방법

### 방법 1: 웹 스크래핑 (자동화)

```python
# scripts/fetch_public_docs.py
import requests
from bs4 import BeautifulSoup

# IANA TLS Cipher Suites
response = requests.get('https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml')
# 파싱 후 JSON으로 저장
```

### 방법 2: 수동 작성 (추천)

각 공식 문서를 읽고 중요한 패턴만 추출하여 JSON 작성:

```json
{
  "log_patterns": [
    {
      "type": "log_pattern",
      "category": "Apache_SSL_Log",
      "content": "Apache SSL 로그 패턴: '[ssl:info] SSL Cipher Suite: ECDHE-RSA-AES256-GCM-SHA384'. ECDHE-RSA는 RSA 인증서를 사용하므로 양자 취약.",
      "confidence": 0.95,
      "source": "Apache_mod_ssl_docs",
      "keywords": ["ssl:info", "Cipher Suite", "ECDHE-RSA"]
    }
  ]
}
```

### 방법 3: PDF/문서 처리 (고급)

```python
# PyPDF2 또는 pdfplumber로 RFC PDF 파싱
import pdfplumber

with pdfplumber.open('rfc5246.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        # Cipher suite 목록 추출
```

---

## 🎯 목표

**현재:** 7개 (logs_config) + 59개 (common) = 66개 패턴 실사용
**목표:** 100-150개 실제 로그/설정 패턴

**예상 개선:**
- F1 Score: 0.273 → 0.400+
- Logs/Config 전용 패턴 확보로 정확도 대폭 향상

---

## 💡 제 추천

**즉시 구현 가능한 우선순위:**

1. **IANA TLS Cipher Suite Registry** (웹에서 다운로드 가능)
2. **Mozilla SSL Configuration** (공개된 설정)
3. **OpenSSH 매뉴얼** (man page에서 추출)
4. **실제 로그 샘플** (Apache, Nginx, SSH 로그 예시)

이 4가지만 해도 **50-70개 고품질 패턴**을 추가할 수 있습니다!

작업을 진행해드릴까요?
