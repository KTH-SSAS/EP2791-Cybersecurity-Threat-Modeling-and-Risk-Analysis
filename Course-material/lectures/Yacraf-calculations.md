# Yacraf calculations and statistical extensions

This document explains the calculations implemented by the Yacraf calculator, including its statistical treatment of distribution-valued inputs. It complements the [Yacraf paper](https://link.springer.com/article/10.1007/s10207-023-00713-y). For installation, input syntax, settings, and GUI instructions, see the [Yacraf calculator user guide](../../YACRAF-Calculator-Tool/README.md).

The calculator supports both the paper-compatible single-value workflow and additional statistical functionality. These have different theoretical status and must not be reported as though they were the same method.

## Contents

1. [Status of the calculations](#status-of-the-calculations)
2. [Notation](#notation)
3. [Bundled Yacraf input calculations](#bundled-yacraf-input-calculations)
4. [Distribution-valued inputs](#distribution-valued-inputs)
5. [Empirical Monte Carlo propagation](#empirical-monte-carlo-propagation)
6. [Global Attack Difficulty](#global-attack-difficulty)
7. [Threat Event Probability, Loss Probability, and Loss Risk](#threat-event-probability-loss-probability-and-loss-risk)
8. [Probability of Success modes](#probability-of-success-modes)
9. [Results, percentiles, and repeated runs](#results-percentiles-and-repeated-runs)
10. [How the bundled metamodel implements the calculations](#how-the-bundled-metamodel-implements-the-calculations)
11. [Supplementary: closed-form survival mappings](#supplementary-closed-form-survival-mappings)

## Status of the calculations

| Calculation or behavior | Status | Interpretation |
| --- | --- | --- |
| Core Yacraf calculation chain, including $TEP=PoC\cdot PoA$, the single-value PoS result, $LR=LM\cdot LP$, and actor-risk aggregation | **Paper-compatible behavior** | Implements the ordinary Yacraf calculation chain represented by the bundled metamodel. |
| Simplified, mean-centred default estimates for calculated $PoC$ and $PoA$ | **Calculator implementation** | Operationalizes the framework's qualitative prompts; it is not presented as the only valid analyst judgment. |
| End-user override of calculated $PoC$ or $PoA$ | **Analyst judgment** | Replaces a simplified default estimate with the analyst's scalar probability or probability distribution while leaving the bundled metamodel unchanged. |
| Empirical Monte Carlo propagation and attack-plan-aware Global Difficulty aggregation | **Calculator statistical implementation** | Propagates distribution-valued inputs without fitting an output distribution family. This is the calculator's numerical implementation for uncertain inputs. |
| Independent union of several abuse-case contributions to one loss | **Explicit calculator assumption** | Assumes the separate loss causes are independent and not mutually exclusive. Dependence or mutual exclusivity must be modeled manually. |
| Conditional PoS distribution | **Optional theoretical extension** | Returns a distribution of success probabilities conditional on realized Global Difficulty. It is not the single-value PoS calculation described in the Yacraf paper. |

## Notation

| Symbol | Meaning |
| --- | --- |
| $AtAS$ | Accessibility to Attack Surface |
| $WoO$ | Window of Opportunity |
| $AtR$ | Ability to Repudiate |
| $PD$ | Perceived Deterrence |
| $PEoA$ | Perceived Ease of Attack |
| $PBoS$ | Perceived Benefit of Success |
| $RT$ | Risk Tolerance |
| $CfCD$ | Concern for Collateral Damage |
| $Sk$ | Attacker Skill |
| $Res$ | Attacker Resources |
| $Sp$ | Attacker Sponsorship |
| $TC$ | Threat Capability |
| $LD$ | Local Difficulty: the incremental difficulty of one attack event |
| $GD$ | Global Difficulty: the total difficulty of the easiest complete plan reaching an attack event |
| $ES$ | Effort Spent by the attacker |
| $PoC$ | Probability of Contact |
| $PoA$ | Probability of Action |
| $TEP$ | Threat Event Probability |
| $PoS$ | Probability of Success, conditional on an attack being attempted |
| $LM$ | Loss Magnitude |
| $LP$ | Loss Probability |
| $LR$ | Loss Risk |
| $AR$ | Actor Risk |
| $DMI$ | Defense Mechanism Impact: difficulty added by a connected defense |
| $DMC$ | Defense Mechanism Cost: a separate decision input |
| $DME$ | Defense Mechanism Existence: a conceptual factor in the framework figure, not a stored calculator attribute |
| $N$ | Number of Monte Carlo samples |
| $s,t$ | Monte Carlo sample indices |

All difficulty and effort quantities compared in the calculations must use compatible units and refer to the same attacker, attack opportunity, and time horizon.

![Overview of the Yacraf risk-calculation framework](Risk_calculator_framework.png)

## Bundled Yacraf input calculations

The bundled metamodel uses values from $0$ to $10$ for the contributing attacker and abuse-case assessments. The dotted or qualitative relationships in the framework are prompts for analyst judgment, so forming numerical calculations from them is challenging. The tool therefore deploys simplified, mean-centred arithmetic formulas for these calculations. The $PoC$ and $PoA$ values calculated this way can also be overridden by the end user to capture the analyst's own judgment.

Threat Capability is the arithmetic mean of attacker Skill, Resources, and Sponsorship:

$$
TC=\frac{Sk+Res+Sp}{3}.
$$

Probability of Contact is the mean of Accessibility to Attack Surface and Window of Opportunity, scaled from $0$ – $10$ to $0$ – $1$:

$$
PoC=0.1\cdot\frac{AtAS+WoO}{2}.
$$

Probability of Action combines positively formulated inputs directly and reverses negatively formulated inputs with $10-x$ before taking and scaling the mean:

$$
PoA
=0.1\cdot\frac{
PEoA+PBoS+RT+(10-AtR)+(10-PD)+(10-CfCD)
}{6}.
$$

Threat Event Probability is then

$$
TEP=PoC\cdot PoA.
$$

These formulas remain the defaults. In particular, the bundled metamodel calculates $TC$ but leaves Effort Spent and Local Difficulty as manual assessments informed by the connected qualitative factors. Likewise, the model can use $TC$ to highlight relevant considerations without automatically converting it into $LD$, $AtAS$, or $ES$.

### Analyst overrides for Probability of Contact and Probability of Action

An analyst can replace either calculated $PoC$ or calculated $PoA$ on an abuse case without editing the bundled metamodel. In a `System View`, select the calculated attribute, press `E`, enter either a scalar probability from `0` through `1` or any [supported distribution specification](#distribution-valued-inputs), and choose `Apply override`. A scalar outside $[0,1]$ is rejected. Choose `Use calculated value` later to remove the analyst override and return to the applicable formula above.

The override specification is persisted when the model is saved. A scalar remains fixed, while a distribution specification is sampled again on every `Calculate` run. Every realized distribution sample is clipped to $[0,1]$ before use; this is especially relevant to unbounded normal, lognormal, and exponential distributions. For example, `normal / 0.6 / 0.3` is a valid probability override even though the source distribution can generate values above $1$.

The selected values replace the calculated parameter sample by sample in the ordinary calculation chain:

$$
TEP^{(s)}=PoC^{(s)}PoA^{(s)}.
$$

A scalar is broadcast across all samples. Consequently, a distribution-valued $PoC$ or $PoA$ produces distribution-valued $TEP$ and propagates through the loss-probability, loss-risk, and actor-risk calculations on aligned sample indices. The override's empirical distribution can be inspected with `Plot distribution` after it has been applied.

A temporary override set by a custom script has higher precedence than a saved analyst override. Clearing the script override reveals the saved analyst override again; it does not silently return the attribute to the bundled formula. Report any override used in an analysis, because the result no longer follows the default $PoC$ or $PoA$ estimate.

## Distribution-valued inputs

The calculator accepts a fixed non-negative value or a non-negative uniform, triangular, zero-truncated normal, lognormal, or exponential distribution. A deterministic non-negative shift may also be added to a named distribution. The parameterizations are:

- uniform: minimum and maximum;
- triangular: minimum, mode, and maximum;
- zero-truncated normal: arithmetic mean and standard deviation before truncation at zero;
- lognormal: median and geometric standard deviation; and
- exponential: mean, equivalently its scale.

For a shifted input, let $X$ follow the named distribution and let $c\geq0$ be the stated offset. Each resulting sample is

$$
Y^{(s)}=c+X^{(s)}.
$$

For example, `1 + lognormal / 5 / 2` uses a lognormal distribution with median $5$ and geometric standard deviation $2$, then adds $1$ to every sampled value. The shifted distribution therefore has lower bound $1$ and median $6$. The offset is deterministic, not another uncertain input.

These names describe the input distributions only. The calculator does not force a named distribution family on an aggregated result, and instead operates on numerical distributions based on sampling.

In the bundled metamodel, named distributions are accepted for attack-event Local and Global Difficulty and their hidden intermediate values, abuse-case Effort Spent, Loss Magnitude and Loss Risk, Actor Risk, and Defense Mechanism Cost and Impact. Probability of Contact and Probability of Action are scalar results by default, but either can become distribution-valued through an analyst override. Threat Event Probability and downstream loss probabilities can then become empirical distributions through samplewise propagation. Probability of Success and Loss Probability can also become empirical distributions when Conditional PoS mode produces distribution-valued downstream results. A custom metamodel may assign the sampled-distribution value type to additional fields.

## Empirical Monte Carlo propagation

For each calculation run, the calculator draws $N$ values from every manually entered distribution:

$$
x_j^{(s)} \sim X_j, \qquad s=1,\ldots,N.
$$

It then evaluates the complete model for sample index $s$, producing $y^{(1)},\ldots,y^{(N)}$. This sample vector is the empirical output distribution. Displayed quantiles and plots are calculated directly from these empirical samples; the calculator does not assume that the output is normal, triangular, or any other named family and does not fit such a family after aggregation.

A fixed input such as $2$ is expanded to $2$ in every sample. Arithmetic involving a distribution and a scalar broadcasts the scalar across all $N$ samples, while arithmetic involving distributions is performed on aligned sample indices.

Different manually entered sources are sampled independently. When the same local attack event is reused through several graph branches or linked views, its samples are cached for that calculation run and reused consistently.

The Monte Carlo sample count controls numerical resolution rather than model uncertainty. More samples normally make quantiles and probability estimates more stable, but they do not remove uncertainty represented by the input distributions.

## Global Attack Difficulty

Every attack event—including root, intermediate, AND, OR, and terminal events—has both a Local Difficulty ($LD$) and a Global Difficulty ($GD$). Local Difficulty is the incremental cost of performing the event itself. Global Difficulty is the total cost of the easiest complete attack plan that reaches and performs it, including the impact of connected defenses.

Consequently, a root attack event without a connected defense has $GD=LD$. A downstream attack event aggregates its predecessors' **global** difficulties and then adds its own Local Difficulty and connected Defense Mechanism Impact. 

Let $c_r^{(s)}$ be the sampled difficulty contribution of one atomic source $r$. An atomic source can be an attack event's Local Difficulty or a connected Defense Mechanism Impact. A complete feasible attack plan $p$ is represented as a set of required atomic sources. Its total difficulty in sample $s$ is

$$
GD_{a,p}^{(s)} = \sum_{r \in p} c_r^{(s)}.
$$

If $\mathcal{P}_a$ is the set of feasible plans that reach attack event $a$, the event's Global Difficulty sample is

$$
GD_a^{(s)} = \min_{p \in \mathcal{P}_a} GD_{a,p}^{(s)}.
$$

The gate operations construct the feasible plans as follows:

1. `OR` collects the alternative input plans. The easiest alternative may be different in different Monte Carlo samples.
2. `AND` forms every required combination and uses set union on the atomic sources. A Local Difficulty or Defense Mechanism Impact shared by two branches is therefore charged once rather than twice.

![Illustration of sample-aligned OR and AND Global Difficulty aggregation](calculation-figures/monte_carlo_aggregation.svg)

The result at every attack event is therefore the empirical distribution of the easiest complete plan reaching that event—not a sum or minimum calculated from only the three displayed percentiles.

Defense Mechanism Cost ($DMC$) is a separate input for comparing or prioritizing defenses. It is not added to Global Difficulty and does not automatically propagate into Loss Probability, Loss Risk, or Actor Risk. Defense Mechanism Impact ($DMI$), by contrast, is added directly to the attack plan when the defense is connected. The framework's Defense Mechanism Existence ($DME$) thus deploys the $DMI$.

## Threat Event Probability, Loss Probability, and Loss Risk

The bundled metamodel separates the probability that an attack is initiated from the probability that an initiated attack succeeds:

$$
TEP = PoC \cdot PoA.
$$

Probability of Action therefore does **not** alter an attack event's PoS. PoS answers the conditional question: given this Effort Spent and Global Difficulty, what is the probability that the attempted attack succeeds? The abuse-case probabilities enter the Loss Probability calculation instead.

### One abuse case contributing to a loss

For every abuse case $j$ that can cause a loss, the calculator pairs its Threat Event Probability with the PoS of its terminal attack event and calculates one loss-cause contribution:

$$
p_j = TEP_j \cdot \mathrm{PoS}_{j,\mathrm{terminal}}.
$$

With one abuse case, this directly gives

$$
LP=TEP\cdot\mathrm{PoS}_{\mathrm{terminal}},
\qquad
LR=LM\cdot LP.
$$

### Several abuse cases contributing to the same loss

The calculator assumes that separate abuse-case contributions are independent and not mutually exclusive. Under that assumption, the Loss Probability is their probability union:

$$
LP
= \Pr\!\left(\bigcup_j L_j\right)
= 1-\prod_j(1-p_j),
\qquad
LR = LM \cdot LP.
$$

For example, with two contributions $p_1=0.10$ and $p_2=0.12$,

$$
LP=1-(1-0.10)(1-0.12)=0.208.
$$

The result is neither the simple sum $0.22$ nor the product $0.012$.

![Propagation from abuse case and terminal attack event to loss probability and risk](calculation-figures/loss_risk_flow.svg)

System-view connections are direct, not transitive. For each contribution, connect the abuse case and its terminal attack event directly to the loss. The calculator associates them by following the attack graph from that abuse case to the terminal event. Every connected abuse case must lead to exactly one of the loss's connected terminal attack events, and every connected terminal event must be associated with at least one abuse case. Several abuse cases may legitimately lead to the same terminal event. Ambiguous or unmatched connections produce a setup warning instead of silently multiplying unrelated inputs.

If the abuse cases are mutually exclusive, dependent, or otherwise require a different overlap model, the independent-union formula is not valid. Calculate the appropriate combined probability separately, override $LP$ manually—for example through a script—and document the chosen dependence assumption.

With the default scalar $PoC$ and $PoA$ calculations and `Single success ratio` mode, the $p_j$ values and $LP$ are scalar. A distribution-valued Loss Magnitude still produces a distribution-valued Loss Risk:

$$
LR^{(s)}=LM^{(s)}LP.
$$

If an analyst supplies a distribution-valued $PoC$ or $PoA$, or if Conditional PoS mode supplies a distribution-valued PoS, the complete probability and risk chain is evaluated sample by sample. Scalar operands are broadcast across the samples:

$$
TEP_j^{(s)}=PoC_j^{(s)}PoA_j^{(s)},
\qquad
p_j^{(s)}=TEP_j^{(s)}\mathrm{PoS}_{j,\mathrm{terminal}}^{(s)},
$$

$$
LP^{(s)}=1-\prod_j\left(1-p_j^{(s)}\right),
\qquad
LR^{(s)}=LM^{(s)}LP^{(s)}.
$$

For an actor associated with loss events $k$, the bundled metamodel aggregates Actor Risk by addition:

$$
AR=\sum_k LR_k.
$$

When any $LR_k$ is distribution-valued, this sum is evaluated on aligned sample indices. The analyst remains responsible for defining loss events so that adding their risks is meaningful; overlapping descriptions of the same consequence can otherwise double-count risk.

(The gray Total Risk box in the framework figure is conceptual. The bundled calculator aggregates Loss Risk into Actor Risk but does not automatically combine several actors into one additional Total Risk attribute.)

## Probability of Success modes

### Single success ratio: paper-compatible mode

Let $ES^{(s)}$ be a sampled Effort Spent value and $GD_a^{(s)}$ the sampled Global Difficulty of attack event $a$. `Single success ratio` reports one scalar:

$$
\widehat{\mathrm{PoS}}_a
= \frac{1}{N}\sum_{s=1}^{N}
\mathbf{1}\!\left[ES^{(s)} > GD_a^{(s)}\right].
$$

Every aligned pair is one simulated attack situation. It contributes $1$ when effort is strictly greater than difficulty and $0$ otherwise. The result is the fraction of successful situations and estimates $\Pr(ES>GD_a)$. Equality counts as failure. This is the default mode because it returns the single probability used by the paper-compatible workflow.

### Conditional PoS distribution

> **Important:** `Conditional PoS distribution` is an extension implemented by the calculator. It is not the single-value PoS calculation described in the Yacraf paper.

#### Empirical survival function: what the calculator actually computes

In Conditional PoS mode, the calculator draws $N$ Effort Spent ($ES$) samples and obtains $N$ Global Difficulty ($GD_a$) realizations by propagating the attack graph's sampled inputs. For **each** realized difficulty $g$, it asks: *What fraction of all sampled effort values is strictly greater than $g$?* This fraction is the empirical survival function at $g$. The calculator does not evaluate a closed-form cumulative distribution function (CDF), fit a probability family to the output, or compare only the effort sample at the same index.

For a small hand-counted example, suppose one run produces these four **realized samples**, not distribution parameters:

| Sampled Effort Spent $ES$ | Sampled Global Difficulty $GD_a$ |
| --- | --- |
| $[2,4,6,8]$ | $[3,5,7,9]$ |

Hold the effort samples fixed and check each difficulty against all four of them:

| Difficulty realization $g$ | Effort samples with $ES>g$ | Empirical survival $\widehat S_{ES}(g)$ |
| --- | --- | --- |
| $3$ | $4,6,8$ | $3/4=0.75$ |
| $5$ | $6,8$ | $2/4=0.50$ |
| $7$ | $8$ | $1/4=0.25$ |
| $9$ | None | $0/4=0$ |

The attack event's Conditional PoS output is therefore the empirical sample vector $[0.75,0.50,0.25,0]$. These are four **success probabilities conditional on four plausible difficulty realizations**, not four binary success/failure outcomes. The tool can show their percentiles or plot the full empirical distribution. With only four effort samples, the estimates move in steps of $1/4$; the user-selected larger sample count normally makes the estimate more stable. If an effort sample equals $g$, it is excluded because success requires $ES>g$.

In notation, $s$ selects a difficulty realization and $t$ ranges over **all** effort samples:

$$
Q_a^{(s)}
= \widehat S_{ES}\!\left(GD_a^{(s)}\right)
= \frac{1}{N}\sum_{t=1}^{N}
\mathbf{1}\!\left[ES^{(t)} > GD_a^{(s)}\right].
$$

Sorting the effort samples makes these counts efficient. The output $Q_a^{(1)},\ldots,Q_a^{(N)}$ is retained as an empirical probability distribution. If $F_{ES}(g)=\Pr(ES\leq g)$ is the theoretical CDF of Effort Spent, its theoretical survival function is $S_{ES}(g)=1-F_{ES}(g)=\Pr(ES>g)$. The empirical fractions approximate that function from the sampled values; they need not equal its [closed-form expression](#supplementary-closed-form-survival-mappings) in a finite run.

#### Why retain the conditional distribution?

The scalar ratio integrates over all uncertainty in Global Difficulty and returns one number. That is often exactly what is needed for expected risk, but it hides whether success is nearly constant or changes substantially between low- and high-difficulty realizations. Conditional mode retains this variation.

As an **idealized theoretical illustration**, suppose $ES\sim\mathrm{Uniform}(0,10)$ and each of the following two Global Difficulty values is equally likely. Both scenarios have mean Conditional PoS $0.50$, and therefore the same scalar PoS in the large-sample limit. A finite calculator run obtains **empirical estimates** from its actual effort samples rather than using the analytical values in this table; small runs need not be close to them:

| Scenario | Possible $GD$ values | Analytical Conditional PoS values $Q(g)=\Pr(ES>g)$ | What the scalar hides |
| --- | --- | --- | --- |
| Nearly constant difficulty | $4.9,\ 5.1$ | $0.51,\ 0.49$ | Success stays close to 50% for either realization. |
| Strongly varying difficulty | $1,\ 9$ | $0.90,\ 0.10$ | Success changes from very likely to very unlikely. |

Thus a scalar value of $0.50$ cannot distinguish the narrow distribution $\{0.49,0.51\}$ from the wide distribution $\{0.10,0.90\}$. The Conditional PoS output makes that difference visible while preserving approximately the same mean as the sample count grows.

#### Interpretation and relationship to the scalar result

| Mode | Returned object | Question answered |
| --- | --- | --- |
| `Single success ratio` | One number $\widehat{\Pr}(ES>GD_a)$ | Across all simulated effort-and-difficulty pairs, what fraction succeeds? |
| `Conditional PoS distribution` | Samples $Q_a^{(s)}$ in $[0,1]$ | How does the chance of success vary over plausible realized Global Difficulty values? |

The conditional output is **not** a posterior distribution or confidence interval for one unknown PoS, and it is not a vector of Bernoulli success/failure outcomes. Its percentiles describe variation in $\Pr(ES>g)$ caused by uncertain $g$. They do not quantify estimation confidence; increasing $N$ only makes the empirical approximation smoother and more stable.

Conditional mode treats Effort Spent $ES$ and Global Difficulty $GD_a$ as independent. Under this assumption,

$$
\mathbb{E}_{GD_a}\!\left[\Pr(ES>GD_a\mid GD_a)\right]
= \Pr(ES>GD_a),
$$

so the mean of the Conditional PoS samples should approach the scalar PoS as the sample count grows. Their medians and other percentiles need not equal the scalar probability.

If effort and difficulty are dependent—for example, if better-resourced attackers systematically choose harder routes—the correct quantity requires a joint model such as $\Pr(ES>g\mid GD_a=g)$. The current calculator does not model that dependence. Such dependence must be captured with new explicit modelling with updated values for the attack cost in the attack events.

#### Appropriate use and reporting

It is suggested to use Conditional PoS as a default as it provides a more nuanced result for the overall risk. However, for more simplified calculations the `single success ratio` can be convenient.

## Results, percentiles, and repeated runs

Each press of `Calculate` clears the per-run sample cache and draws new samples from every manually declared distribution. A reused source keeps the same samples everywhere within that one run, but a later run draws a new realization. The calculator currently has no user-facing random-seed setting. Small differences between repeated results are therefore expected, especially at low sample counts or in distribution tails.

Calculated sample arrays are not stored in save files; the selected sample count, percentile mode, PoS mode, and any analyst-entered $PoC$ or $PoA$ override specifications are stored. Reopening and recalculating a save regenerates its empirical distributions, including distribution-valued probability overrides.

The two display modes summarize empirical samples as follows:

- `P0 / P50 / P100` shows the smallest observed sample, median, and largest observed sample. `P0` and `P100` are sample extrema, not necessarily the theoretical lower and upper bounds of the underlying distribution.
- `P5 / P50 / P95` shows the empirical 5th percentile, median, and 95th percentile. It suppresses the most extreme 5% of sampled values in each tail from the displayed interval but does not remove them from the underlying sample vector.

The selection changes only the three displayed values and percentile markers. It does not change sampling, downstream calculations, or the full empirical histogram and cumulative distribution available through `Plot distribution`.

A saved analyst override of $PoC$ or $PoA$ takes precedence over the bundled calculation for that attribute. An explicit temporary attribute override applied through a custom script has still higher precedence. Downstream calculations consume whichever value has precedence. Clearing a script override exposes the saved analyst override again; choosing `Use calculated value` in the attribute dialog removes the saved override. A reported result that uses any override must identify it, because the overridden attribute no longer follows the default equation documented here.

## How the bundled metamodel implements the calculations

The bundled Metamodel Views encode Yacraf and are expected to remain unchanged during ordinary use. Their Input blocks implement the transformations and relationships consumed by the calculations above.

The metamodel editor exposes the following generic operations:

| Symbol | Operation | Behavior |
| --- | --- | --- |
| `M` | Mean | Arithmetic mean of all inputs; distribution-valued inputs are averaged sample by sample. |
| `&` | AND/addition | Sum of all inputs. For attack-plan-aware values it combines all required atomic sources and counts a shared source once. |
| `\|` | OR/minimum | Minimum of the inputs. For attack-plan-aware values it retains the alternative plans so the easiest plan can vary by sample. |
| `*` | Multiplication | Product of all inputs, evaluated sample by sample when needed. The bundled Loss Probability attribute specializes this operation by pairing loss causes and taking their independent probability union. |
| `/` | Division | Exactly two ordered inputs, calculated as input (1) divided by input (2), sample by sample when needed. |
| `T` | Effort comparison | Exactly two ordered inputs: Effort Spent (1) and Global Difficulty (2). It applies the selected PoS mode using the strict comparison $ES>GD$. |
| `Q` | Qualitative | No numerical operation. The output remains a manual assessment while the connections document and highlight relevant considerations. |

After an operation, the destination attribute applies its Metamodel Input scalar and offset:

$$
y_{\mathrm{adjusted}}=\alpha y+\beta.
$$

The destination value type then enforces its range. Sampled-distribution results are clipped to be non-negative, and probability results are clipped to $[0,1]$. These are metamodel attribute settings; System View connections pass values without an editable scalar or offset.

The attributes highlighted by (1) in the following figure accept values between 0 and 10. The shown addition, multiplication by $-1$, and offset $10$ feed a temporary hidden attribute and reverse a negatively formulated scale into a positive one, or vice versa. Algebraically, the transformation is

$$
x \longmapsto 10-x.
$$

For example, it transforms $3$ into $7$.

Calculation type `Q`, highlighted by (2), illustrates the qualitative operation described in the table. Its connections visualize the relationship and allow relevant inputs to be highlighted in the System View.

![Calculations and qualitative relationships in the bundled Yacraf metamodel](calculation-figures/configuration_explanation.svg)

For GUI instructions and the advanced metamodel editor, return to the [Yacraf calculator user guide](../../YACRAF-Calculator-Tool/README.md). Source-level implementation notes are available in the [calculation code overview](../../YACRAF-Calculator-Tool/src/blocks_calculation/README.md).

## Supplementary: closed-form survival mappings

The preceding [empirical worked example](#empirical-survival-function-what-the-calculator-actually-computes) describes the **actual Conditional PoS implementation**. The following formulas are analytical survival functions for idealized Effort Spent distributions. They can help explain the theoretical shape of the mapping or check a large-sample approximation, but the calculator does **not** evaluate these formulas when it calculates Conditional PoS. Finite empirical results may differ from the analytical values.

**Fixed effort.** For deterministic effort $ES=e$, strict comparison produces a step: $Q(g)=1$ when $g<e$ and $Q(g)=0$ when $g\geq e$.

**Shifted distributions.** If $ES=c+X$ for a non-negative fixed shift $c$, then

| Global Difficulty $g$ | Analytical survival $Q(g)$ |
| --- | --- |
| $g<c$ | $1$ |
| $g\geq c$ | $S_X(g-c)$ |

Thus the analytical survival function for any supported named distribution can be shifted by evaluating its unshifted survival function at $g-c$.

**Uniform.** For $ES\sim\mathrm{Uniform}(a,b)$, $Q(g)=1$ below $a$, $Q(g)=0$ at or above $b$, and

$$
Q(g)=\frac{b-g}{b-a}, \qquad a\leq g < b.
$$

When $a=b$, treat the uniform input as deterministic effort at $a$ rather than evaluating the fraction with a zero denominator.

The smooth line in the following figure is the **analytical** mapping for uniform effort, not the stepwise empirical survival curve of a finite sample. The calculator approximates it from the sampled effort values.

![Analytical uniform-effort survival mapping](calculation-figures/conditional_pos.svg)

**Triangular.** For $ES\sim\mathrm{Triangular}(a,m,b)$, where $m$ is the mode:

| Global Difficulty $g$ | Analytical survival $Q(g)$ |
| --- | --- |
| $g<a$ | $1$ |
| $a\leq g\leq m$ | $1-\frac{(g-a)^2}{(b-a)(m-a)}$ |
| $m<g<b$ | $\frac{(b-g)^2}{(b-a)(b-m)}$ |
| $g\geq b$ | $0$ |

If the mode equals an endpoint or all three parameters are equal, interpret the expression by its corresponding limiting or deterministic case.

For an **analytical** example, let $ES\sim\mathrm{Triangular}(2,5,8)$ and consider difficulty values $g=3$, $5$, and $7$:

| Difficulty $g$ | Closed-form calculation | Analytical $Q(g)$ |
| --- | --- | --- |
| $3$ | $1-(3-2)^2/((8-2)(5-2))$ | $17/18\approx0.944$ |
| $5$ | $1-(5-2)^2/((8-2)(5-2))$ | $1/2=0.500$ |
| $7$ | $(8-7)^2/((8-2)(8-5))$ | $1/18\approx0.056$ |

The theoretical mapping gives $\{0.944,0.500,0.056\}$ at those three difficulty values. These are **not** claimed to be the outputs of a finite calculator run; its empirical fractions depend on the effort samples actually drawn. The following figure shows the theoretical nonlinear shape.

![Analytical triangular-effort survival mapping](calculation-figures/conditional_pos_triangular.svg)

**Zero-truncated normal.** For the calculator's $ES\sim\mathrm{Normal}(\mu,\sigma^2)\mid ES\geq0$, with standard normal cumulative distribution function $\Phi$, $Q(g)=1$ for $g<0$, and for $g\geq0$,

$$
Q(g)=\frac{1-\Phi\!\left((g-\mu)/\sigma\right)}{1-\Phi\!\left(-\mu/\sigma\right)}.
$$

When $\sigma=0$, effort is deterministic and the mapping is a step at $\mu$.

**Lognormal.** For $ES\sim\mathrm{Lognormal}(\log m,\log^2 g_{\mathrm{sd}})$, where $m$ is the median and $g_{\mathrm{sd}}$ is the geometric standard deviation, $Q(g)=1$ for $g\leq0$, and

$$
Q(g)=1-\Phi\!\left(\frac{\log g-\log m}{\log g_{\mathrm{sd}}}\right), \qquad g>0.
$$

When $g_{\mathrm{sd}}=1$, effort is deterministic at the median.

**Exponential.** For $ES\sim\mathrm{Exponential}(\theta)$, where the mean (scale) $\theta>0$, $Q(g)=1$ for $g<0$, and

$$
Q(g)=e^{-g/\theta}, \qquad g\geq0.
$$

The strict comparison $ES>g$ is used in every case. Equality has probability zero for continuous distributions, but the distinction matters for deterministic or repeated empirical values.
