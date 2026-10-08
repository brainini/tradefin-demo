// [단계 판정] n8n Code 노드(Run Once for All Items) — 03 Part1 §8.1 노드 4 + 03 Part2 §5.10 Switch 규칙의 합집합.
// 앱 app/core/dunning.py route()와 같은 규칙이다. 바꾸면 둘 다 고친다(tools/build_day5_agents.py --check가 대조).
//  - 기준일 = Config as_of(= run_date_override 2026-09-30). 비어 있으면 오늘(한국).
//  - 단계: DM3(D-3~D-1) · D7(D+7~14) · D15(D+15~29, C등급은 D+7부터) · D30(D+30~44) · PRE(D+30 이후 + escalation_approved = Y)
//  - 제외: status ≠ open · 신용장·선수금 · 이미 보낸 단계(last_dunning_stage) · 독촉 단계 아님
//  - 사람 처리(HUMAN): 파산·사기 신호(bankruptcy_flag·fraud_flag = 1) · D+45 이후(최고장·추심 위임은 사람이 작성) — 바이어당 한 건으로 묶는다
const cfg = {};
for (const it of $('Config 읽기').all()) {
  const k = String(it.json.key ?? '').trim();
  if (k) cfg[k] = it.json.value;
}
const DAY = 86400000;
function toDate(v) {
  if (v === null || v === undefined || v === '') return null;
  if (typeof v === 'number') return new Date(Date.UTC(1899, 11, 30) + Math.round(v) * DAY);  // 시트 날짜 일련번호
  const s = String(v).trim();
  let m = s.match(/^(\d{4})\s*[-./]\s*(\d{1,2})\s*[-./]\s*(\d{1,2})/);   // 2026-09-30 · 2026. 9. 30.
  if (m) return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);                        // 일/월/연
  if (m) return new Date(Date.UTC(+m[3], +m[2] - 1, +m[1]));
  return null;
}
const ymd = (d) => d.toISOString().slice(0, 10);
const addDays = (d, n) => new Date(d.getTime() + n * DAY);
function todayKst() {
  const p = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  return toDate(p);
}
function fmtAmount(v, ccy) {
  const n = Number(String(v ?? '').replace(/,/g, ''));
  if (!isFinite(n)) return String(v ?? '');
  const d = ccy === 'JPY' ? 0 : 2;
  return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}
