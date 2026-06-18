# RST Signalling Corpus Aggregate Summary

Generated from aggregate TSV inventories only. This report does not contain raw corpus text, row-level records, prompts, or examples.

## Method Guardrails

These guardrails are adapted from the corpus-methods DiD paper as general methodological hygiene, not as causal DiD machinery.

- Target quantity: the RST-SC pass asks how existing signal labels can triangulate formal-balance categories. It does not estimate a treatment effect, reader response, or population-level causal effect.
- Unit separation: keep the linguistic figure, the annotation signal, the counted feature-vector label, and the document split distinct. A signal-label count is not an isocolon count unless a human crosswalk licenses that interpretation.
- Feature roles: assign each label one job before interpretation: parison-like form, lexical echo, comparison reference, semantic opposition, exclusion/control, or unresolved. Do not let one label silently serve as both outcome and explanation.
- Aggregation: treat the reported numbers as non-disjoint label memberships. Combined labels can contribute to more than one bridge group, so percentages are descriptive memberships, not mutually exclusive event rates.
- Artifact checks: before using a label as evidence, ask whether its frequency could reflect annotation design, split duplication, lexical-chain breadth, or a measurement convention rather than a rhetorical pattern in the text.
- Downgrade rules: if the crosswalk is ambiguous, if a bridge group is dominated by a broad label such as `lexical_chain`, or if Rency/Brett judge the label theoretically mismatched, report the result as annotation-context only, not rhetorical confirmation.

## Split Inventory

| split | text_files | xml_files | annotation_feature_vectors | feature_vector_lengths |
| --- | --- | --- | --- | --- |
| Full_Annotation | 385 | 772 | 29300 | 1=3; 2=1554; 3=19; 4=27724 |
| Training_Annotation | 347 | 696 | 26285 | 1=3; 2=1321; 3=9; 4=24952 |
| Test_Annotation | 38 | 78 | 3016 | 2=233; 4=2783 |

## Full Annotation Signal Families

These are slot-3 label memberships. Combined labels can contribute to more than one family.

| signal_family | n | pct_of_slot3_labels |
| --- | --- | --- |
| syntactic | 12247 | 44.14 |
| semantic | 9830 | 35.43 |
| lexical | 1560 | 5.62 |
| graphical | 1240 | 4.47 |
| reference | 1130 | 4.07 |
| morphological | 313 | 1.13 |
| numerical | 26 | 0.09 |

## Full Annotation Candidate Subtypes

These are slot-4 label memberships for formal or comparison-relevant candidate labels.

| signal_subtype | n | pct_of_slot4_labels |
| --- | --- | --- |
| lexical_chain | 7151 | 25.79 |
| repetition | 2377 | 8.57 |
| parallel_syntactic_constructions | 558 | 2.01 |
| comparative_reference | 183 | 0.66 |
| meronymy | 118 | 0.43 |
| synonymy | 60 | 0.22 |
| antonymy | 37 | 0.13 |

## Project Bridge Candidates

These group label memberships into candidate bridges for human/Rency interpretation. They are not automatic isocolon judgments.

| bridge_group | n | pct_of_slot4_labels | note |
| --- | --- | --- | --- |
| lexical_echo | 9588 | 34.58 | membership counts; groups can overlap on combined labels |
| parison_or_syntactic_parallelism | 558 | 2.01 | membership counts; groups can overlap on combined labels |
| comparison_reference | 183 | 0.66 | membership counts; groups can overlap on combined labels |
| semantic_opposition | 37 | 0.13 | membership counts; groups can overlap on combined labels |

## Next Interpretive Question

The safe next step is to decide which candidate labels, especially `parallel_syntactic_constructions`, `repetition`, `lexical_chain`, `antonymy`, and `comparative_reference`, should count as evidence for parison-like form, lexical echo, semantic opposition, or comparison in this paper.
