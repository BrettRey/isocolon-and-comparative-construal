from pathlib import Path
p = Path("main.tex"); s = p.read_text()
R = [
# abstract
("analysis scores 17,456 adjacent relation pairs from 299 documents across", "analysis scores 17,912 adjacent relation pairs from 301 documents across"),
("The broad target family of comparison and co-ordination relations scores\n4.1 points higher", "The broad target family of comparison and co-ordination relations scores\n4.2 points higher"),
# corpus
("contains 17,456 such pairs from 299 documents across 24 genres.", "contains 17,912 such pairs from 301 documents across 24 genres."),
("The extracted set contains 16,278 rows with collection label GUM and 1,178", "The extracted set contains 16,723 rows with collection label GUM and 1,189"),
# score scale
("whole interval evenly. In the 17,456 adjacent pairs, the median composite\nvalue is 32.8. The middle half runs from 22.3 to 41.9, and 95\\% of pairs\nfall below 55.9.",
 "whole interval evenly. In the 17,912 adjacent pairs, the median composite\nvalue is 33.3. The middle half runs from 22.6 to 42.2, and 95\\% of pairs\nfall below 56.1."),
("the 4.1-point effect reported below is adjusted", "the 4.2-point effect reported below is adjusted"),
("repeated pairs sit 19.0\npoints above other pairs.", "repeated pairs sit 18.9\npoints above other pairs."),
("formal-balance score of 100.0. That's 68.3 points above the non-target\nmedian of 31.7.", "formal-balance score of 100.0. That's 67.9 points above the non-target\nmedian of 32.1."),
("100.0 & Non-target & \\(+68.3\\)", "100.0 & Non-target & \\(+67.9\\)"),
("95.2 & Target & \\(+63.5\\)", "95.2 & Target & \\(+63.1\\)"),
("60.0 & Non-target & \\(+28.3\\)", "60.0 & Non-target & \\(+27.9\\)"),
("59.9 & Target & \\(+28.2\\)", "59.9 & Target & \\(+27.8\\)"),
("50.0 & Non-target & \\(+18.3\\)", "50.0 & Non-target & \\(+17.9\\)"),
("50.0 & Target & \\(+18.3\\)", "50.0 & Target & \\(+17.9\\)"),
("40.0 & Non-target & \\(+8.3\\)", "40.0 & Non-target & \\(+7.9\\)"),
("40.0 & Target & \\(+8.3\\)", "40.0 & Target & \\(+7.9\\)"),
("30.0 & Non-target & \\(-1.7\\)", "30.0 & Non-target & \\(-2.1\\)"),
("30.0 & Target & \\(-1.7\\)", "30.0 & Target & \\(-2.1\\)"),
("20.0 & Non-target & \\(-11.7\\)", "20.0 & Non-target & \\(-12.1\\)"),
("19.6 & Target & \\(-12.1\\)", "19.6 & Target & \\(-12.5\\)"),
("score points against the non-target median of 31.7.", "score points against the non-target median of 32.1."),
("The gap between the broad target family and the non-target baseline is 4.1\npoints", "The gap between the broad target family and the non-target baseline is 4.2\npoints"),
# results
("composite formal-balance score, pairs in the broad target family are 4.1\npoints higher", "composite formal-balance score, pairs in the broad target family are 4.2\npoints higher"),
("0.041 on the raw 0--1 scale.", "0.042 on the raw 0--1 scale."),
("The document-clustered uncertainty interval runs from 3.6 to 4.7 points.", "The document-clustered uncertainty interval runs from 3.6 to 4.8 points."),
("subscore difference is 7.7 points, compared with 2.4 points for the\nlexical-echo subscore. With mean-length control only, the broad isocolon\nsubscore difference is 6.6 points.",
 "subscore difference is 7.7 points, compared with 2.6 points for the\nlexical-echo subscore. With mean-length control only, the broad isocolon\nsubscore difference is 6.7 points."),
("column as the substantive length-balance result: 6.6 points for the broad", "column as the substantive length-balance result: 6.7 points for the broad"),
("4.8 points, \\mention{joint-list} has an adjusted effect of 4.4 points, and", "4.7 points, \\mention{joint-list} has an adjusted effect of 4.4 points, and"),
("\\mention{adversative-concession} is negative at -1.3 points, meaning that", "\\mention{adversative-concession} is negative at -1.4 points, meaning that"),
("formal-balance effect, 19.0 points, with especially large lexical-echo and", "formal-balance effect, 18.9 points, with especially large lexical-echo and"),
("\\mention{joint-list} estimate is 4.0 points across 17 genres, and", "\\mention{joint-list} estimate is 4.1 points across 17 genres, and"),
("adversative family is 1.2 points.", "adversative family is 1.1 points."),
("their spread, one standard deviation, is about 1.1 points for the broad\ntarget family, 1.3 for \\mention{joint-list}, 0.9 for the narrow adversative\nfamily, and 0.7 for \\mention{adversative-contrast}.",
 "their spread, one standard deviation, is about 1.0 points for the broad\ntarget family, 1.2 for \\mention{joint-list}, 0.9 for the narrow adversative\nfamily, and 0.5 for \\mention{adversative-contrast}."),
# relation table
("Broad target family & 2,462 & 14,994 & 4.1 & 0.8 & 6.6 & 7.7 & 2.4\\\\", "Broad target family & 2,514 & 15,398 & 4.2 & 0.8 & 6.7 & 7.7 & 2.6\\\\"),
("Narrow adversative family & 605 & 16,851 & 1.3 & -0.1 & 4.7 & 2.4 & 1.7\\\\", "Narrow adversative family & 626 & 17,286 & 1.3 & -0.1 & 4.8 & 2.4 & 1.7\\\\"),
("\\mention{joint-list} & 1,690 & 15,766 & 4.4 & 1.0 & 6.5 & 8.2 & 2.0\\\\", "\\mention{joint-list} & 1,713 & 16,199 & 4.4 & 0.9 & 6.5 & 8.3 & 2.2\\\\"),
("\\mention{joint-disjunction} & 167 & 17,289 & 4.8 & 0.9 & 3.6 & 8.6 & 4.0\\\\", "\\mention{joint-disjunction} & 175 & 17,737 & 4.7 & 1.0 & 3.8 & 8.2 & 4.2\\\\"),
("\\mention{adversative-contrast} & 262 & 17,194 & 2.4 & -0.0 & 7.3 & 4.5 & 2.8\\\\", "\\mention{adversative-contrast} & 268 & 17,644 & 2.4 & 0.1 & 7.4 & 4.4 & 2.7\\\\"),
("\\mention{adversative-antithesis} & 343 & 17,113 & 0.4 & -0.2 & 2.5 & 0.8 & 0.9\\\\", "\\mention{adversative-antithesis} & 358 & 17,554 & 0.4 & -0.2 & 2.7 & 0.8 & 1.0\\\\"),
("\\mention{adversative-concession} & 679 & 16,777 & -1.3 & 0.1 & 1.1 & -2.7 & -0.7\\\\", "\\mention{adversative-concession} & 702 & 17,210 & -1.4 & 0.0 & 1.0 & -2.8 & -0.9\\\\"),
("\\mention{restatement-repetition} & 321 & 17,135 & 19.0 & 4.6 & 17.0 & 27.3 & 32.5\\\\", "\\mention{restatement-repetition} & 325 & 17,587 & 18.9 & 4.4 & 17.1 & 27.2 & 32.9\\\\"),
# robustness main text
("4.1 points [3.6, 4.7]. Mean-only length models recover isocolonic length\nbalance for the broad target family, 6.6 [5.6, 7.7], without conditioning",
 "4.2 points [3.6, 4.8]. Mean-only length models recover isocolonic length\nbalance for the broad target family, 6.7 [5.6, 7.8], without conditioning"),
("effect to 1.7 [0.6, 2.8], showing that co-ordination explains a", "effect to 1.8 [0.7, 2.9], showing that co-ordination explains a"),
("stays positive at 3.0 [1.4, 4.7] on the composite formal-balance score.", "stays positive at 2.9 [1.2, 4.5] on the composite formal-balance score."),
# validation main text
("So the AUC of 0.73 reported here means that, in this head-to-head,\nthe marked pair wins about 73 times in 100.", "So the AUC of 0.72 reported here means that, in this head-to-head,\nthe marked pair wins about 72 times in 100."),
("On that scale, the composite formal-balance score has an AUC of 0.73, with an\napproximate Hanley--McNeil interval from 0.66 to 0.80.", "On that scale, the composite formal-balance score has an AUC of 0.72, with an\napproximate Hanley--McNeil interval from 0.65 to 0.78."),
("The parison subscore\nis slightly higher at 0.75 [0.69, 0.82], the lexical-echo subscore is 0.72\n[0.65, 0.79], and the isocolon subscore is 0.65 [0.58, 0.72]",
 "The parison and\nlexical-echo subscores are slightly higher, both at 0.74 [0.68, 0.80], and\nthe isocolon subscore is 0.63 [0.56, 0.69]"),
("876 rows; 27 carry \\mention{syn-prl}. That's a 3.1\\% hit rate, about seven\ntimes the corpus base rate of 0.4\\%, and it recovers 37\\% of all",
 "896 rows; 27 carry \\mention{syn-prl}. That's a 3.0\\% hit rate, about seven\ntimes the corpus base rate of 0.4\\%, and it recovers 34\\% of all"),
("scores included, 24 of 438 inspected rows carry \\mention{syn-prl}. That's\na 5.5\\% hit rate and recovers 33\\% of all \\mention{syn-prl} rows.",
 "scores included, 24 of 448 inspected rows carry \\mention{syn-prl}. That's\na 5.4\\% hit rate and recovers 30\\% of all \\mention{syn-prl} rows."),
# interpretation
("A targeted follow-up will code all 343 eRST", "A targeted follow-up will code all 358 eRST"),
# data statement
("The raw GUM/eRST source files are excluded from the repository; the\nscripts expect a local corpus checkout under \\path{data/raw/gum-erst}.",
 "The raw GUM/eRST source files are excluded from the repository; the\nscripts expect a local corpus checkout under \\path{data/raw/gum-erst}.\nGUM distributes its Reddit documents without their text, so the text was\nrestored with the corpus's own \\path{get_text.py} script before extraction."),
# appendix extraction table
("Valid explicit/implicit relation rows & 34,976\\\\", "Valid explicit/implicit relation rows & 35,943\\\\"),
("Adjacent relation rows used in analysis & 17,456\\\\", "Adjacent relation rows used in analysis & 17,912\\\\"),
("Non-adjacent relation rows excluded & 17,520\\\\", "Non-adjacent relation rows excluded & 18,031\\\\"),
("\\quad gapped rows excluded & 15,349\\\\", "\\quad gapped rows excluded & 15,817\\\\"),
("\\quad interleaved rows excluded & 2,171\\\\", "\\quad interleaved rows excluded & 2,214\\\\"),
("Adjacent rows with discontinuous token intervals & 1,963\\\\", "Adjacent rows with discontinuous token intervals & 2,011\\\\"),
("Adjacent explicit rows & 4,943\\\\", "Adjacent explicit rows & 5,077\\\\"),
("Adjacent implicit rows & 12,513\\\\", "Adjacent implicit rows & 12,835\\\\"),
# appendix validation
("point divides 24 \\mention{syn-prl} rows by 438 inspected rows. In Panel B,\nthe same point divides those 24 rows by all 73 \\mention{syn-prl} rows in",
 "point divides 24 \\mention{syn-prl} rows by 448 inspected rows. In Panel B,\nthe same point divides those 24 rows by all 79 \\mention{syn-prl} rows in"),
("\\mention{syn-prl} rows divided by all 73 \\mention{syn-prl} rows in the", "\\mention{syn-prl} rows divided by all 79 \\mention{syn-prl} rows in the"),
("Composite formal balance & 0.73 [0.66, 0.80] & 0.50 & 0.33\\\\", "Composite formal balance & 0.72 [0.65, 0.78] & 0.49 & 0.33\\\\"),
("Isocolon & 0.65 [0.58, 0.72] & 0.68 & 0.56\\\\", "Isocolon & 0.63 [0.56, 0.69] & 0.68 & 0.57\\\\"),
("Parison & 0.75 [0.69, 0.82] & 0.44 & 0.21\\\\", "Parison & 0.74 [0.68, 0.80] & 0.42 & 0.21\\\\"),
("Lexical echo & 0.72 [0.65, 0.79] & 0.20 & 0.06\\\\", "Lexical echo & 0.74 [0.68, 0.80] & 0.20 & 0.05\\\\"),
("\\caption{Validation against the 73 eRST \\mention{syn-prl} signal\nlabels in 17,456 adjacent relation pairs.", "\\caption{Validation against the 79 eRST \\mention{syn-prl} signal\nlabels in 17,912 adjacent relation pairs."),
# appendix robustness table
("Main & Broad target family, composite & 4.1 & [3.6, 4.7]\\\\", "Main & Broad target family, composite & 4.2 & [3.6, 4.8]\\\\"),
("Mean-length only & Broad isocolon & 6.6 & [5.6, 7.7]\\\\", "Mean-length only & Broad isocolon & 6.7 & [5.6, 7.8]\\\\"),
("Mean-length only & \\mention{adversative-contrast} isocolon & 7.3 & [5.0, 9.6]\\\\", "Mean-length only & \\mention{adversative-contrast} isocolon & 7.4 & [5.1, 9.8]\\\\"),
("Joint-only & List/disjunction composite & 1.7 & [0.6, 2.8]\\\\", "Joint-only & List/disjunction composite & 1.8 & [0.7, 2.9]\\\\"),
("Joint-only & List/disjunction parison & 2.9 & [1.0, 4.8]\\\\", "Joint-only & List/disjunction parison & 2.9 & [1.1, 4.8]\\\\"),
("Adversative-only & Contrast composite & 3.0 & [1.4, 4.7]\\\\", "Adversative-only & Contrast composite & 2.9 & [1.2, 4.5]\\\\"),
("Adversative-only & Contrast parison & 5.9 & [3.0, 8.8]\\\\", "Adversative-only & Contrast parison & 5.6 & [2.8, 8.4]\\\\"),
# weight sensitivity: report range, not interval-excludes-zero counts
("weightings of the three subscores. The effect for the broad target family\nstays positive, with an uncertainty interval that excludes zero, in every\none of the 66. For \\mention{adversative-contrast}, 65 of the 66 are\npositive and 59 have uncertainty intervals that exclude zero.",
 "weightings of the three subscores. The effect for the broad target family\nis positive under every one of the 66, ranging from 0.8 to 7.7 points. For\n\\mention{adversative-contrast}, all 66 are positive, ranging from 0.1 to\n4.4 points."),
# null table: drop p column
("\\begin{tabular}{lrrrrrrr}\n\\toprule\nTarget & Observed & Null mean & Null 95\\% & Strata & Rows & Target rows & \\(p\\)\\\\",
 "\\begin{tabular}{lrrrrrr}\n\\toprule\nTarget & Observed & Null mean & Null 95\\% & Strata & Rows & Target rows\\\\"),
("Broad target family & 4.1 & 1.2 & [0.8, 1.6] & 1,240 & 8,277 & 2,174 & 0.002\\\\", "Broad target family & 4.2 & 1.2 & [0.8, 1.5] & 1,264 & 8,516 & 2,230\\\\"),
("List/disjunction & 4.6 & 1.3 & [1.0, 1.7] & 1,033 & 7,047 & 1,659 & 0.002\\\\", "List/disjunction & 4.7 & 1.3 & [0.9, 1.7] & 1,052 & 7,260 & 1,693\\\\"),
("\\mention{adversative-contrast} & 2.4 & 0.8 & [-0.1, 1.7] & 201 & 1,472 & 220 & 0.002\\\\", "\\mention{adversative-contrast} & 2.4 & 0.7 & [-0.1, 1.6] & 208 & 1,517 & 228\\\\"),
("the data that could move under the stratified shuffle. The \\(p\\)\nvalues are two-sided empirical values from 500 permutations, with the\nstandard plus-one correction, and should be read at that resolution.}",
 "the data that could move under the stratified shuffle. The null\nsummaries come from 500 shuffles.}"),
]
for old, new in R:
    c = s.count(old)
    assert c == 1, (c, old[:80])
    s = s.replace(old, new)
p.write_text(s)
print("applied", len(R), "replacements")