function termsText(pm, inv, due) {
  const days = inv && due ? Math.round((due - inv) / DAY) : null;
  return ({ OA: days !== null ? `O/A ${days} days` : 'O/A', DA: days !== null ? `D/A ${days} days` : 'D/A', DP: 'D/P at sight',
    TT_SPLIT_30_70: '30% T/T in advance, 70% within 30 days after B/L' })[pm] ?? pm;
}
const asOf = toDate(cfg.as_of) ?? todayKst();
const STAGE = { DM3: [0, 'T0'], D7: [1, 'T1'], D15: [2, 'T2'], D30: [3, 'T3'], PRE: [4, 'T4'] };
let wl = null;
try { wl = cfg.whitelist_regex ? new RegExp(String(cfg.whitelist_regex)) : null; } catch (e) { wl = null; }
const common = {
  as_of: ymd(asOf), approver_email: String(cfg.approver_email ?? ''), test_recipient: String(cfg.test_recipient ?? ''),
  model_alias: String(cfg.model_alias ?? 'fast-default'), prompt_version: String(cfg.prompt_version ?? 'v1'),
  learner_id: String(cfg.learner_id ?? 'L00'), send_tz: String(cfg.send_tz ?? 'Asia/Seoul'),
  send_window: String(cfg.send_window_local ?? '08:00-21:00'), whitelist_regex: String(cfg.whitelist_regex ?? ''),
};
const out = [];
const human = {};
for (const it of $input.all()) {
  const r = it.json;
  const status = String(r.status ?? 'open').trim().toLowerCase();
  if (status && status !== 'open') continue;
  const pm = String(r.payment_method ?? '').trim();
  if (pm === 'LC_SIGHT' || pm === 'LC_USANCE' || pm === 'TT_ADV') continue;   // 신용장 = 은행 채널 확인, 선수금 = 대상 아님
  const due = toDate(r.due_date);
  if (!due) continue;
  const inv = toDate(r.invoice_date);
  const dpd = Math.round((asOf - due) / DAY);
  const flagged = Number(r.bankruptcy_flag) === 1 || Number(r.fraud_flag) === 1;
  const esc = String(r.escalation_approved ?? '').trim().toUpperCase() === 'Y';
  const grade = String(r.grade ?? '').trim();
  let key = null;
  let why = '';
  if (flagged) why = '파산·사기 신호 — 사람 처리(AI 초안 금지)';
  else if (dpd >= 30 && esc) key = 'PRE';
  else if (dpd >= 45) why = `D+${dpd} — D+45 이후 최고장·추심 위임 검토는 사람이 작성`;
  else if (dpd >= 30) key = 'D30';
  else if (dpd >= 15) key = 'D15';
  else if (dpd >= 7) key = grade === 'C' ? 'D15' : 'D7';
  else if (dpd >= -3 && dpd <= -1) key = 'DM3';
  if (!key && !why) continue;                       // 독촉 단계 아님
  if (!key) {                                        // 사람 처리 — 바이어당 한 건
    if (dpd < -3) continue;                          // 아직 만기 전이면 오늘 할 일 없음
    const b = String(r.buyer_id);
    human[b] = human[b] ?? { ...common, route: 'HUMAN', buyer_id: b, buyer_name: String(r.buyer_name ?? ''), reason: why,
      fraud_type: String(r.fraud_type ?? ''), invoices: [] };
    human[b].invoices.push(`${r.invoice_id}(D${dpd >= 0 ? '+' : ''}${dpd})`);
    continue;
  }
  const [stageNo, tpl] = STAGE[key];
  const lastRaw = r.last_dunning_stage;
  const last = (lastRaw === '' || lastRaw === null || lastRaw === undefined) ? -1 : Number(lastRaw);
  if (stageNo <= last) continue;                     // 이미 보낸 단계 — 중복 발송 방지
  const ccy = String(r.currency ?? '');
  const amount = (r.open_amount_ccy !== '' && r.open_amount_ccy !== undefined && r.open_amount_ccy !== null) ? r.open_amount_ccy : r.amount_ccy;
  const insured = String(r.ksure_insured ?? 'N').toUpperCase() === 'Y' ? 'Y' : 'N';
  const recipient = String(r.contact_email ?? '').trim();
  const nd = toDate(r.ksure_notice_deadline);
  out.push({ json: {
    ...common, route: 'DRAFT', invoice_id: String(r.invoice_id), buyer_id: String(r.buyer_id), buyer_name: String(r.buyer_name ?? ''),
    grade, dpd, stage_key: key, stage_no: stageNo, template: tpl, reason: (key === 'D15' && dpd < 15) ? 'C등급 한 단계 앞당김' : key,
    recipient, whitelist_ok: wl ? wl.test(recipient) : false, insured,
    ksure_notice_deadline: nd ? ymd(nd) : '', notice_days_left: nd ? Math.round((nd - asOf) / DAY) : null,
    facts: {
      company_name: String(cfg.company_name ?? 'Hanbit Precision Co., Ltd. (fictional)'), sender_name: String(cfg.sender_name ?? 'Credit Team'),
      sender_title: String(cfg.sender_title ?? 'Accounts Receivable'), account_manager: String(cfg.account_manager ?? 'your account manager'),
      buyer_name: String(r.buyer_name ?? ''), contact_name: String(r.contact_name ?? '').trim() || 'Accounts Payable Team',
      invoice_id: String(r.invoice_id), invoice_date: inv ? ymd(inv) : '', currency: ccy, amount_ccy: fmtAmount(amount, ccy),
      payment_terms: termsText(pm, inv, due), due_date: ymd(due), days_overdue: String(Math.max(dpd, 0)),
      reply_by_date: ymd(addDays(asOf, 5)), hold_effective_date: ymd(addDays(asOf, 7)), insured,
      escalation_partner: insured === 'Y' ? 'our export credit insurer' : 'our authorised collection partner',
    },
  } });
}
for (const h of Object.values(human)) out.push({ json: { ...h, invoices: h.invoices.join(', ') } });
return out;
