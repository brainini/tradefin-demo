// [가드레일] n8n Code 노드(Run Once for Each Item) — LLM 초안 JSON을 꺼내 5가지를 검사한다. 앱 app/core/guardrails.py와 같은 규칙.
//  ① 금지 표현(법적 절차·국가기관·위협 + 계좌 변경 문구) ② 단계별 필수 요소 ③ 180단어 이하 ④ 수신자 화이트리스트 ⑤ 발송 시간창(현지 08–21시)
const row = $('단계 판정').item.json;
const raw = String($json.text ?? $json.output ?? $json.response ?? '');
function extract(t) {
  const s = t.replace(/```(?:json)?/g, '');
  let start = s.indexOf('{');
  while (start !== -1) {
    let depth = 0;
    for (let j = start; j < s.length; j++) {
      if (s[j] === '{') depth++;
      else if (s[j] === '}') { depth--; if (depth === 0) { try { return JSON.parse(s.slice(start, j + 1)); } catch (e) { break; } } }
    }
    start = s.indexOf('{', start + 1);
  }
  return null;
}
const obj = extract(raw) ?? {};
const subject = String(obj.subject ?? '').trim();
const body = String(obj.body ?? '').trim();
const summaryKo = String(obj.summary_ko ?? '').trim();
const text = `${subject}\n${body}`;
const BLOCK = /(legal action|legal proceedings|\bcourt\b|\blawsuit\b|\bsue\b|\bsuing\b|attorney|lawyer|police|criminal|prosecut|\bseiz|garnish|blacklist|credit bureau|report you to|arrest|interpol)/gi;
const BLOCK_KO = /(법원|경찰|검찰|형사|고소|소송|압류|체포|신용불량|블랙리스트|법적 조치)/g;
const BANK = /(new (bank )?account|updated? bank|change[sd]? (of |in |to )?(our |the )?bank|bank (account )?details? (have|has) changed|\biban\b|swift code|account number|routing number)/gi;
const bad = [...new Set([...(text.match(BLOCK) ?? []), ...(text.match(BLOCK_KO) ?? []), ...(text.match(BANK) ?? [])])];
const f = row.facts;
const miss = [];
if (!body) miss.push('본문 없음(JSON 형식 오류)');
if (f.invoice_id && !body.includes(f.invoice_id)) miss.push('인보이스 번호');
const core = String(f.amount_ccy).replace(/,/g, '').split('.')[0];
if (core && !body.replace(/[^\d]/g, '').includes(core)) miss.push('금액');
if (['DM3', 'D7', 'D15', 'D30'].includes(row.stage_key) && !body.includes(f.due_date)) miss.push('결제기일');
if (row.stage_key === 'D7' && !/disregard/i.test(body)) miss.push("'이미 지급했으면 무시' 문장");
if (['D15', 'D30', 'PRE'].includes(row.stage_key) && !body.includes(f.reply_by_date)) miss.push('회신 기한');
if (row.stage_key === 'D30' && !/hold/i.test(body)) miss.push('선적 보류 고지');
if (row.stage_key === 'PRE' && !body.includes(f.escalation_partner)) miss.push('이관 대상');
const words = body.split(/\s+/).filter(Boolean).length;
let wlOk = false;
try { wlOk = row.whitelist_regex ? new RegExp(row.whitelist_regex).test(row.recipient) : false; } catch (e) { wlOk = false; }
const [h0, h1] = String(row.send_window || '08:00-21:00').split('-').map((x) => parseInt(x, 10));
const hour = parseInt(new Intl.DateTimeFormat('en-US', { timeZone: row.send_tz || 'Asia/Seoul', hour: 'numeric', hourCycle: 'h23' }).format(new Date()), 10);
const inWindow = hour >= h0 && hour < h1;
const checks = [
  { check: '① 금지 표현', ok: bad.length === 0, detail: bad.join(', ') || '없음' },
  { check: '② 필수 요소', ok: miss.length === 0, detail: miss.join(', ') || '모두 있음' },
  { check: '③ 길이 ≤ 180단어', ok: words <= 180, detail: `${words}단어` },
  { check: '④ 수신자 화이트리스트', ok: wlOk, detail: row.recipient },
];
const pass = checks.every((c) => c.ok);
const fails = checks.filter((c) => !c.ok).map((c) => c.check.split(' ')[0]);
return { json: {
  ...row, subject, body, summary_ko: summaryKo, checks, guardrail_pass: pass, in_window: inWindow, local_hour: hour,
  guardrail_result: pass ? (inWindow ? 'pass' : 'pass(발송 시간창 밖 → 08:00까지 대기)') : `fail:${fails.join(',')}`,
  checks_text: checks.map((c) => `${c.ok ? '✅' : '❌'} ${c.check}: ${c.detail}`).join('\n'),
} };
