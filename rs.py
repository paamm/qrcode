from __future__ import annotations
from typing import List, Optional


# Basic GF operations

def gf_multiplication(a: int, b: int) -> int:
    return 0 if a == 0 or b == 0 else gf_exp[(gf_log[a] + gf_log[b]) % 255]


def gf_add(a: int, b: int) -> int:
    return a ^ b


def gf_sub(a: int, b: int) -> int:
    return a ^ b


def gf_polynomial_division(a, b) -> List[int]:
    # Synthetic division for GF
    dividend = a.get_inversed_terms() + [0] * (len(b.terms) - 1)
    divisor = b.get_inversed_terms()

    result = dividend.copy()
    for i in range(len(dividend) - len(divisor) + 1):
        term = result[i]
        if term != 0:  # log(0) doesn't exist
            for j in range(1, len(divisor)):  # Never use first term of the divisor when doing synthetic div
                if divisor[j] != 0:
                    result[i + j] ^= gf_multiplication(term, divisor[j])  # GF operation for += term * divisor[j]

    return result[-(len(divisor) - 1):]


class RSPolynomial:
    def __init__(self, terms: List[int] = None):
        if terms is None:
            terms = []
        self.terms = terms

    def __str__(self):
        result = ""
        for i in range(len(self.terms)):
            term = self.terms[i]
            if term != 0:
                if i == 0:
                    result = str(term)
                elif i == 1:
                    result = "{:s}x + ".format(str(term) if term > 1 else "") + result
                else:
                    result = "{:s}x^{:d} + ".format(str(term) if term > 1 else "", i) + result
        return result.rstrip(" + ")

    def set_term(self, term: int, index: int):
        new_terms = self.terms
        if len(self.terms) < index:
            # pad terms to make room for new term
            new_terms += [0] * (index - len(self.terms) + 1)

        new_terms[index] = term
        self.terms = new_terms

    def get_inversed_terms(self) -> List[int]:
        return self.terms[::-1]

    def scalar_multiplication(self, scalar: int) -> RSPolynomial:
        return RSPolynomial([gf_multiplication(i, scalar) for i in self.terms])

    def polynomial_multiplication(self, other: RSPolynomial) -> RSPolynomial:
        new_terms = [0] * (len(self.terms) + len(other.terms) - 1)
        for i in range(len(self.terms)):
            for j in range(len(other.terms)):
                new_terms[i + j] ^= gf_multiplication(self.terms[i], other.terms[j])
        return RSPolynomial(new_terms)


generator_polynomials: List[Optional[RSPolynomial]] = [None] * 69  # Biggest amount of ECC needed ever is 68


def rs_generator_poly(n: int) -> RSPolynomial:
    if generator_polynomials[n]:
        return generator_polynomials[n]

    if n == 1:
        poly = RSPolynomial([gf_exp[0], 1])
        generator_polynomials[n] = poly
        return poly
    else:
        poly = RSPolynomial([gf_exp[n - 1], 1])
        poly = poly.polynomial_multiplication(rs_generator_poly(n - 1))
        generator_polynomials[n] = poly
        return poly


def message_poly(codewords: List[str]):
    length = len(codewords)
    msg_poly = RSPolynomial()
    for i in range(length):
        # ax^n-1 + bx^n-2 + ... + (n-1)x^0
        msg_poly.set_term(int(codewords[i], 2), length - i - 1)  # Converting binary codewords to decimal
    return msg_poly


gf_exp = [0] * 256
gf_log = [0] * 256


def fill_tables():
    exp = 1
    for i in range(256):
        gf_exp[i] = exp
        gf_log[exp] = i

        exp *= 2
        exp = exp ^ 285 if exp > 255 else exp
    gf_log[1] = 0  # manually setting log(1) to 0 because it'd show 255 otherwise


fill_tables()
