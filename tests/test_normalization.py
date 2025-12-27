import unittest

from preprocessing import normalize_equation

class TestNormalization(unittest.TestCase):
    def test_equation_normalization(self):
        # 1. Inline Equations within Sentences (Standard & Alternative)
        # Requirement: Convert all inline mathematics to a unified format (e.g., $...$)[cite: 29].
        self.assertEqual(normalize_equation(r"The variable \(x\) is used."), "The variable $x$ is used.")
        self.assertEqual(normalize_equation(r"The variable $y$ is used."), "The variable $y$ is used.")
        self.assertEqual(normalize_equation(r"Let \begin{math}a+b\end{math} be real."), "Let $a+b$ be real.")
        
        # 2. Multiple Inline Equations in One Sentence
        # Ensures sequential replacement does not break prose.
        multi_inline = r"If \( \alpha < \beta \), then \begin{math} \beta > \alpha \end{math} is true."
        expected_inline = r"If $ \alpha < \beta $, then $ \beta > \alpha $ is true."
        self.assertEqual(normalize_equation(multi_inline), expected_inline)

        # 3. Block Equations: Standard Delimiters
        # Requirement: Convert all block mathematics to a unified format (e.g., \begin{equation}...\end{equation})[cite: 29].
        self.assertEqual(normalize_equation(r"\[ E=mc^2 \]"), r"\begin{equation} E=mc^2 \end{equation}")
        self.assertEqual(normalize_equation(r"$$a^2 + b^2 = c^2$$"), r"\begin{equation}a^2 + b^2 = c^2\end{equation}")

        # 4. Block Equations: Multi-line and Starred Environments
        # All logical block math must converge to the same unified environment[cite: 29].
        self.assertEqual(normalize_equation(r"\begin{align}y=mx+b\end{align}"), r"\begin{equation}y=mx+b\end{equation}")
        self.assertEqual(normalize_equation(r"\begin{align*}z=f(x,y)\end{align*}"), r"\begin{equation}z=f(x,y)\end{equation}")

        # 5. Mixed Content: Inline and Block in Sequential Order
        # This tests the transition from sentence leaf nodes to block formula leaf nodes.
        mixed_input = r"Given \( \sigma \), we calculate: \[ \sigma^2 \]"
        mixed_expected = r"Given $ \sigma $, we calculate: \begin{equation} \sigma^2 \end{equation}"
        self.assertEqual(normalize_equation(mixed_input), mixed_expected)

        # 6. Preservation of Internal Math Formatting
        # Formatting like \mathbf should remain, but outer delimiters must change[cite: 28, 29].
        self.assertEqual(normalize_equation(r"Vector \( \mathbf{v} \) is here."), r"Vector $ \mathbf{v} $ is here.")

        # 7. Empty Math Delimiters
        # Edge case: empty equations should still be normalized
        self.assertEqual(normalize_equation(r"\(\)"), r"$$")
        self.assertEqual(normalize_equation(r"\[\]"), r"\begin{equation}\end{equation}")
        self.assertEqual(normalize_equation(r"$$$$"), r"\begin{equation}\end{equation}")

        # 8. Nested Delimiters (if supported)
        # Test equations with nested braces or complex structure
        self.assertEqual(normalize_equation(r"\( \frac{a}{b} \)"), r"$ \frac{a}{b} $")
        self.assertEqual(normalize_equation(r"\[ \int_{0}^{\infty} e^{-x} dx \]"), r"\begin{equation} \int_{0}^{\infty} e^{-x} dx \end{equation}")

        # 9. Whitespace Handling
        # Equations with various whitespace patterns
        self.assertEqual(normalize_equation(r"\(  x  \)"), r"$  x  $")
        self.assertEqual(normalize_equation(r"\[   E=mc^2   \]"), r"\begin{equation}   E=mc^2   \end{equation}")
        self.assertEqual(normalize_equation(r"$$  \alpha  $$"), r"\begin{equation}  \alpha  \end{equation}")

        # 10. Multiple Block Equations in Sequence
        # Ensure multiple block equations are all converted
        multi_block = r"\[ x = 1 \] and \[ y = 2 \]"
        expected_block = r"\begin{equation} x = 1 \end{equation} and \begin{equation} y = 2 \end{equation}"
        self.assertEqual(normalize_equation(multi_block), expected_block)

        # 11. Complex Mixed Document
        # Real-world scenario with multiple inline and block equations
        complex_input = r"Consider \( f(x) = x^2 \). The integral is \[ \int f(x) dx = \frac{x^3}{3} + C \]. Note that \begin{math}C\end{math} is constant."
        complex_expected = r"Consider $ f(x) = x^2 $. The integral is \begin{equation} \int f(x) dx = \frac{x^3}{3} + C \end{equation}. Note that $C$ is constant."
        self.assertEqual(normalize_equation(complex_input), complex_expected)

        # 12. Equations with Special Characters
        # Test equations containing LaTeX special characters
        self.assertEqual(normalize_equation(r"\( \alpha \wedge \beta \)"), r"$ \alpha \wedge \beta $")
        self.assertEqual(normalize_equation(r"\[ \sum_{i=1}^{n} x_i \]"), r"\begin{equation} \sum_{i=1}^{n} x_i \end{equation}")

        # 13. Text with Dollar Signs (Non-Math)
        # Edge case: literal dollar signs in text (if distinguishable)
        # This test depends on implementation - may need escaping
        self.assertEqual(normalize_equation(r"Price is \$5."), r"Price is \$5.")

        # 14. Already Normalized Content
        # Idempotency: normalizing already normalized content should not change it
        already_inline = r"The value $x$ is constant."
        self.assertEqual(normalize_equation(already_inline), already_inline)
        
        already_block = r"\begin{equation}E=mc^2\end{equation}"
        self.assertEqual(normalize_equation(already_block), already_block)

        # 15. Multiline Block Equations
        # Block equations spanning multiple lines
        multiline_input = r"\begin{align}x + y &= 10\\x - y &= 2\end{align}"
        multiline_expected = r"\begin{equation}x + y &= 10\\x - y &= 2\end{equation}"
        self.assertEqual(normalize_equation(multiline_input), multiline_expected)

        # 16. Inline Equations at Start and End of String
        # Edge case: equations at boundaries
        self.assertEqual(normalize_equation(r"\(x\) is a variable"), r"$x$ is a variable")
        self.assertEqual(normalize_equation(r"A variable is \(x\)"), r"A variable is $x$")
        self.assertEqual(normalize_equation(r"\(x\)"), r"$x$")

        # 17. Block Equations at Start and End of String
        self.assertEqual(normalize_equation(r"\[ x = 1 \] is true"), r"\begin{equation} x = 1 \end{equation} is true")
        self.assertEqual(normalize_equation(r"The equation is \[ x = 1 \]"), r"The equation is \begin{equation} x = 1 \end{equation}")

        # 18. Consecutive Inline Equations
        # Multiple inline equations with no text between them
        consecutive = r"Values \(a\)\(b\)\(c\) are used."
        expected_consecutive = r"Values $a$$b$$c$ are used."
        self.assertEqual(normalize_equation(consecutive), expected_consecutive)

        # 19. Complex Math with Subscripts and Superscripts
        self.assertEqual(normalize_equation(r"\( x_{i}^{2} + y_{j}^{2} \)"), r"$ x_{i}^{2} + y_{j}^{2} $")
        self.assertEqual(normalize_equation(r"\[ \lim_{n \to \infty} \frac{1}{n} = 0 \]"), r"\begin{equation} \lim_{n \to \infty} \frac{1}{n} = 0 \end{equation}")

        # 20. Equations with Line Breaks Inside
        # Block equations with internal newlines
        newline_input = r"\[ x = 1 + 2 + 3 \]"
        newline_expected = r"\begin{equation} x = 1 + 2 + 3 \end{equation}"
        self.assertEqual(normalize_equation(newline_input), newline_expected)

        # 21. Multiple Different Inline Formats in Same Text
        mixed_inline_formats = r"We have \(x\), $y$, and \begin{math}z\end{math}."
        expected_mixed = r"We have $x$, $y$, and $z$."
        self.assertEqual(normalize_equation(mixed_inline_formats), expected_mixed)

        # 22. Multiple Different Block Formats in Same Text
        mixed_block_formats = r"First: \[ a = b \] Second: $$c = d$$ Third: \begin{align}e = f\end{align}"
        expected_mixed_block = r"First: \begin{equation} a = b \end{equation} Second: \begin{equation}c = d\end{equation} Third: \begin{equation}e = f\end{equation}"
        self.assertEqual(normalize_equation(mixed_block_formats), expected_mixed_block)

        # 23. Edge Case: Text Only (No Equations)
        plain_text = "This is plain text with no equations."
        self.assertEqual(normalize_equation(plain_text), plain_text)

        # 24. Equations with Greek Letters and Symbols
        self.assertEqual(normalize_equation(r"\( \Delta \theta \approx \pi \)"), r"$ \Delta \theta \approx \pi $")
        self.assertEqual(normalize_equation(r"\[ \Omega = \{ 1, 2, 3 \} \]"), r"\begin{equation} \Omega = \{ 1, 2, 3 \} \end{equation}")

        # 25. Starred Equation Environment
        self.assertEqual(normalize_equation(r"\begin{equation*}F = ma\end{equation*}"), r"\begin{equation}F = ma\end{equation}")