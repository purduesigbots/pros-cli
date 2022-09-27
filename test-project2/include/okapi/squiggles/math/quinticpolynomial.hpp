/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _MATH_QUINTIC_POLYNOMIAL_HPP_
#define _MATH_QUINTIC_POLYNOMIAL_HPP_

#include <string>

namespace squiggles {
class QuinticPolynomial {
  public:
  /**
   * Defines the polynomial function for a spline in one dimension.
   *
   * @param s_p The starting position of the curve in meters.
   * @param s_v The starting velocity of the curve in meters per second.
   * @param s_a The starting acceleration of the curve in meters per second per
   *            second.
   * @param g_p The goal or ending position of the curve in meters.
   * @param g_v The goal or ending velocity of the curve in meters per second.
   * @param g_a The goal or ending acceleration of the curve in meters per
   *            second per second.
   * @param t The desired duration for the curve in seconds.
   */
  QuinticPolynomial(double s_p,
                    double s_v,
                    double s_a,
                    double g_p,
                    double g_v,
                    double g_a,
                    double t);

  /**
   * Calculates the values of the polynomial and its derivatives at the given
   * time stamp.
   */
  double calc_point(double t);
  double calc_first_derivative(double t);
  double calc_second_derivative(double t);
  double calc_third_derivative(double t);

  /**
   * Serializes the Quintic Polynomial data for debugging.
   *
   * @return The Quintic Polynomial data.
   */
  std::string to_string() const {
    return "QuinticPolynomial: {0: " + std::to_string(a0) +
           " 1: " + std::to_string(a1) + " 2: " + std::to_string(a2) +
           " 3: " + std::to_string(a3) + " 4: " + std::to_string(a4) +
           " 5: " + std::to_string(a5) + "}";
  }

  protected:
  /**
   * The coefficients for each term of the polynomial.
   */
  double a0, a1, a2, a3, a4, a5;
};
} // namespace squiggles

#endif