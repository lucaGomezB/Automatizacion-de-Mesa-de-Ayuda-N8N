# Design: c-78 — Bibliografia y atribucion

## Context

Ver `proposal.md` — Why. Estado relevante verificado contra el arbol de trabajo
v9 (2026-10-10):

- `03-estado-del-arte.tex:28` atribuye a Revina et al. (2020) BERT, ~91 % y
  transferencia de modelos preentrenados. `08-discusion.tex:20,22` repite la
  atribucion (BERT, 91 %) y agrega un rango "88 % a 94 %" sin cita. La seccion
  `03-estado-del-arte.tex:30` hace una afirmacion sobre literatura few-shot sin
  cita.
- `04-marco-metodologico.tex:47` rotula \(\kappa = 0{,}87\) como "sustancial" y
  deja entre parentesis "(\(\kappa > 0{,}80\) indica acuerdo casi perfecto)":
  contradiccion interna. `:79` repite el Kappa en "Amenazas a la validez". Los
  rangos se citan a `Cohen1960_kappa`, pero son de Landis & Koch (1977).
- `Bibliography_base.bib` tiene 33 entradas, todas citadas; el aparato de citas
  esta en `biblatex` con `style=apa` (`preambles/preamble.tex:92`).
- El corpus y los numeros de resultados NO son alcance de este change (c-76).

Restriccion dura: la tesis se compila en Overleaf (sin toolchain LaTeX local).
No se toca `App/**`. No se editan artefactos de c-67/c-76/c-77 ni `CHANGES.md`.

## Goals / Non-Goals

**Goals:**

- Corregir la misatribucion de Revina et al. (2020) en 3.3 y 8.2 e integrar la
  tension en el capitulo 8.
- Modernizar el estado del arte con al menos 12 referencias arbitradas 2023-2026 y
  resolver las dos afirmaciones sin cita.
- Reparar la higiene de citas y atribucion (Landis & Koch, metadatos de tres
  entradas, citas huerfanas, estilo "et al.").

**Non-Goals:**

- No tocar los numeros del corpus, el redondeo de tiempos, la ventana temporal,
  la unificacion sectorial, el efecto de tamano, la calibracion, el prompt ni el
  tag (c-76 / c-77).
- No modificar `evaluation-framework` ni `App/**`.
- No recompilar localmente (Overleaf).
- No fabricar ninguna referencia, en particular un estudio de Gemini sobre
  tickets en espanol que no existe.

## Decisions

### D-B1 — Reescribir Revina et al. (2020) con su conclusion real

**Evidencia verificada** (no re-investigar): titulo real "IT Ticket Classification:
The Simpler, the Better" (IEEE Access 8:193380-193395, 2020, DOI
`10.1109/ACCESS.2020.3032840`). La palabra "BERT" aparece CERO veces; no usa
transformer ni modelo preentrenado. Compara TF-IDF contra rasgos linguisticos
artesanales alimentando clasificadores clasicos (kNN, arboles de decision, naive
Bayes, regresion logistica, SVM, semi-supervisado) para predecir la **complejidad**
del ticket (baja/media/alta), no la categoria. Concluye lo opuesto a la tesis:
los algoritmos simples y explicables con pocos rasgos linguisticos ganan.
Cita textual sobre embeddings preentrenados: "pre-trained models would not perform
well considering the domain-specific vocabulary which contains many new words
compared to the training corpus". No aparece ningun "91 %" en el cuerpo; la unica
exactitud en prosa es un 62 % previo de reglas de los mismos autores.

**Decision:** reescribir 3.3 y 8.2. En 3.3, presentar a Revina et al. como
evidencia de que los metodos simples/explicables con rasgos del dominio son
competitivos y que los embeddings preentrenados pueden rendir peor por vocabulario
de dominio. En 8.2, eliminar la comparacion "frente al enfoque BERT de Revina
(91 %)" (no existe) e incorporar la tension: el presente trabajo usa un LLM de
proposito general, y Revina et al. es la evidencia contraria a la suposicion de
transferencia trivial; se discute por que esa tension refuerza el analisis (la
eleccion del LLM se justifica por la tarea —clasificacion de categoria con
contexto instruccional— no por transferencia no supervisada). **Alternativa**:
retirar la cita — se descarta; el articulo es pertinente y su correccion es
justamente la evidencia que fortalece la discusion.

