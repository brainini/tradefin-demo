# RAG 코퍼스 — 무엇을 어디서 받나 (Day5)

이 폴더에는 **(가상) 한빛정밀 여신관리규정 한 개만** 들어 있습니다. 나머지 문서는 저작권·재배포 조건 때문에 **링크만** 적습니다 — 각자 공식 사이트에서 받아 내 Gemini Notebook·Dify 지식베이스에 올립니다. 받은 원문이나 변환본을 이 저장소·포크·단체방에 다시 올리지 마세요.

## 1. 문서 목록

| ID 머리 | 문서 | 받는 곳 | 형태 | 쓰는 곳 |
|---|---|---|---|---|
| `HB-` | (가상) 한빛정밀(주) 여신관리규정 — 12장 35조 + 부칙·별표4 | 이 폴더 [`hanbit_credit_policy.md`](hanbit_credit_policy.md) | Markdown(CC BY 4.0) | Notebook · Dify · 앱 ⑥ |
| `KS-` | 한국무역보험공사 「단기수출보험(선적후-일반수출거래 등) 약관」 17차 개정(2024-10-15), 14쪽, 제1~38조 | [약관 PDF 내려받기](https://www.ksure.or.kr/rh-kr/bbs/i-328/down.do?bbs_id=1013&atfile_sn=2&data_ty_cd=A&ntt_sn=65) · [K-SURE 보험약관 게시판](https://www.ksure.or.kr/rh-kr/bbs/i-328/list.do) | PDF(링크만) | Notebook · Dify |
| `LAW-TIA-` | 무역보험법(시행 2026-01-02) | [국가법령정보센터 — 무역보험법](https://www.law.go.kr/법령/무역보험법) | 웹 조문(복사해서 텍스트로 추가) | Notebook · Dify |
| `LAW-FTA-` | 대외무역법(시행 2026-01-02) | [국가법령정보센터 — 대외무역법](https://www.law.go.kr/법령/대외무역법) | 웹 조문 | Notebook · Dify |
| `LAW-CIT-` | 법인세법 시행령 제19조의2(대손금의 범위) | [국가법령정보센터 — 법인세법 시행령](https://www.law.go.kr/법령/법인세법시행령) | 웹 조문 | Notebook · Dify(선택) |
| `CIV-` | 민법 제163조(3년의 단기소멸시효) | [국가법령정보센터 — 민법 제163조](https://www.law.go.kr/법령/민법/제163조) | 웹 조문 | 선택 |
| — | (선택 🔵) K-SURE 「무역보험 제도안내(2026년 8월)」 97쪽 | [K-SURE 자료실](https://www.ksure.or.kr/rh-kr/bbs/i-329/detail.do?ntt_sn=38033) | PDF(링크만) | Notebook만(분량이 큼) |
| — | (선택 🔵) K-SURE 「16가지 사례로 배우는 단기수출보험 보상 가이드」 | [K-SURE 자료실](https://www.ksure.or.kr/rh-kr/bbs/i-329/detail.do?ntt_sn=38019) | PDF(링크만) | Notebook |
| — | (선택 🔵) US EXIM Multi-Buyer Insurance — 청구 안내(영문) | [Filing Claims](https://www.exim.gov/solutions/export-credit-insurance/filing-claims-multi-buyer-insurance-policies) | 웹 | Notebook(한·영 교차 질문) |

**넣지 않는 문서**: ICC UCP 600 · ISBP · URDG · Incoterms 원문. ICC가 AI 학습·텍스트 마이닝 목적의 이용을 명시적으로 금지합니다([ICC 저작권 안내](https://iccwbo.org/copyright-and-trademarks/)). 골든셋의 기권(abstain) 문항으로만 등장합니다.

- 법령 조문은 저작권법 제7조에 따라 보호받지 않는 저작물이라 RAG에 써도 됩니다. 약관·제도안내는 공공기관 저작물이라 자동으로 자유 이용이 되지 않으므로 **링크만** 적습니다.
- 법령은 시행일이 바뀔 수 있습니다. 수업 전날 law.go.kr에서 현행인지 다시 확인합니다.

## 2. 조항 단위로 자르기 (article-aware chunking)

규정·약관은 `제N조(제목) → 항(①②) → 호(1. 2.)` 구조입니다. 검색 단위를 **조(條)** 로 맞추면 검색 결과 첫 줄에 조항 번호가 와서 평가(Hit@3·MRR)를 기록하기 쉽고, 답의 인용도 정확해집니다.

| 설정 | 값 | 이유 |
|---|---|---|
| 문서 형식 | 조 머리를 `## 제N조(제목)` 한 줄로. **조와 조 사이에만 빈 줄**, 조 안의 항·호는 한 줄에 하나 | 빈 줄 = 부모 청크 경계, 줄바꿈 = 자식 청크 경계 |
| Dify 청크 모드 | **Parent-child** — Parent: Paragraph, 구분자 `\n\n`, 최대 1,000 tokens · Child: 구분자 `\n`, 최대 200 tokens | 부모 1개 = 조 1개, 자식 = 항·호 |
| Dify 전처리 | "연속 공백·줄바꿈·탭 치환" **끔** · "URL·이메일 삭제" **끔** | 줄 구조와 조문 속 연락처·링크 보존 |
| 검색 | Hybrid(의미 + 키워드) → **Rerank 켬** → Top K 3 → Score Threshold 0.5 | Dify 문서상 Top K·Threshold는 Rerank를 켜야 적용된다 |
| 미리보기 확인 | "Preview Chunk"에서 부모 1개 = 조 1개인지 | 조 안에 빈 줄이 있으면 조가 둘로 갈라진다 |

- **K-SURE 약관 PDF를 조 단위 Markdown으로**: 프롬프트 라이브러리 **P5-2**(약관 조문 Markdown 변환)로 *각자* 변환해 내 지식베이스에만 올립니다. 변환본은 공유하지 않습니다.
- 앱 ⑥ RAG 페이지는 이 폴더의 `.md`를 같은 규칙(`## 제N조` = 조각 1개)으로 잘라 TF-IDF로 찾습니다. 내 변환본을 화면에서 올리면 그 문서도 같은 방식으로 함께 찾습니다(서버에 저장하지 않음).

## 3. 조항 ID 규칙 (골든셋·평가 시트 공통)

| 문서 | 형식 | 예 |
|---|---|---|
| K-SURE 약관 | `KS-조` · `KS-조항호` | `KS-7①2`(제7조 제1항 제2호) · `KS-22의2` |
| 한빛 여신관리규정 | `HB-조` · `HB-조항` · `HB-별표N` | `HB-27②` · `HB-별표1` |
| 법인세법 시행령 | `LAW-CIT-조항호` | `LAW-CIT-19의2①7` |
| 민법 | `CIV-조-호` | `CIV-163-6` |

- 검색 지표(Hit@3·MRR)는 **조 단위**로 맞춥니다(`HB-27②` → `HB-27`). Dify 부모 청크가 조 하나이기 때문입니다. 답의 정확성(항·호까지 맞는지)은 사람이 채점합니다.
- 골든셋: [`../goldset_20.csv`](../goldset_20.csv) · 평가 시트: [`../eval_sheet_template.xlsx`](../eval_sheet_template.xlsx)
