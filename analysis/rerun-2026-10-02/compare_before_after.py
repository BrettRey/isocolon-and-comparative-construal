import sys, pandas as pd, numpy as np
S = sys.argv[1]
OLD, NEW = f"{S}/before/derived", "data/derived"
rows = []
def add(section, label, old, new, paper=""):
    rows.append((section, label, paper, old, new))
def rd(d, f): return pd.read_csv(f"{d}/{f}", sep="\t")
def pts(x): return f"{100*x:.1f}"
def ci(lo, hi): return f"[{100*lo:.1f}, {100*hi:.1f}]"

for tag, d in (("old", OLD), ("new", NEW)):
    pass

def both(fn):
    return fn(OLD), fn(NEW)

# A. corpus
def corpus(d):
    s = rd(d, "gum_erst_adjacent_isocolon_scores.tsv")
    return {"pairs": f"{len(s):,}", "docs": str(s.doc.nunique()), "genres": str(s.genre.nunique()),
            "GUM rows": f"{(s.collection=='GUM').sum():,}", "GENTLE rows": f"{(s.collection=='GENTLE').sum():,}"}
o, n = both(corpus)
for k in o: add("Corpus", k, o[k], n[k])
def diag(d):
    t = rd(d, "extraction_diagnostics.tsv").set_index("diagnostic")["value"]
    return t
o, n = both(diag)
for k in o.index:
    add("Extraction (appendix)", k, f"{int(o[k]):,}" if float(o[k]).is_integer() else str(o[k]), f"{int(n.get(k,np.nan)):,}" if k in n and float(n[k]).is_integer() else str(n.get(k,"")))

# B. distribution
def dist(d):
    s = rd(d, "gum_erst_adjacent_isocolon_scores.tsv"); x = 100*s.isocolon_score
    broad = rd(d, "observed_isocolon_effects.tsv")
    return {"median": f"{x.median():.1f}", "IQR": f"{x.quantile(.25):.1f}–{x.quantile(.75):.1f}",
            "95th pct": f"{x.quantile(.95):.1f}", "SD": f"{x.std():.1f}"}
o, n = both(dist)
for k in o: add("Score distribution (0–100)", k, o[k], n[k])

# C. relation table + main
def rel(d):
    r = rd(d, "robustness_checks.tsv")
    out = {}
    for t in ["broad","narrow","joint_list","joint_disjunction","adversative_contrast","adversative_antithesis","adversative_concession","restatement_repetition"]:
        g = r[(r.check=="document_clustered") & (r.target==t)].set_index("outcome")
        m = r[(r.check=="length_with_mean_control") & (r.target==t)]
        mo = pts(m.estimate.iloc[0]) if len(m) else "–"
        c = g.loc["isocolon_score"]
        out[t] = (f"{int(c.target_n):,}/{int(c.comparison_n):,}",
                  f"{pts(c.estimate)} {ci(c.cluster_ci_low, c.cluster_ci_high)}",
                  pts(g.loc['length_score'].estimate), mo, pts(g.loc['syntax_score'].estimate), pts(g.loc['lexical_score'].estimate))
    return out
o, n = both(rel)
for t in o:
    add("Relation table", f"{t}: n target/other", o[t][0], n[t][0])
    add("Relation table", f"{t}: composite [clustered CI]", o[t][1], n[t][1])
    add("Relation table", f"{t}: isocolon full / mean-only / parison / lexical", " / ".join(o[t][2:]), " / ".join(n[t][2:]))

# D. robustness
def rob(d):
    r = rd(d, "robustness_checks.tsv"); out = {}
    def get(check, target, outcome):
        g = r[(r.check==check)&(r.target==target)&(r.outcome==outcome)]
        if not len(g): return "–"
        g = g.iloc[0]; return f"{pts(g.estimate)} {ci(g.cluster_ci_low, g.cluster_ci_high)}"
    out["mean-only broad isocolon"] = get("length_with_mean_control","broad","length_score")
    out["mean-only adv-contrast isocolon"] = get("length_with_mean_control","adversative_contrast","length_score")
    out["joint-only list/disj composite"] = get("coordination_matched","joint_list_or_disjunction_vs_other_joint","isocolon_score")
    out["joint-only list/disj parison"] = get("coordination_matched","joint_list_or_disjunction_vs_other_joint","syntax_score")
    out["adv-only contrast composite"] = get("adversative_matched","adversative_contrast_vs_other_adversative","isocolon_score")
    out["adv-only contrast parison"] = get("adversative_matched","adversative_contrast_vs_other_adversative","syntax_score")
    out["GUM-only broad composite"] = get("gum_only","broad","isocolon_score")
    out["continuous-only broad composite"] = get("continuous_spans_only","broad","isocolon_score")
    out["joint-list composite"] = get("document_clustered","joint_list","isocolon_score")
    return out