### D-B2 — Modernizar el estado del arte y resolver las afirmaciones sin cita

**Decision:** agregar **al menos 12** referencias (minimo contractual). Las 12
candidatas core del anexo, ya verificadas, cubren el minimo; si la longitud final
lo permite se agrega la reserva arbitrada `razma2026aibased` (Systems, 2026),
cuyo DOI debe re-verificarse antes de usarla. Asignacion tematica:

- **(a) Clasificacion de tickets / mesa de servicio con LLM**: `paket2024itservice`,
  `liu2025tickit`, `zangari2023ticket`, `colavito2025benchmarking`.
- **(b) Evaluacion zero-shot / few-shot multilingue**: `ahuja2023mega`,
  `lai2023okapi`, `zhang2023multilingual`, `xuan2025mmluprox`.
- **(c) LLM en espanol / Iberoamerica**: `grandury2025laleaderboard`,
  `mayorrocher2026spanish`, `bernalbeltran2025mexicanspanish`,
  `ramonferrer2026tripletotext`.

Reemplazar el rango "88 % a 94 %" (`08:20`) por resultados concretos citados (por
ejemplo, los reportados por las evaluaciones incorporadas) o retirarlo. Sustituir
la afirmacion few-shot sin cita de `03:30` por una cita a una de las referencias
multilingues (p. ej. `ahuja2023mega` para cobertura por idioma,
`grandury2025laleaderboard` para variedades del espanol).

**Brecha declarada:** no existe articulo arbitrado 2023-2026 que evalue Google
Gemini sobre tickets de soporte en espanol; se declara como parte de la
contribucion. NO se fabrica una referencia. **Alternativa**: sostener solo las
referencias 2023-2026 — se descarta; Revina/Paramesh (base de comparacion) siguen
siendo el ancla clasica y no se eliminan.

### D-B3 — Higiene de citas y atribucion (incluye el estado de las citas huerfanas)

**Landis & Koch:** agregar la entrada y citarla para los rangos. Corregir:
`04:47` "considerado sustancial" -> "considerado casi perfecto" (con
\(\kappa = 0{,}87\)) y ajustar el parentetico para que la fuente sea Landis & Koch;
`04:79` ("Amenazas a la validez") idem. `Cohen1960_kappa` queda solo para la
definicion del coeficiente.

**Metadatos:**
- `Stallings2017_computer_security`: `author = {Stallings, William and Brown, Lawrie}`.
- `OGC2011_itil`: quitar el campo `edition = {2011}` (2011 no es una edicion); la
  publicacion de *ITIL Service Operation* (2011) es de **The Stationery Office
  (TSO)** por encargo del Office of Government Commerce; ITIL es hoy de la
  herencia AXELOS. Se conserva `author = {{Office of Government Commerce}}` y
  `publisher = {The Stationery Office}` y se agrega una `note` que aclara la
  titularidad posterior (AXELOS/PeopleCert) para trazabilidad.
- `Jurafsky2023_speech_language`: cambiar `publisher = {Pearson}` por
  `publisher = {Stanford University}` con `note = {Borrador de la 3ra edicion,
  disponible en el sitio de los autores}` (la 2da edicion si fue Pearson).

**Estilo "et al.":** el preambulo usa `style=apa`, que ya separa con coma; la cita
`\textcite` produce "Autor et al. (ano)". La tarea es auditar el PDF compilado y,
si algun pasaje manual escribe "et al. 2020" sin coma, normalizarlo. No se edita
el preambulo salvo que la auditoria del PDF lo exija.

