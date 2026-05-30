# Literature acquisition notes

Updated: 2026-05-30

The main shared-literature destination for this project is:

`/Users/brettreynolds/Documents/LLM-CLI-projects/literature/isocolon-rhetoric/`

I also added verified entries to `references.bib`. Metadata was checked against publisher DOI records, ACL Anthology, LDC catalog records, or official corpus pages.

Update after library downloads: the Fahnestock books, Fahnestock 2004 "Preserving the Figure," both Harris rhetorical-figures articles, and both Das/Taboada 2018 signalling articles are now local. The RST Signalling Corpus data itself is still pending library/LDC access.

## Best local/shared holdings already present

- `zeldes2017-gum-corpus.pdf` and `.md`: core citation for GUM.
- `Cuneo_Goldberg_2023_Discourse_functions_islands.pdf` and variants: useful background for discourse-function accounts of grammatical constructions, not specific to isocolon.
- `goldberg2006-constructions-at-work.pdf`: broad construction/function background.
- `flusberg-etal2018-war-metaphors-public-discourse.pdf`: broad rhetorical/framing background, probably peripheral.
- `kuhn2022-disjunctive-discourse-referents-lsf.pdf`: relevant only if we discuss disjunction/comparison more broadly.

## Open PDFs acquired

Fahnestock / rhetorical theory:

- `fahnestock1999-rhetorical-figures-in-science/`: five Oxford chapter/part PDFs plus `.md` files.
- `fahnestock2011-rhetorical-style/`: introduction plus ten chapter PDFs and `.md` files.
- `fahnestock_2004_preserving_the_figure.pdf`
- `fahnestock_2004_figures_of_argument.pdf`

Computational rhetorical figures:

- `harris_dimarco_2017_rhetorical_figures_arguments_computation.pdf`
- `harris_dimarco_ruan_oreilly_2018_annotation_scheme_rhetorical_figures.pdf`
- `kuehn_mitrovic_granitzer_2024_lesser_known_rhetorical_figures_survey.pdf`
- `dubremetz_nivre_2018_rhetorical_figure_detection.pdf`
- `dubremetz_nivre_2015_chiasmus_detection.pdf`
- `dubremetz_nivre_2016_syntax_chiasmus.pdf`
- `dubremetz_nivre_2017_machine_learning_chiasmus.pdf`
- `hromada_2011_multilingual_rhetoric_figures_regex.pdf`
- `lawrence_visser_reed_2017_harnessing_rhetorical_figures.pdf`
- `mitrovic_oreilly_mladenovic_handschuh_2017_ontological_representations.pdf`

Discourse corpora and relation signalling:

- `das_taboada_2018_rst_signalling_corpus.pdf`
- `das_taboada_2018_signalling_beyond_discourse_markers.pdf`
- `zeldes_etal_2025_erst.pdf`
- `taboada_das_2013_annotation_upon_annotation.pdf`
- `das_taboada_2016_multiple_signals_coherence_relations.pdf`
- `das_taboada_2019_multiple_signals_coherence_relations.pdf`
- `liu_zeldes_2019_beyond_wsj_discourse_signals.pdf`
- `prasad_etal_2008_pdtb_2.pdf`
- `carlson_marcu_okurowski_2001_rst_discourse_tagged_corpus.pdf`
- `carlson_marcu_okurowski_2001_rst_tagging_reference_manual.pdf`

## Verified online but not downloaded

These are verified and now in `references.bib`, but I did not get local PDFs.

- Mehlenbacher 2017, `Rhetorical Figures as Argument Schemes`: same SAGE direct-download issue.
- Green 2022, `The Use of Antithesis and Other Contrastive Relations in Argumentation`: same SAGE direct-download issue.
- McQuarrie and Mick 1996, `Figures of Rhetoric in Advertising Language`: DOI verified; likely library access.
- Leigh 1994, `The Use of Figures of Speech in Print Ad Headlines`: DOI verified; likely library access.
- Mann and Thompson 1988, `Rhetorical Structure Theory`: DOI verified; likely library access.

## Corpus/data access still needed

- RST Signalling Corpus data: `LDC2015T10`, DOI `10.35111/5sm9-m096`. LDC catalog confirms it is a licensed web download, with fees shown after login. This is the one remaining item Brett is waiting on from the library.
- RST Discourse Treebank data: `LDC2002T07`, DOI `10.35111/4w31-m996`. It underlies the RST Signalling Corpus, but the current project can proceed with GUM/eRST unless we decide we need WSJ comparability.

## Recommended reading order

1. Fahnestock 1999 and 2011 for the central claim that figures are not decoration but argumentative/form-functional resources.
2. Fahnestock 2004 `Figures of Argument` and `Preserving the Figure` for antithesis, parallel phrasing, and scientific argument.
3. Harris and Di Marco 2017 plus Harris et al. 2018 for the computational-rhetoric framing and annotation problem.
4. Dubremetz and Nivre 2015/2016/2017/2018 for the closest computational analogy: easy formal candidate generation, hard rhetorical false-positive control.
5. Zeldes et al. 2025 eRST and Taboada/Das signalling work for discourse-relation signalling and the justification for relation-conditioned isocolon tests.
6. McQuarrie and Mick 1996 and Leigh 1994 if the paper needs a broader empirical literature on rhetorical figures in naturally occurring persuasive text.

## Immediate paper-facing takeaways

- The literature supports our distinction between formal parallelism and rhetorical function. Dubremetz and Nivre explicitly frame this as the difference between easy repetition detection and hard rhetorical-effect classification.
- The Fahnestock/Harris line supports treating isocolon as a form-function pairing rather than a decorative stylistic label.
- eRST gives a better currently usable corpus basis than RST-SC for this project because it has freely available English multi-genre data with relation signals anchored in GUM.
- RST-SC is still worth getting for comparison, but it is WSJ-only, licensed through LDC, and older than the eRST/GUM signal framework.
