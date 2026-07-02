## 1. R1: Chapter numbering fix

- [x] 1.1 Rename `paper/sections/13-anexos.tex` to `paper/sections/12-anexos.tex` (file rename via PowerShell Move-Item, directory not under git version control)
- [x] 1.2 Update `paper/main.tex`: change `\input{sections/13-anexos}` to `\input{sections/12-anexos}`

## 2. R2: Bibliographic reference quality

- [x] 2.1 Add Ladas2009 entry to `Bibliography_base.bib` (Scrumban foundational text)
- [x] 2.2 Replace Pressman2020 with Galup2009 in `01-introduccion.tex` (ITSM process degradation claims)
- [x] 2.3 Replace Pressman2020 with Galup2009 in `02-marco-teorico.tex` (ITSM process degradation claims)
- [x] 2.4 Replace Crispin2009 with Ladas2009 in `04-marco-metodologico.tex` (Scrumban methodology, NOT testing pyramid)
- [x] 2.5 Replace Crispin2009 with Ladas2009 in `06-implementacion.tex` — NO-OP: the only Crispin2009 citation in 06-implementacion.tex is for the testing pyramid (line 79), correctly preserved. The Scrumban section (6.6) references Capitulo~4 without directly citing Crispin2009.

## 3. R3: Eliminate fabricated references

- [x] 3.1 Remove Karchhud2024 entry from `Bibliography_base.bib`
- [x] 3.2 Remove all `\cite{Karchhud2024}`, `\textcite{Karchhud2024}`, `\parencite{Karchhud2024}` from `01-introduccion.tex`; rewrite "brecha del espanol" claim using thesis own contribution
- [x] 3.3 Remove all Karchhud2024 citations from `03-estado-del-arte.tex`; rewrite affected paragraphs
- [x] 3.4 Remove Karchhud2024 citation from `08-discusion.tex`; rewrite affected paragraph (both occurrences at lines 20 and 24)
- [x] 3.5 Remove Karchhud2024 citation from `10-recomendaciones.tex` — NO-OP: no Karchhud2024 citations found in this file. Touvron2023 (real reference) correctly preserved.
- [x] 3.6 Remove Mehdi2023 entry from `Bibliography_base.bib`
- [x] 3.7 Remove all Mehdi2023 citations from `01-introduccion.tex`; remove unsupported quantitative claims (40-60%, 35%, 60%)
- [x] 3.8 Remove all Mehdi2023 citations from `03-estado-del-arte.tex`; remove unsupported quantitative claims (60% adoption rate, 2020-2023 period)

## 4. R4: Fix CV argument in discussion

- [x] 4.1 Edit `08-discusion.tex`: removed misleading CV comparison ("sustancialmente mas predecible" with CV 25% vs 23.4%), replaced with absolute range compression argument (11-31s automated vs 96-289s manual)

## 5. R5: Ethics chapter debriefing

- [x] 5.1 Add post-hoc debriefing paragraph to `11-aspectos-legales.tex`: operators informed after data collection, purpose explained, right to withdraw granted, aligned with APA (2017) recommendations

## 6. Verification and compilation

- [x] 6.1 Run `verify_citations.py` from `docs/Tesis/v8 (IA)/`; result: 33 bib entries (not 32 — net change: 34 - 2 removed + 1 added = 33), zero orphans, zero unused entries. STATUS: PASS
- [x] 6.2 Compile PDF: XeLaTeX + Biber + XeLaTeX + XeLaTeX executed successfully. 33 citekeys found, zero citation warnings, zero errors. Output: 68 pages, clean PDF.