**Citas huerfanas (resuelto 2026-10-10):** las dos citas huerfanas que reportaba
la auditoria estaban en la version **v7** (la version auditada) y eran **Karchhud,
R., Singh, A., & Patel, M. (2024)** ("Few-shot ticket classification with large
language models: A multilingual evaluation", JISEM 9(2), 145-168) y **Mehdi, S.,
Kapoor, A., & Larsson, J. (2023)** ("The state of AI in customer support: Industry
adoption survey 2020-2023", International Journal of Service Operations Management
45(3), 211-234). Ambas fueron **verificadas como FABRICADAS**: Crossref y OpenAlex
devuelven cero resultados para los autores y los titulos; el journal JISEM
(ISSN 2468-4376) existe pero el articulo no; en el segundo caso el propio nombre
del journal es un near-miss del real "International Journal of Services and
Operations Management" (ISSN 1744-2389). Firma tipica de alucinacion: journal real
plausible + autores/articulo imposibles + venue near-miss. Ambas ya fueron
**retiradas entre v7 y v9**; el arbol v9 actual tiene **cero** citas huerfanas y
**cero** entradas sin usar, verificado por `verify_citations.py` (STATUS: PASS,
33/33) y por la comparacion de `paper/main.bcf` contra el `.bib` (diferencia
vacia). El change MUST NOT reintroducirlas y MUST re-citar/reformular/retirar las
dos afirmaciones que sostenian (rango "88 % a 94 %" en `08:20`; adopcion de IA en
`03:12`), ya cubierto por B2. **Guardia (fabricaciones en cluster):** como las
referencias fabricadas suelen aparecer agrupadas, el apply MUST re-verificar
**todas** las entradas restantes del `.bib` contra resolucion por DOI/URL y
retirar o reemplazar cualquiera que no resuelva. **Alternativa**: inventar las dos
candidatas para "cerrar" el item — se rechaza por integridad.

## Risks / Trade-offs

- Tocar `.tex`/`.bib` sin compilador local -> mitigar con `openspec validate` +
  revision en Overleaf + `rg` de control.
- La bibliografia crece (33 -> ~42-46) y podria empujar la tesis por encima de
  100 paginas (actual ~74) -> mitigar midiendo tras B2; el limite de 100 paginas
  es criterio de exito.
- Solapamiento con c-76/c-77 -> mitigado: este change solo toca bibliografia y
  atribucion; los numeros y la estadistica se referencian a c-76/c-77.
- Riesgo de introducir una referencia no verificada -> mitigado: solo se usa la
  lista candidata verificada del anexo; el apply debe confirmar el DOI.
- Citas fabricadas en una version previa (v7: Karchhud 2024, Mehdi 2023) ->
  mitigado re-verificando por DOI **cada** entrada del `.bib` (las fabricaciones
  suelen agruparse) y manteniendo la guardia de no reintroduccion.

## Migration Plan

1. Editar `Bibliography_base.bib` (Landis1977, metadatos, nuevas entradas).
2. Reescribir `03-estado-del-arte.tex`, `04-marco-metodologico.tex`,
   `08-discusion.tex` y citar las nuevas referencias.
3. Verificar integridad de citas (`verify_citations.py` + `main.bcf`).
4. Append del grupo B1-B3 en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
5. Recompilar en Overleaf; verificar PDF sin errores fatales y <= 100 paginas.
6. Rollback: `git checkout --` / `git revert`.

## Open Questions

- OQ-B2-1 (RESUELTA): el minimo es **12** referencias arbitradas 2023-2026. Las 12
  candidatas core verificadas del anexo cubren el minimo; la reserva
  `razma2026aibased` (Systems, 2026) se agrega solo si la longitud final lo
  permite y previa re-verificacion de su DOI. El contrato de la spec pasa a
  "al menos 12".
- OQ-B3-1 (ABIERTA): si el PDF compilado confirma que `style=apa` ya aplica la
  coma antes del ano en todas las citas, el item de estilo se cierra sin editar
  el preambulo. Verificacion manual del autor en tiempo de compilacion.

---

## Anexo A — Referencias candidatas verificadas (BibTeX verbatim)

> Todas verificadas (ACL Anthology / Crossref / DOI). Usar tal cual; el apply no
> debe inventar campos ni referencias.

```bibtex
@inproceedings{ahuja2023mega,
  title     = "{MEGA}: Multilingual Evaluation of Generative {AI}",
  author    = {Ahuja, Kabir and Diddee, Harshita and Hada, Rishav and Ochieng, Millicent and Ramesh, Krithika and Jain, Prachi and Nambi, Akshay and Ganu, Tanuja and Segal, Sameer and Ahmed, Mohamed and Bali, Kalika and Sitaram, Sunayana},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages     = {4232--4267},
  year      = {2023},
  publisher = {Association for Computational Linguistics},
  address   = {Singapore},
  doi       = {10.18653/v1/2023.emnlp-main.258},
  url       = {https://aclanthology.org/2023.emnlp-main.258/}
}

@inproceedings{lai2023okapi,
  title     = {Okapi: Instruction-tuned Large Language Models in Multiple Languages with Reinforcement Learning from Human Feedback},
  author    = {Lai, Viet Dac and Nguyen, Chien and Ngo, Nghia and Nguyen, Thuat and Dernoncourt, Franck and Rossi, Ryan A. and Nguyen, Thien Huu},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing: System Demonstrations},
  pages     = {318--327},
  year      = {2023},
  publisher = {Association for Computational Linguistics},
  address   = {Singapore},
  doi       = {10.18653/v1/2023.emnlp-demo.28},
  url       = {https://aclanthology.org/2023.emnlp-demo.28/}
}

@inproceedings{zhang2023multilingual,
  title     = {Multilingual Large Language Models Are Not (Yet) Code-Switchers},
  author    = {Zhang, Ruochen and Cahyawijaya, Samuel and Cruz, Jan Christian Blaise and Winata, Genta Indra and Aji, Alham Fikri},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages     = {12567--12582},
  year      = {2023},
  publisher = {Association for Computational Linguistics},
  address   = {Singapore},
  doi       = {10.18653/v1/2023.emnlp-main.774},
  url       = {https://aclanthology.org/2023.emnlp-main.774/}
}

@inproceedings{xuan2025mmluprox,
  title     = "{MMLU}-{P}ro{X}: A Multilingual Benchmark for Advanced Large Language Model Evaluation",
  author    = {Xuan, Weihao and Yang, Rui and Qi, Heli and Zeng, Qingcheng and Xiao, Yunze and Feng, Aosong and Liu, Dairui and Xing, Yun and Wang, Junjue and Gao, Fan and Lu, Jinghui and Jiang, Yuang and Li, Huitao and Li, Xin and Yu, Kunyu and Dong, Ruihai and Gu, Shangding and Li, Yuekang and Xie, Xiaofei and Juefei-Xu, Felix and Khomh, Foutse and Yoshie, Osamu and Chen, Qingyu and Teodoro, Douglas and Liu, Nan and Goebel, Randy and Ma, Lei and Marrese-Taylor, Edison and Lu, Shijian and Iwasawa, Yusuke and Matsuo, Yutaka and Li, Irene},
  booktitle = {Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages     = {1513--1532},
  year      = {2025},
  publisher = {Association for Computational Linguistics},
  address   = {Suzhou, China},
  doi       = {10.18653/v1/2025.emnlp-main.79},
  url       = {https://aclanthology.org/2025.emnlp-main.79/}
}

@inproceedings{grandury2025laleaderboard,
  title     = {La Leaderboard: A Large Language Model Leaderboard for {S}panish Varieties and Languages of {S}pain and {L}atin {A}merica},
  author    = {Grandury, Mar{\'i}a and Aula-Blasco, Javier and Falc{\~a}o, J{\'u}lia and Fourrier, Cl{\'e}mentine and Gonz{\'a}lez Saiz, Miguel and Mart{\'i}nez, Gonzalo and Santamaria Gomez, Gonzalo and Agerri, Rodrigo and Aldama Garc{\'i}a, Nuria and Chiruzzo, Luis and Conde, Javier and Gomez Adorno, Helena and Guerrero Nieto, Marta and Ivetta, Guido and L{\'o}pez Fuertes, Nat{\`a}lia and Plaza-del-Arco, Flor Miriam and Mart{\'i}n-Valdivia, Mar{\'i}a-Teresa and Montoro Zamorano, Helena and Mu{\~n}oz Sanz, Carmen and Reviriego, Pedro and Rosado Plaza, Leire and Vaca Serrano, Alejandro and Vallecillo-Rodr{\'i}guez, Estrella and Vallego, Jorge and Zubiaga, Irune},
  booktitle = {Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  pages     = {32482--32524},
  year      = {2025},
  publisher = {Association for Computational Linguistics},
  address   = {Vienna, Austria},
  doi       = {10.18653/v1/2025.acl-long.1561},
  url       = {https://aclanthology.org/2025.acl-long.1561/}
}

@article{mayorrocher2026spanish,
  title   = {Evaluating large language models with tests of {S}panish as a foreign language: pass or fail?},
  author  = {Mayor-Rocher, Marina and Melero, Nina and Merino-G{\'o}mez, Elena and Grandury, Mar{\'i}a and Conde, Javier and Reviriego, Pedro},
  journal = {Applied Linguistics},
  year    = {2026},
  note    = {Advance article; volume/pages pending},
  doi     = {10.1093/applin/amag048},
  url     = {https://doi.org/10.1093/applin/amag048}
}

@article{bernalbeltran2025mexicanspanish,
  title   = {Sentiment Analysis in {M}exican {S}panish: A Comparison Between Fine-Tuning and In-Context Learning with Large Language Models},
  author  = {Bernal-Beltr{\'a}n, Tom{\'a}s and Paredes-Valverde, Mario Andr{\'e}s and Salas-Z{\'a}rate, Mar{\'i}a del Pilar and Garc{\'i}a-D{\'i}az, Jos{\'e} Antonio and Valencia-Garc{\'i}a, Rafael},
  journal = {Future Internet},
  volume  = {17},
  number  = {10},
  pages   = {445},
  year    = {2025},
  doi     = {10.3390/fi17100445},
  url     = {https://doi.org/10.3390/fi17100445}
}

@article{ramonferrer2026tripletotext,
  title   = {{S}panish Triple-to-Text Benchmark on Low-Resource Large Language Models},
  author  = {Ram{\'o}n-Ferrer, Virginia and Badenes-Olmedo, Carlos and Corcho, {\'O}scar},
  journal = {Semantic Web},
  volume  = {17},
  number  = {3},
  year    = {2026},
  doi     = {10.1177/22104968261440701},
  url     = {https://doi.org/10.1177/22104968261440701}
}

@inproceedings{paket2024itservice,
  title      = {IT Service Desk Ticket Classification via Large Language Models},
  author     = {Paket, Ezgi and {\c{S}}enerkek, G{\"o}ksu and Akyol, Fatma Bet{\"u}l and Salman, Furkan},
  booktitle  = {2024 9th International Conference on Computer Science and Engineering (UBMK)},
  pages      = {135--140},
  year       = {2024},
  publisher  = {IEEE},
  doi        = {10.1109/ubmk63289.2024.10773473},
  url        = {https://doi.org/10.1109/ubmk63289.2024.10773473}
}

@inproceedings{liu2025tickit,
  title     = {TickIt: Leveraging Large Language Models for Automated Ticket Escalation},
  author    = {Liu, Fengrui and He, Xiao and Zhang, Tieying and Chen, Jianjun and Li, Yi and Yi, Lihua and Zhang, Haipeng and Wu, Gang and Shi, Rui},
  booktitle = {Proceedings of the 33rd ACM International Conference on the Foundations of Software Engineering (FSE)},
  pages     = {343--354},
  year      = {2025},
  publisher = {ACM},
  doi       = {10.1145/3696630.3728558},
  url       = {https://doi.org/10.1145/3696630.3728558}
}

@article{zangari2023ticket,
  title   = {Ticket automation: An insight into current research with applications to multi-level classification scenarios},
  author  = {Zangari, Alessandro and Marcuzzo, Matteo and Schiavinato, Michele and Gasparetto, Andrea and Albarelli, Andrea},
  journal = {Expert Systems with Applications},
  volume  = {225},
  pages   = {119984},
  year    = {2023},
  doi     = {10.1016/j.eswa.2023.119984},
  url     = {https://doi.org/10.1016/j.eswa.2023.119984}
}

@article{colavito2025benchmarking,
  title   = {Benchmarking large language models for automated labeling: The case of issue report classification},
  author  = {Colavito, Giuseppe and Lanubile, Filippo and Novielli, Nicole},
  journal = {Information and Software Technology},
  volume  = {184},
  pages   = {107758},
  year    = {2025},
  doi     = {10.1016/j.infsof.2025.107758},
  url     = {https://doi.org/10.1016/j.infsof.2025.107758}
}
```

### Entrada de B3 (Landis & Koch, 1977)

```bibtex
@article{Landis1977_kappa,
  author  = {Landis, J. Richard and Koch, Gary G.},
  title   = {The Measurement of Observer Agreement for Categorical Data},
  journal = {Biometrics},
  volume  = {33},
  number  = {1},
  pages   = {159--174},
  year    = {1977},
  doi     = {10.2307/2529310},
}
```
