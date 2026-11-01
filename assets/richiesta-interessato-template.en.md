# Handling a data-subject request (GDPR arts. 12–22)

> English edition of `richiesta-interessato-template.md`. Working template for the controller. It is not legal advice and does not replace the DPO's opinion: text in [BRACKETS] must be completed, and the decisions (grant, restrict, refuse) belong to the controller. The deadlines below are those of the GDPR; check any national rules. In Italy the supervisory authority is the Garante per la protezione dei dati personali; elsewhere name the competent authority.

## 1. Request sheet (fill in at once)
| Field | Value |
|---|---|
| Internal number and date received | [TO COMPLETE] |
| Channel | [email / registered email / post / front desk] |
| Requester (name and contact) | [TO COMPLETE] |
| Right exercised | access (art. 15) · rectification (16) · erasure (17) · restriction (18) · portability (20) · objection (21) · other: [ ] |
| Identity verified on / by what means | [TO COMPLETE] (art. 12(6): ask only for the information needed) |
| Reply deadline | one month from receipt (art. 12(3)) |
| Extension | up to two further months if the request is complex or numerous: it must be notified within the first month, with the reasons |
| Acknowledgement sent on | [TO COMPLETE] |

## 2. Checks before replying
- [ ] The request concerns the requester's own data (or there is a written authorization).
- [ ] Search done in **all** systems on the processing map (databases, logs, backups, email, vendors, paper).
- [ ] For erasure: exceptions checked (legal obligation, establishment or defence of legal claims, art. 17(3)) and the retention planned in the map.
- [ ] For access: third-party data in the same documents is protected (art. 15(4)).
- [ ] Recipients and processors to notify after rectification, erasure or restriction (art. 19).
- [ ] Refusal or restriction: written reasons, with the right to complain to the supervisory authority and to seek a judicial remedy (art. 12(4)).
- [ ] Free of charge: a fee or refusal only if the request is manifestly unfounded or excessive, with reasons (art. 12(5)).
- [ ] Request, outcome and date recorded in the internal request log.

## 3. What the reply contains
- **Access**: confirmation whether data are processed; a copy of the data; purposes, categories of data, recipients, retention period or criteria, source of the data, existence of automated decisions, rights and the right to complain (art. 15).
- **Erasure, rectification, restriction**: what was done, on which systems, by when; what is still kept and why.
- **Portability**: data provided by the data subject in a structured, commonly used, machine-readable format (art. 20).
- **Objection**: the outcome and, if processing continues, the compelling legitimate grounds (art. 21).

## 4. Reply texts (adapt)

### 4.1 Acknowledgement
Subject: Data-subject request – acknowledgement of receipt
Dear [NAME],
we received your request of [RIGHT] on [DATE]. We will handle it within one month of receipt. To proceed safely we need [DOCUMENT OR MINIMUM INFORMATION TO VERIFY IDENTITY]: please do not send other data.
[CONTROLLER] · [DPO OR PRIVACY CONTACT]

### 4.2 Granting the request
Subject: Reply to your request of [DATE]
Dear [NAME],
in reply to your request of [RIGHT] we inform you that [OUTCOME: what was done or attached]. [For access: list of purposes, categories, recipients, retention, source.] [If some data were kept: which, and under what obligation or interest.]
You may contact us for clarification and, at any time, lodge a complaint with the supervisory authority or seek a judicial remedy.

### 4.3 Extension (within the first month)
Dear [NAME],
your request of [DATE] is complex/numerous ([CONCRETE REASON]). As provided by art. 12(3) GDPR, the reply deadline is extended by [UP TO TWO] months, to [NEW DATE]. We will reply by that date.

### 4.4 Refusal or partial grant
Dear [NAME],
we cannot grant [in full / in part] your request of [DATE] because [SPECIFIC REASON AND LEGAL BASIS, e.g. a legal retention obligation …]. The data concerned remain processed only for [PURPOSE] until [DATE].
You may lodge a complaint with the supervisory authority or seek a judicial remedy.

## 5. What the technical review can and cannot say
The code shows where the data are and whether export and erasure functions exist. It does not show that the search is complete across backups, logs and vendors, or that deadlines are met: that evidence is gathered through the request log.
