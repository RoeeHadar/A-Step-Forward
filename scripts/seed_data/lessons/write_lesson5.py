"""Write Lesson 5: linear_regression_least_squares"""
import json, os
BASE = os.path.dirname(os.path.abspath(__file__))

lesson = {
  "id": "linear_regression_least_squares",
  "type": "interactive",
  "subject": "statistics_probability",
  "title_en": "Linear Regression \u2014 Least Squares Method",
  "title_he": "\u05e8\u05d2\u05e8\u05e1\u05d9\u05d4 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea \u2014 \u05e9\u05d9\u05d8\u05ea \u05d4\u05e8\u05d9\u05d1\u05d5\u05e2\u05d9\u05dd \u05d4\u05e4\u05d7\u05d5\u05ea\u05d9\u05dd",
  "duration_min": 25,
  "level_min": "university",
  "agent_hints": "Students confuse correlation (r) with causation, and often misinterpret R^2 (e.g. thinking R^2=0.81 means 81 data points fit perfectly). Stress: (1) r measures linear association strength, not causation; (2) R^2 is the proportion of variance in y explained by the linear model; (3) the OLS line always passes through (x-bar, y-bar); (4) extrapolation is unreliable because the linear pattern may not hold outside the observed range. At university level, students should be able to derive the OLS formulas by minimizing SS_res with calculus.",
  "sections": [
    {
      "id": "problem_setup",
      "title_en": "Problem Setup \u2014 Fitting a Line to Data",
      "title_he": "\u05d4\u05d2\u05d3\u05e8\u05ea \u05d4\u05d1\u05e2\u05d9\u05d4 \u2014 \u05d4\u05ea\u05d0\u05de\u05ea \u05d9\u05e9\u05e8 \u05dc\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd",
      "level_min": "university",
      "body_en_md": "Given $n$ data points $(x_1, y_1), (x_2, y_2), \\ldots, (x_n, y_n)$, we want to find the line $\\hat{y} = a + bx$ that best fits the data.\n\n**Why not just connect all points?** With real data, no single line passes through all points (measurement error, natural variability). We need a principled criterion for \"best fit.\"\n\n**Least Squares Criterion.** For a line $\\hat{y} = a + bx$, define the **residual** for observation $i$ as:\n$$e_i = y_i - \\hat{y}_i = y_i - (a + bx_i).$$\n\nThe **residual sum of squares** is:\n$$SS_{\\text{res}} = \\sum_{i=1}^n e_i^2 = \\sum_{i=1}^n (y_i - a - bx_i)^2.$$\n\nOLS (**ordinary least squares**) chooses $a$ and $b$ to **minimize** $SS_{\\text{res}}$. This minimization is done by calculus: set $\\partial SS_{\\text{res}}/\\partial a = 0$ and $\\partial SS_{\\text{res}}/\\partial b = 0$, then solve the **normal equations**.",
      "body_he_md": "\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd $n$ \u05e0\u05e7\u05d5\u05d3\u05d5\u05ea $(x_1, y_1), \\ldots, (x_n, y_n)$. \u05e8\u05d5\u05e6\u05d9\u05dd \u05dc\u05de\u05e6\u05d5\u05d0 \u05d9\u05e9\u05e8 $\\hat{y} = a + bx$ \u05d4\u05de\u05ea\u05d0\u05d9\u05dd \u05d1\u05d9\u05d5\u05ea\u05e8 \u05dc\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd.\n\n**\u05dc\u05de\u05d4 \u05dc\u05d0 \u05e8\u05e7 \u05dc\u05d7\u05d1\u05e8 \u05d0\u05ea \u05db\u05dc \u05d4\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea?** \u05d1\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd \u05d0\u05de\u05d9\u05ea\u05d9\u05d9\u05dd, \u05d0\u05d9\u05df \u05d9\u05e9\u05e8 \u05d0\u05d7\u05d3 \u05e9\u05e2\u05d5\u05d1\u05e8 \u05d3\u05e8\u05da \u05db\u05dc \u05d4\u05e0\u05e7\u05d5\u05d3\u05d5\u05ea. \u05e6\u05e8\u05d9\u05da \u05e7\u05e8\u05d9\u05d8\u05e8\u05d9\u05d5\u05df \u05de\u05e2\u05d5\u05d2\u05df \u05dc\u201c\u05d4\u05ea\u05d0\u05de\u05d4 \u05d4\u05d8\u05d5\u05d1\u05d4 \u05d1\u05d9\u05d5\u05ea\u05e8\u201d.\n\n**\u05e7\u05e8\u05d9\u05d8\u05e8\u05d9\u05d5\u05df \u05d4\u05e8\u05d9\u05d1\u05d5\u05e2\u05d9\u05dd \u05d4\u05e4\u05d7\u05d5\u05ea\u05d9\u05dd.** \u05e2\u05d1\u05d5\u05e8 \u05d9\u05e9\u05e8 $\\hat{y} = a + bx$, \u05d4**\u05e9\u05d0\u05e8\u05d9\u05ea** \u05e2\u05d1\u05d5\u05e8 \u05ea\u05e6\u05e4\u05d9\u05ea $i$:\n$$e_i = y_i - \\hat{y}_i = y_i - (a + bx_i).$$\n\n**\u05e1\u05db\u05d5\u05dd \u05e8\u05d9\u05d1\u05d5\u05e2\u05d9 \u05d4\u05e9\u05d0\u05e8\u05d9\u05d5\u05ea:**\n$$SS_{\\text{res}} = \\sum_{i=1}^n (y_i - a - bx_i)^2.$$\n\nOLS \u05d1\u05d5\u05d7\u05e8 $a$ \u05d5-$b$ \u05d4\u05de**\u05de\u05d6\u05e2\u05e8\u05d9\u05dd** \u05d0\u05ea $SS_{\\text{res}}$ \u05d1\u05d0\u05de\u05e6\u05e2\u05d5\u05ea \u05d7\u05e9\u05d1\u05d5\u05df \u05d3\u05d9\u05e4\u05e8\u05e0\u05e6\u05d9\u05d0\u05dc\u05d9."
    },
    {
      "id": "ols_formulas",
      "title_en": "OLS Formulas",
      "title_he": "\u05e0\u05d5\u05e1\u05d7\u05d0\u05d5\u05ea OLS",
      "level_min": "university",
      "body_en_md": "Minimizing $SS_{\\text{res}}$ by setting partial derivatives to zero yields the **OLS formulas**:\n\n$$\\boxed{b = \\frac{S_{xy}}{S_{xx}} = \\frac{\\sum_{i=1}^n (x_i - \\bar{x})(y_i - \\bar{y})}{\\sum_{i=1}^n (x_i - \\bar{x})^2}, \\qquad a = \\bar{y} - b\\bar{x},}$$\n\nwhere $\\bar{x} = \\frac{1}{n}\\sum x_i$ and $\\bar{y} = \\frac{1}{n}\\sum y_i$ are the sample means.\n\n**Equivalent forms for computation:**\n$$S_{xx} = \\sum x_i^2 - n\\bar{x}^2, \\quad S_{xy} = \\sum x_i y_i - n\\bar{x}\\bar{y}, \\quad S_{yy} = \\sum y_i^2 - n\\bar{y}^2.$$\n\n**Key property:** The OLS regression line always passes through the point $(\\bar{x}, \\bar{y})$ (the center of mass of the data).\n\n**Interpretation of $b$:** A one-unit increase in $x$ is associated with a $b$-unit change in the predicted $y$. This is an association, not necessarily causation.",
      "body_he_md": "\u05d4\u05e7\u05d8\u05e0\u05ea $SS_{\\text{res}}$ \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d0\u05e4\u05e1\u05d5\u05e1 \u05e0\u05d2\u05d6\u05e8\u05d5\u05ea \u05d7\u05dc\u05e7\u05d9\u05d5\u05ea \u05e0\u05d5\u05ea\u05e0\u05ea \u05d0\u05ea **\u05e0\u05d5\u05e1\u05d7\u05d0\u05d5\u05ea OLS**:\n\n$$\\boxed{b = \\frac{S_{xy}}{S_{xx}}, \\qquad a = \\bar{y} - b\\bar{x}.}$$\n\n**\u05e6\u05d5\u05e8\u05d5\u05ea \u05e9\u05d9\u05e7\u05d5\u05dc\u05d9\u05d5\u05ea \u05dc\u05d7\u05d9\u05e9\u05d5\u05d1:**\n$$S_{xx} = \\sum x_i^2 - n\\bar{x}^2, \\quad S_{xy} = \\sum x_i y_i - n\\bar{x}\\bar{y}.$$\n\n**\u05ea\u05db\u05d5\u05e0\u05d4 \u05de\u05e8\u05db\u05d6\u05d9\u05ea:** \u05d9\u05e9\u05e8 \u05d4\u05e8\u05d2\u05e8\u05e1\u05d9\u05d4 \u05e2\u05d5\u05d1\u05e8 \u05ea\u05de\u05d9\u05d3 \u05d3\u05e8\u05da $(\\bar{x}, \\bar{y})$.\n\n**\u05e4\u05d9\u05e8\u05d5\u05e9 $b$:** \u05e2\u05dc\u05d9\u05d9\u05d4 \u05d1\u05d9\u05d7\u05d9\u05d3\u05d4 \u05d0\u05d7\u05ea \u05d1-$x$ \u05e7\u05e9\u05d5\u05e8\u05d4 \u05dc\u05e9\u05d9\u05e0\u05d5\u05d9 \u05e9\u05dc $b$ \u05d9\u05d7\u05d9\u05d3\u05d5\u05ea \u05d1-$\\hat{y}$ \u05d4\u05d7\u05d6\u05d5\u05d9 (קשר, \u05dc\u05d0 \u05d1\u05d4\u05db\u05e8\u05d7 \u05e1\u05d9\u05d1\u05ea\u05d9\u05d5\u05ea)."
    },
    {
      "id": "correlation_r2",
      "title_en": "Correlation Coefficient and $R^2$",
      "title_he": "\u05de\u05e7\u05d3\u05dd \u05d4\u05de\u05ea\u05d0\u05dd \u05d5-$R^2$",
      "level_min": "university",
      "body_en_md": "**Pearson correlation coefficient:**\n$$r = \\frac{S_{xy}}{\\sqrt{S_{xx}\\, S_{yy}}}, \\quad -1 \\leq r \\leq 1.$$\n\n- $r = 1$: perfect positive linear relationship.\n- $r = -1$: perfect negative linear relationship.\n- $r = 0$: no linear association (but could have nonlinear).\n- $|r|$ close to 1: strong linear association; close to 0: weak.\n\n**Coefficient of determination:**\n$$R^2 = r^2, \\quad 0 \\leq R^2 \\leq 1.$$\n\n$R^2$ is the **proportion of total variance in $y$ explained by the linear regression on $x$**.\n\nEquivalently: $R^2 = 1 - SS_{\\text{res}} / SS_{\\text{tot}}$ where $SS_{\\text{tot}} = S_{yy}$.\n\n**Example interpretation:** $R^2 = 0.81$ means the linear model explains 81% of the variability in $y$; the remaining 19% is unexplained by $x$ alone.",
      "body_he_md": "**מקדם המתאם של פירסון:**\n$$r = \\frac{S_{xy}}{\\sqrt{S_{xx}\\, S_{yy}}}, \\quad -1 \\leq r \\leq 1.$$\n\n- $r = 1$: \u05e7\u05e9\u05e8 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05d7\u05d9\u05d5\u05d1\u05d9 \u05de\u05d5\u05e9\u05dc\u05dd.\n- $r = -1$: \u05e7\u05e9\u05e8 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05e9\u05dc\u05d9\u05dc\u05d9 \u05de\u05d5\u05e9\u05dc\u05dd.\n- $r = 0$: \u05d0\u05d9\u05df \u05e7\u05e9\u05e8 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 (אך \u05d9\u05ea\u05db\u05df \u05e7\u05e9\u05e8 \u05dc\u05d0-\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9).\n\n**\u05de\u05e7\u05d3\u05dd \u05d4\u05e7\u05d1\u05d9\u05e2\u05d5\u05ea:**\n$$R^2 = r^2 = 1 - SS_{\\text{res}} / SS_{\\text{tot}}.$$\n\n$R^2$ \u05d4\u05d5\u05d0 **\u05d7\u05dc\u05e7 \u05d4\u05e9\u05e0\u05d5\u05ea \u05d4\u05db\u05dc\u05dc\u05d9\u05ea \u05d1-$y$ \u05d4\u05de\u05d5\u05e1\u05d1\u05e8\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05d3\u05d2\u05dd \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9**.\n\n**\u05d3\u05d5\u05d2\u05de\u05d4:** $R^2 = 0.81$ \u05e4\u05d9\u05e8\u05d5\u05e9\u05d5 \u05e9\u05d4\u05d3\u05d2\u05dd \u05de\u05e1\u05d1\u05d9\u05e8 81% \u05de\u05d4\u05e9\u05e4\u05e8\u05d5\u05ea \u05d1-$y$; 19% \u05e0\u05d5\u05ea\u05e8\u05d9\u05dd \u05d1\u05dc\u05ea\u05d9 \u05de\u05d5\u05e1\u05d1\u05e8\u05d9\u05dd \u05e2\u05dc \u05d9\u05d3\u05d9 $x$ \u05dc\u05d1\u05d3\u05d5."
    },
    {
      "id": "worked_example",
      "title_en": "Worked Example",
      "title_he": "\u05d3\u05d5\u05d2\u05de\u05d4 \u05de\u05dc\u05d0\u05d4",
      "level_min": "university",
      "body_en_md": "**Example.** Five students\u2019 study hours ($x$) and exam scores ($y$):\n\n| $x$ | 1 | 2 | 3 | 4 | 5 |\n|-----|---|---|---|---|---|\n| $y$ | 50 | 55 | 65 | 70 | 80 |\n\n**Step 1.** $\\bar{x} = 3$, $\\bar{y} = 64$.\n\n**Step 2.** $S_{xx} = (1-3)^2+(2-3)^2+(3-3)^2+(4-3)^2+(5-3)^2 = 4+1+0+1+4 = 10$.\n\n$S_{xy} = (1-3)(50-64)+(2-3)(55-64)+(3-3)(65-64)+(4-3)(70-64)+(5-3)(80-64)$\n$= (-2)(-14)+(-1)(-9)+(0)(1)+(1)(6)+(2)(16) = 28+9+0+6+32 = 75$.\n\n**Step 3.** $b = S_{xy}/S_{xx} = 75/10 = 7.5$. $a = \\bar{y} - b\\bar{x} = 64 - 7.5 \\cdot 3 = 41.5$.\n\n**Regression line:** $\\hat{y} = 41.5 + 7.5x$.\n\n**Step 4.** $S_{yy} = (-14)^2+(-9)^2+1^2+6^2+16^2 = 196+81+1+36+256 = 570$.\n$r = S_{xy}/\\sqrt{S_{xx}S_{yy}} = 75/\\sqrt{10 \\cdot 570} = 75/\\sqrt{5700} \\approx 75/75.5 \\approx 0.993$.\n$R^2 \\approx 0.986$: the model explains 98.6% of variance in scores.",
      "body_he_md": "**\u05d3\u05d5\u05d2\u05de\u05d4.** \u05d7\u05de\u05d9\u05e9\u05d4 \u05e1\u05d8\u05d5\u05d3\u05e0\u05d8\u05d9\u05dd, \u05e9\u05e2\u05d5\u05ea \u05dc\u05d9\u05de\u05d5\u05d3 ($x$) \u05d5\u05e6\u05d9\u05d5\u05df ($y$):\n\n| $x$ | 1 | 2 | 3 | 4 | 5 |\n|-----|---|---|---|---|---|\n| $y$ | 50 | 55 | 65 | 70 | 80 |\n\n$\\bar{x} = 3$, $\\bar{y} = 64$. $S_{xx} = 10$, $S_{xy} = 75$.\n\n$b = 75/10 = 7.5$, $a = 64 - 22.5 = 41.5$.\n\n**\u05d9\u05e9\u05e8 \u05d4\u05e8\u05d2\u05e8\u05e1\u05d9\u05d4:** $\\hat{y} = 41.5 + 7.5x$.\n\n$r \\approx 0.993$, $R^2 \\approx 0.986$: \u05d4\u05d3\u05d2\u05dd \u05de\u05e1\u05d1\u05d9\u05e8 98.6% \u05de\u05d4\u05e9\u05e4\u05e8\u05d5\u05ea \u05d1\u05e6\u05d9\u05d5\u05e0\u05d9\u05dd."
    },
    {
      "id": "prediction_residuals",
      "title_en": "Prediction, Residuals, and Diagnostics",
      "title_he": "\u05e0\u05d1\u05d5\u05d0\u05d4, \u05e9\u05d0\u05e8\u05d9\u05d5\u05ea \u05d5\u05d3\u05d9\u05d0\u05d2\u05e0\u05d5\u05e1\u05d8\u05d9\u05e7\u05d4",
      "level_min": "university",
      "body_en_md": "**Prediction.** For a new $x_0$, predict $\\hat{y}_0 = a + bx_0$.\n\n**Interpolation vs. extrapolation:** Interpolation (predicting within the range of observed $x$ values) is generally reliable. **Extrapolation** (predicting outside this range) is risky \u2014 the linear pattern may not extend.\n\n**Residuals.** $e_i = y_i - \\hat{y}_i$. Key properties of OLS residuals:\n- $\\sum e_i = 0$ (residuals sum to zero)\n- $\\sum x_i e_i = 0$ (residuals are uncorrelated with $x$)\n\n**Residual plot.** Plot $e_i$ vs. $\\hat{y}_i$ (or vs. $x_i$). A good model shows:\n- Residuals scattered randomly around 0 (no pattern).\n- Roughly constant spread (homoscedasticity).\n\nPatterns in residuals (curved trend, funnel shape, outliers) suggest the linear model is inadequate.",
      "body_he_md": "**\u05e0\u05d1\u05d5\u05d0\u05d4.** \u05e2\u05d1\u05d5\u05e8 $x_0$ \u05d7\u05d3\u05e9: $\\hat{y}_0 = a + bx_0$.\n\n**\u05d0\u05d9\u05e0\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4 \u05de\u05d5\u05dc \u05d0\u05e7\u05e1\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4:** \u05d0\u05d9\u05e0\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4 (תחזית \u05d1\u05ea\u05d7\u05d5\u05dd $x$ \u05d4\u05e0\u05e6\u05e4\u05d4) \u05d1\u05d3\u05e8\u05da \u05db\u05dc\u05dc \u05d0\u05de\u05d9\u05e0\u05d4. **\u05d0\u05e7\u05e1\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4** (\u05de\u05d7\u05d5\u05e5 \u05dc\u05ea\u05d7\u05d5\u05dd) \u05de\u05e1\u05d5\u05db\u05e0\u05ea \u2014 \u05d4\u05d3\u05e4\u05d5\u05e1 \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05e2\u05e9\u05d5\u05d9 \u05dc\u05d0 \u05dc\u05d4\u05ea\u05e7\u05d9\u05d9\u05dd.\n\n**\u05e9\u05d0\u05e8\u05d9\u05d5\u05ea.** $e_i = y_i - \\hat{y}_i$. \n\n**\u05d2\u05e8\u05e3 \u05e9\u05d0\u05e8\u05d9\u05d5\u05ea.** \u05de\u05e9\u05e8\u05d8\u05d8\u05d9\u05dd $e_i$ \u05de\u05d5\u05dc $\\hat{y}_i$. \u05d3\u05d2\u05dd \u05d8\u05d5\u05d1 \u05de\u05e8\u05d0\u05d4: \u05e4\u05d9\u05d6\u05d5\u05e8 \u05d0\u05e7\u05e8\u05d0\u05d9 \u05e1\u05d1\u05d9\u05d1 0 (\u05dc\u05dc\u05d0 \u05d3\u05e4\u05d5\u05e1). \u05d3\u05e4\u05d5\u05e1\u05d9\u05dd \u05d1\u05e9\u05d0\u05e8\u05d9\u05d5\u05ea \u05de\u05e8\u05de\u05d6\u05d9\u05dd \u05e9\u05d4\u05d3\u05d2\u05dd \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05d0\u05d9\u05e0\u05d5 \u05de\u05ea\u05d0\u05d9\u05dd."
    }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "body_en": "Which formula correctly gives the OLS slope $b$?",
      "body_he": "\u05d0\u05d9\u05d6\u05d5 \u05e0\u05d5\u05e1\u05d7\u05d0 \u05e0\u05d5\u05ea\u05e0\u05ea \u05e0\u05db\u05d5\u05df \u05d0\u05ea \u05e9\u05d9\u05e4\u05d5\u05e2 OLS $b$?",
      "options": [
        {"id": "a", "text_en": "$b = \\dfrac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sum(y_i - \\bar{y})^2}$", "text_he": "$b = \\dfrac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sum(y_i - \\bar{y})^2}$", "correct": False},
        {"id": "b", "text_en": "$b = \\dfrac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sum(x_i - \\bar{x})^2}$", "text_he": "$b = \\dfrac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sum(x_i - \\bar{x})^2}$", "correct": True},
        {"id": "c", "text_en": "$b = \\dfrac{\\bar{y}}{\\bar{x}}$", "text_he": "$b = \\dfrac{\\bar{y}}{\\bar{x}}$", "correct": False},
        {"id": "d", "text_en": "$b = \\dfrac{\\sum x_i y_i}{\\sum x_i^2}$", "text_he": "$b = \\dfrac{\\sum x_i y_i}{\\sum x_i^2}$", "correct": False}
      ],
      "explanation_en": "The OLS slope is $b = S_{xy}/S_{xx} = \\sum(x_i-\\bar{x})(y_i-\\bar{y}) / \\sum(x_i-\\bar{x})^2$. Option (a) divides by $S_{yy}$ instead of $S_{xx}$; option (d) is only valid when the regression passes through the origin.",
      "explanation_he": "\u05e9\u05d9\u05e4\u05d5\u05e2 OLS \u05d4\u05d5\u05d0 $b = S_{xy}/S_{xx}$. \u05d0\u05e4\u05e9\u05e8\u05d5\u05ea (א) \u05de\u05d7\u05dc\u05e7\u05ea \u05d1-$S_{yy}$ \u05d1\u05de\u05e7\u05d5\u05dd $S_{xx}$."
    },
    {
      "id": "q2",
      "type": "mcq",
      "body_en": "A regression of exam score on hours studied gives $R^2 = 0.81$. Which interpretation is correct?",
      "body_he": "\u05e8\u05d2\u05e8\u05e1\u05d9\u05d4 \u05e9\u05dc \u05e6\u05d9\u05d5\u05df \u05d1\u05d7\u05d9\u05e0\u05d4 \u05e2\u05dc \u05e9\u05e2\u05d5\u05ea \u05dc\u05d9\u05de\u05d5\u05d3 \u05e0\u05d5\u05ea\u05e0\u05ea $R^2 = 0.81$. \u05d0\u05d9\u05d6\u05d4 \u05e4\u05e8\u05e9\u05e0\u05d5\u05ea \u05e0\u05db\u05d5\u05e0\u05d4?",
      "options": [
        {"id": "a", "text_en": "81% of students scored exactly on the regression line", "text_he": "81% \u05de\u05d4\u05e1\u05d8\u05d5\u05d3\u05e0\u05d8\u05d9\u05dd \u05e7\u05d9\u05d1\u05dc\u05d5 \u05d1\u05d3\u05d9\u05d5\u05e7 \u05d0\u05ea \u05d4\u05e6\u05d9\u05d5\u05df \u05d4\u05e0\u05d7\u05d6\u05d4", "correct": False},
        {"id": "b", "text_en": "81% of the variance in exam scores is explained by the linear regression on study hours", "text_he": "81% \u05de\u05d4\u05e9\u05e4\u05e8\u05d5\u05ea \u05d1\u05e6\u05d9\u05d5\u05e0\u05d9\u05dd \u05de\u05d5\u05e1\u05d1\u05e8\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05e8\u05d2\u05e8\u05e1\u05d9\u05d4 \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9\u05ea \u05e2\u05dc \u05e9\u05e2\u05d5\u05ea \u05d4\u05dc\u05d9\u05de\u05d5\u05d3", "correct": True},
        {"id": "c", "text_en": "The correlation coefficient is $r = 0.81$", "text_he": "\u05de\u05e7\u05d3\u05dd \u05d4\u05de\u05ea\u05d0\u05dd \u05d4\u05d5\u05d0 $r = 0.81$", "correct": False},
        {"id": "d", "text_en": "Hours studied causes 81% improvement in exam scores", "text_he": "\u05e9\u05e2\u05d5\u05ea \u05d4\u05dc\u05d9\u05de\u05d5\u05d3 \u05d2\u05d5\u05e8\u05de\u05d5\u05ea \u05e9\u05d9\u05e4\u05d5\u05e8 \u05e9\u05dc 81% \u05d1\u05e6\u05d9\u05d5\u05e0\u05d9\u05dd", "correct": False}
      ],
      "explanation_en": "$R^2 = 0.81$ means the linear model accounts for 81% of the total variability (variance) in $y$. Option (c) is wrong because $r = \\sqrt{0.81} = 0.9$, not 0.81. Option (d) is wrong because correlation does not imply causation.",
      "explanation_he": "$R^2 = 0.81$ \u05d0\u05d5\u05de\u05e8 \u05e9\u05d4\u05d3\u05d2\u05dd \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05de\u05e1\u05d1\u05d9\u05e8 81% \u05de\u05d4\u05e9\u05e4\u05e8\u05d5\u05ea \u05d4\u05db\u05dc\u05dc\u05d9\u05ea \u05d1-$y$. \u05d0\u05e4\u05e9\u05e8\u05d5\u05ea (ג) \u05e9\u05d2\u05d5\u05d9\u05d9\u05d4 \u05db\u05d9 $r = 0.9$, \u05dc\u05d0 0.81."
    },
    {
      "id": "q3",
      "type": "mcq",
      "body_en": "Given $\\hat{y} = 5 + 3x$, what is the predicted $y$ when $x = 4$?",
      "body_he": "\u05e0\u05ea\u05d5\u05df $\\hat{y} = 5 + 3x$, \u05de\u05d4 \u05d4\u05d5\u05d0 $y$ \u05d4\u05d7\u05d6\u05d5\u05d9 \u05db\u05d0\u05e9\u05e8 $x = 4$?",
      "options": [
        {"id": "a", "text_en": "$12$", "text_he": "$12$", "correct": False},
        {"id": "b", "text_en": "$17$", "text_he": "$17$", "correct": True},
        {"id": "c", "text_en": "$20$", "text_he": "$20$", "correct": False},
        {"id": "d", "text_en": "$27$", "text_he": "$27$", "correct": False}
      ],
      "explanation_en": "$\\hat{y} = 5 + 3(4) = 5 + 12 = 17$.",
      "explanation_he": "$\\hat{y} = 5 + 3(4) = 17$."
    },
    {
      "id": "q4",
      "type": "mcq",
      "body_en": "A correlation of $r = -0.9$ between two variables $x$ and $y$ means:",
      "body_he": "מתאם $r = -0.9$ \u05d1\u05d9\u05df \u05e9\u05e0\u05d9 \u05de\u05e9\u05ea\u05e0\u05d9\u05dd $x$ \u05d5-$y$ \u05de\u05e9\u05de\u05e2\u05d5:",
      "options": [
        {"id": "a", "text_en": "$x$ causes $y$ to decrease", "text_he": "$x$ \u05d2\u05d5\u05e8\u05dd \u05dc-$y$ \u05dc\u05e8\u05d3\u05ea", "correct": False},
        {"id": "b", "text_en": "There is a strong negative linear association between $x$ and $y$", "text_he": "\u05e7\u05e9\u05e8 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05e9\u05dc\u05d9\u05dc\u05d9 \u05d7\u05d6\u05e7 \u05d1\u05d9\u05df $x$ \u05dc-$y$", "correct": True},
        {"id": "c", "text_en": "As $x$ increases by 1, $y$ decreases by 0.9", "text_he": "\u05db\u05d0\u05e9\u05e8 $x$ \u05e2\u05d5\u05dc\u05d4 \u05d1-1, $y$ \u05d9\u05d5\u05e8\u05d3 \u05d1-0.9", "correct": False},
        {"id": "d", "text_en": "$R^2 = -0.81$ and the fit is poor", "text_he": "$R^2 = -0.81$ \u05d5\u05d4\u05d4\u05ea\u05d0\u05de\u05d4 \u05d2\u05e8\u05d5\u05e2\u05d4", "correct": False}
      ],
      "explanation_en": "$r = -0.9$ means a strong negative linear association: as $x$ tends to increase, $y$ tends to decrease. Option (c) confuses $r$ with the slope $b$ (they are proportional but not equal). Option (d) is wrong because $R^2 = r^2 = 0.81 > 0$.",
      "explanation_he": "$r = -0.9$ \u05de\u05e9\u05de\u05e2\u05d5 \u05e7\u05e9\u05e8 \u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05e9\u05dc\u05d9\u05dc\u05d9 \u05d7\u05d6\u05e7. \u05d0\u05e4\u05e9\u05e8\u05d5\u05ea (ג) \u05de\u05d1\u05dc\u05d1\u05dc\u05ea $r$ \u05e2\u05dd $b$. \u05d0\u05e4\u05e9\u05e8\u05d5\u05ea (ד) \u05e9\u05d2\u05d5\u05d9\u05d9\u05ea \u05db\u05d9 $R^2 = 0.81 > 0$."
    },
    {
      "id": "q5",
      "type": "mcq",
      "body_en": "The data covers ages 20\u201350. Using the fitted line to predict for age 80 is problematic because:",
      "body_he": "\u05d4\u05e0\u05ea\u05d5\u05e0\u05d9\u05dd \u05de\u05db\u05e1\u05d9\u05dd \u05d2\u05d9\u05dc 20\u201350. \u05e9\u05d9\u05de\u05d5\u05e9 \u05d1\u05d9\u05e9\u05e8 \u05d4\u05de\u05d5\u05ea\u05d0\u05dd \u05dc\u05d7\u05d9\u05d6\u05d5\u05d9 \u05e2\u05d1\u05d5\u05e8 \u05d2\u05d9\u05dc 80 \u05d1\u05e2\u05d9\u05d9\u05ea\u05d9 \u05db\u05d9\u05d5\u05d5\u05df \u05e9:",
      "options": [
        {"id": "a", "text_en": "The OLS formulas are only valid for small datasets", "text_he": "\u05e0\u05d5\u05e1\u05d7\u05d0\u05d5\u05ea OLS \u05ea\u05e7\u05e4\u05d5\u05ea \u05e8\u05e7 \u05dc\u05e2\u05d1\u05d5\u05e8 \u05de\u05d3\u05d2\u05de\u05d9\u05dd \u05e7\u05d8\u05e0\u05d9\u05dd", "correct": False},
        {"id": "b", "text_en": "The linear relationship found in the range 20\u201350 may not hold at age 80 (extrapolation risk)", "text_he": "\u05d4\u05e7\u05e9\u05e8 \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05e9\u05e0\u05de\u05e6\u05d0 \u05d1\u05ea\u05d7\u05d5\u05dd 20\u201350 \u05e2\u05e9\u05d5\u05d9 \u05dc\u05d0 \u05dc\u05d4\u05ea\u05e7\u05d9\u05d9\u05dd \u05d1\u05d2\u05d9\u05dc 80 (\u05e1\u05db\u05e0\u05ea \u05d0\u05e7\u05e1\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4)", "correct": True},
        {"id": "c", "text_en": "Age 80 is not in the dataset, so there is no residual", "text_he": "\u05d2\u05d9\u05dc 80 \u05d0\u05d9\u05e0\u05d5 \u05d1\u05de\u05d3\u05d2\u05dd, \u05dc\u05db\u05df \u05d0\u05d9\u05df \u05e9\u05d0\u05e8\u05d9\u05ea", "correct": False},
        {"id": "d", "text_en": "The correlation coefficient is undefined outside the data range", "text_he": "\u05de\u05e7\u05d3\u05dd \u05d4\u05de\u05ea\u05d0\u05dd \u05d0\u05d9\u05e0\u05d5 \u05de\u05d5\u05d2\u05d3\u05e8 \u05de\u05d7\u05d5\u05e5 \u05dc\u05ea\u05d7\u05d5\u05dd", "correct": False}
      ],
      "explanation_en": "Extrapolation means predicting outside the range of observed data. The linear relationship seen in [20, 50] may break down, accelerate, or reverse at age 80. OLS gives no warning about this \u2014 it blindly extrapolates the line.",
      "explanation_he": "\u05d0\u05e7\u05e1\u05d8\u05e8\u05e4\u05d5\u05dc\u05e6\u05d9\u05d4 \u05d4\u05d9\u05d0 \u05e0\u05d1\u05d5\u05d0\u05d4 \u05de\u05d7\u05d5\u05e5 \u05dc\u05ea\u05d7\u05d5\u05dd \u05d4\u05e0\u05e6\u05e4\u05d4. \u05d4\u05e7\u05e9\u05e8 \u05d4\u05dc\u05d9\u05e0\u05d0\u05e8\u05d9 \u05d1-[20, 50] \u05e2\u05e9\u05d5\u05d9 \u05dc\u05d4\u05d9\u05e9\u05d1\u05e8 \u05d0\u05d5 \u05dc\u05d4\u05d9\u05e4\u05da \u05d1\u05d2\u05d9\u05dc 80."
    }
  ]
}

path = os.path.join(BASE, lesson["id"] + ".json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
print(f"Saved {lesson['id']}")
