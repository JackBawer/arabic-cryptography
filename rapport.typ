// ============================================================
// USTHB Cryptography Lab Report — Professional Template
// ============================================================

#import "@preview/gentle-clues:1.0.0": *   // optional callout boxes

// ── Page layout ─────────────────────────────────────────────
#set page(
  paper: "a4",
  margin: (top: 30mm, bottom: 30mm, left: 28mm, right: 28mm),
  numbering: none,          // disabled on title page; re-enabled below
)

// ── Typography ───────────────────────────────────────────────
#set text(
  font: "Libertinus Serif",
  size: 13pt,
  lang: "fr",
)

#set par(
  justify: true,
  leading: 1.4em,
  first-line-indent: 1.2em,
)

// ── Heading style ────────────────────────────────────────────
#set heading(numbering: "1.1")

#show heading.where(level: 1): it => {
  v(1.4em)
  text(size: 13pt, weight: "bold", fill: rgb("#003366"))[
    #counter(heading).display("1.") #h(0.5em) #it.body
  ]
  v(0.5em)
  line(length: 100%, stroke: 0.5pt + rgb("#003366"))
  v(0.4em)
}

#show heading.where(level: 2): it => {
  v(0.8em)
  text(size: 11.5pt, weight: "bold")[
    #counter(heading).display("1.1.") #h(0.5em) #it.body
  ]
  v(0.3em)
}

// ── Code blocks ──────────────────────────────────────────────
#show raw.where(block: true): it => {
  set text(font: "JetBrains Mono", size: 9.5pt)
  block(
    fill: rgb("#f4f4f4"),
    stroke: 0.5pt + rgb("#cccccc"),
    radius: 4pt,
    inset: 10pt,
    width: 100%,
    it,
  )
}

#show raw.where(block: false): it => {
  text(font: "JetBrains Mono", size: 9.5pt, fill: rgb("#c0392b"), it)
}

// ── Metadata ─────────────────────────────────────────────────
#let university  = "Université des Sciences et de la Technologie Houari Boumediene"
#let department  = "Département Informatique"
#let course      = "Introduction à la Sécurtié Informatique"
#let tp_number   = "TP n°1"
#let tp_title    = "Cryptographie Arabe"
#let tp_subtitle = "César — Affine — Substitution"
#let academic_year = "2025–2026"
#let supervisor  = "Pr BELKHIR Abdelkader"
#let group       = "Groupe X — Binôme Y"

#let students = (
  (name: "LOUNI Mohammed Said", reg: "232331499716"),
  (name: "LISRI Akram", reg: "232331200815"),
)

// ============================================================
// TITLE PAGE
// ============================================================

#align(center + horizon)[

  // University logo placeholder — replace src with actual logo path
  // #image("logo_usthb.png", width: 30mm)
  // #v(8pt)

  #text(size: 15pt, weight: "bold", fill: rgb("#003366"))[#university]
  #v(4pt)
  #text(size: 11pt, fill: rgb("#555555"))[#department]

  #v(10pt)
  #line(length: 70%, stroke: 1pt + rgb("#003366"))
  #v(30pt)

  #text(size: 13pt, fill: rgb("#555555"))[#tp_number — Module : #course]
  #v(10pt)
  #text(size: 24pt, weight: "bold")[#tp_title]
  #v(8pt)
  #text(size: 13pt, style: "italic")[#tp_subtitle]

  #v(35pt)
  #line(length: 70%, stroke: 0.5pt + rgb("#aaaaaa"))
  #v(25pt)

  // Student table
  #table(
    columns: (2fr, 1.5fr),
    align: (left, center),
    stroke: 0.5pt + rgb("#aaaaaa"),
    fill: (_, row) => if row == 0 { rgb("#003366") } else if calc.odd(row) { rgb("#eef2f7") } else { white },
    table.header(
      text(fill: white, weight: "bold")[Nom de l'étudiant],
      text(fill: white, weight: "bold")[Matricule],
    ),
    ..students.map(s => (
      s.name,
      s.reg,
    )).flatten()
  )

  #v(25pt)
  #grid(
    columns: (1fr, 1fr),
    gutter: 12pt,
    align(left)[
      *Professeur :* #supervisor \
      *Groupe :* #group
    ],
    align(right)[
      *Année universitaire :* #academic_year \
      *Date :* #datetime.today().display("[day]/[month]/[year]")
    ]
  )
]

#pagebreak()

// ============================================================
// PAGE NUMBERING — starts after title page
// ============================================================

#set page(
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 {
      grid(
        columns: (1fr, 1fr),
        align(left)[
          #text(size: 9pt, fill: rgb("#888888"))[#university]
        ],
        align(right)[
          #text(size: 9pt, fill: rgb("#888888"))[#course — #tp_title]
        ]
      )
      line(length: 100%, stroke: 0.3pt + rgb("#aaaaaa"))
    }
  },
  footer: context {
    line(length: 100%, stroke: 0.3pt + rgb("#aaaaaa"))
    v(2pt)
    grid(
      columns: (1fr, 1fr),
      align(left)[
        #text(size: 9pt, fill: rgb("#888888"))[#group]
      ],
      align(center)[
        #text(size: 9pt)[
          Page #counter(page).display("1") sur #counter(page).final().first()
        ]
      ],
      align(right)[
        #text(size: 9pt, fill: rgb("#888888"))[#academic_year]
      ]
    )
  },
)

#counter(page).update(1)

// ============================================================
// TABLE OF CONTENTS
// ============================================================

#show outline.entry.where(level: 1): it => {
  v(4pt, weak: true)
  strong(it)
}

#heading(numbering: none, outlined: false)[Table des matières]
#v(8pt)
#outline(
  title: none,
  indent: 1.5em,
  depth: 2,
)