o, n = both(rob)
for k in o: add("Robustness", k, o[k], n[k])

# E. validation
def val(d):
    v = rd(d, "isocolon_score_validation_summary.tsv").set_index("score"); out = {}
    out["syn-prl rows / base rate"] = f"{int(v.loc['isocolon_score','gold_syn_prl_n'])} / {100*v.loc['isocolon_score','gold_syn_prl_prevalence']:.1f}%"
    for s, lab in (("isocolon_score","composite"),("length_score","isocolon"),("syntax_score","parison"),("lexical_score","lexical")):
        x = v.loc[s]; out[f"AUC {lab} [CI]; labelled/unlabelled mean"] = f"{x.auc:.2f} [{x.auc_ci_low:.2f}, {x.auc_ci_high:.2f}]; {x.mean_gold:.2f}/{x.mean_non_gold:.2f}"
    t = rd(d, "isocolon_score_thresholds.tsv").set_index("percentile")
    for p in (95, 97.5):
        x = t.loc[p]; out[f"top {p}th pct: n, syn-prl, precision, recall"] = f"{int(x.selected_n)}, {int(x.selected_gold_syn_prl_n)}, {100*x.precision:.1f}%, {100*x.recall:.0f}%"
    return out
o, n = both(val)
for k in o: add("Validation", k, o[k], n[k])

# F. genre varying
def gv(d):
    g = rd(d, "genre_varying_summary.tsv").set_index("target")
    return {t: f"mu {pts(g.loc[t,'eb_mu'])}, tau {pts(g.loc[t,'eb_tau'])}, genres {int(g.loc[t,'n_genres'])}" for t in g.index}
o, n = both(gv)
for k in o: add("Genre-varying", k, o[k], n.get(k,"–"))

# G. weight sensitivity
def ws(d):
    w = rd(d, "score_weight_sensitivity_summary.tsv"); w = w[w.weight_family=="grid"].set_index("target")
    return {t: f"{int(round(w.loc[t,'share_positive']*w.loc[t,'n_weight_specs']))}/{int(w.loc[t,'n_weight_specs'])} positive, {int(round(w.loc[t,'share_ci_excludes_zero_positive']*w.loc[t,'n_weight_specs']))} CI>0" for t in w.index}
o, n = both(ws)
for k in o: add("Weight sensitivity (grid)", k, o[k], n.get(k,"–"))

# H. nulls
def nulls(d):
    z = rd(d, "stratified_nulls.tsv"); z = z[z.outcome=="isocolon_score"].set_index("target")
    return {t: f"obs {pts(z.loc[t,'observed_estimate'])}, null {pts(z.loc[t,'null_mean'])} {ci(z.loc[t,'null_q025'], z.loc[t,'null_q975'])}, strata {int(z.loc[t,'movable_strata']):,}, rows {int(z.loc[t,'movable_rows']):,}, target {int(z.loc[t,'movable_target_rows']):,}, p {z.loc[t,'empirical_p_two_sided']:.3f}" for t in z.index}
o, n = both(nulls)
for k in o: add("Stratified nulls", k, o[k], n.get(k,"–"))

# I. influence: reddit omitted
def infl(d):
    z = rd(d, "influence_checks.tsv"); z = z[(z.spec=="broad_main")].set_index("omitted_genre")
    return {g: f"{pts(z.loc[g,'estimate'])} {ci(z.loc[g,'cluster_ci_low'], z.loc[g,'cluster_ci_high'])}" for g in ("none","reddit")} | {"range over omissions": f"{pts(z.estimate.min())}–{pts(z.estimate.max())}"}
o, n = both(infl)
for k in o: add("Leave-one-genre (broad)", k, o[k], n[k])

# non-target median for calibration-table gaps
def ntm(d):
    s = rd(d, "gum_erst_adjacent_isocolon_scores.tsv")
    broad = {"joint-list","joint-disjunction","adversative-contrast","adversative-antithesis","adversative-concession"}
    return None
out = ["| Section | Quantity | Old (bug + underscores) | New (fixed + restored) | Changed |", "|---|---|---|---|---|"]
for sec, lab, paper, o_, n_ in rows:
    out.append(f"| {sec} | {lab} | {o_} | {n_} | {'' if str(o_)==str(n_) else '●'} |")
open(f"{S}/before_after.md","w").write("\n".join(out)+"\n")
print("\n".join(out))