#pagebreak()

// ============================================================
// ABSTRACT / RÉSUMÉ  (optional — delete if not needed)
// ============================================================

#heading(numbering: none, outlined: true)[Résumé]

Ce rapport présente l'implémentation de trois méthodes classiques de
chiffrement appliquées à l'alphabet arabe : le chiffrement de César, le
chiffrement affine et le chiffrement par substitution. Chaque algorithme est
accompagné d'une attaque par analyse fréquentielle exploitant les propriétés
statistiques de la langue arabe.

#pagebreak()

// ============================================================
// MAIN REPORT BODY
// ============================================================

= Introduction

Ce travail pratique consiste à implémenter plusieurs méthodes classiques de
chiffrement ainsi que des techniques de cassage basées sur l'analyse
fréquentielle. Les algorithmes étudiés sont le chiffrement de César, le
chiffrement affine et le chiffrement par substitution.

L'objectif est d'appliquer ces méthodes à un alphabet arabe et d'observer
comment les propriétés statistiques de la langue peuvent être utilisées pour
retrouver la clé d'un message chiffré.

= Organisation du projet

Le projet est structuré en plusieurs modules afin de séparer clairement les
différentes fonctionnalités. Les implémentations des chiffrements sont
regroupées dans des fichiers distincts tandis que les fonctions liées à
l'analyse fréquentielle et à la normalisation du texte sont placées dans des
modules dédiés.

Cette organisation rend le code plus lisible et facilite les tests.

== Structure des fichiers

#table(
  columns: (1.2fr, 2fr),
  align: (left, left),
  stroke: 0.4pt + rgb("#aaaaaa"),
  fill: (_, row) => if row == 0 { rgb("#003366") } else if calc.odd(row) { rgb("#eef2f7") } else { white },
  table.header(
    text(fill: white, weight: "bold")[Fichier],
    text(fill: white, weight: "bold")[Rôle],
  ),
  [`cesar.py`],    [Chiffrement et déchiffrement de César],
  [`affine.py`],    [Chiffrement affine et inverse modulaire],
  [`substitution.py`],     [Chiffrement par substitution],
  [`frequency.py`],      [Analyse fréquentielle],
  [`normalize.py`], [Normalisation et nettoyage du texte arabe],
  [`main1.py`],     [Script primal — démonstration de chiffrements],
  [`main2.py`],     [Script principal — chiffrement et attaque],
)

= Alphabet arabe

L'alphabet utilisé dans ce projet contient 28 lettres :

#align(center)[
  #block(
    fill: rgb("#eef2f7"),
    stroke: 0.5pt + rgb("#aaaaaa"),
    radius: 4pt,
    inset: 10pt,
  )[
    #text(size: 14pt, dir: rtl)[ابتثجحخدذرزسشصضطظعغفقكلمنهوي]
  ]
]

Chaque lettre est associée à un indice numérique compris entre 0 et 27.

= Chiffrement César

Le chiffrement de César consiste à décaler chaque lettre d'un nombre fixe de
positions dans l'alphabet. La fonction de chiffrement est :

$ E(x) = (x + k) mod 28 $

Le déchiffrement applique simplement l'opération inverse :

$ D(y) = (y - k) mod 28 $

où $k$ est la clé (valeur du décalage).

= Chiffrement Affine

Le chiffrement affine généralise le chiffrement de César en utilisant une
transformation linéaire :

$ E(x) = (a dot x + b) mod 28 $

Le déchiffrement nécessite le calcul de l'inverse modulaire $a^(-1)$ de $a$
modulo 28 :

$ D(y) = a^(-1) dot (y - b) mod 28 $

La clé est le couple $(a, b)$, avec $gcd(a, 28) = 1$.

= Chiffrement par substitution

Dans le chiffrement par substitution, chaque lettre est remplacée par une autre
lettre selon une permutation fixe $pi$ de l'alphabet :

$ E(x) = pi(x) $

La clé est la permutation complète, soit $28!$ clés possibles.

= Analyse fréquentielle

Les attaques implémentées reposent sur l'observation des fréquences
d'apparition des lettres dans le texte chiffré et leur comparaison avec les
fréquences typiques de la langue arabe.

== Principe

Pour chaque lettre $c$ du texte chiffré, on calcule sa fréquence relative
$f(c)$ puis on la compare avec la distribution de référence $f_"ar"$.

== Calcul du score de corrélation

$ "score"(k) = sum_(x=0)^(27) f(x) dot f_"ar" ((x - k) mod 28) $

La clé $k$ maximisant ce score est retenue comme candidate.

= Expérimentation

Le script principal du projet chiffre un texte arabe puis tente de retrouver la
clé avec la commande suivante :
```sh
cd src
python main2.py
```

Les résultats obtenus montrent que les chiffrements simples peuvent être cassés
efficacement par analyse fréquentielle.

= Conclusion

Ce projet met en évidence les limites de sécurité des chiffrements classiques.
Les méthodes de César et d'Affine sont particulièrement vulnérables aux
attaques statistiques. Le chiffrement par substitution est plus robuste mais
reste cassable lorsque l'on dispose d'un texte suffisamment long.

// ============================================================
// REFERENCES  (add your actual sources)
// ============================================================

#pagebreak()
#heading(numbering: none, outlined: true)[Références]

#set par(first-line-indent: 0em)

+ A. Menezes, P. van Oorschot, S. Vanstone. _Handbook of Applied Cryptography_. CRC Press, 1996.
+ B. Schneier. _Applied Cryptography_. Wiley, 2nd ed., 1996.
+ Documentation Python 3. #link("https://docs.python.org/3/")
