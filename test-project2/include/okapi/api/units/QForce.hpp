/*
 * This code is a modified version of Benjamin Jurke's work in 2015. You can read his blog post
 * here:
 * https://benjaminjurke.com/content/articles/2015/compile-time-numerical-unit-dimension-checking/
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/units/QAcceleration.hpp"
#include "okapi/api/units/QMass.hpp"
#include "okapi/api/units/RQuantity.hpp"

namespace okapi {
QUANTITY_TYPE(1, 1, -2, 0, QForce)

constexpr QForce newton = (kg * meter) / (second * second);
constexpr QForce poundforce = pound * G;
constexpr QForce kilopond = kg * G;

inline namespace literals {
constexpr QForce operator"" _n(long double x) {
  return QForce(x);
}
constexpr QForce operator"" _n(unsigned long long int x) {
  return QForce(static_cast<double>(x));
}
constexpr QForce operator"" _lbf(long double x) {
  return static_cast<double>(x) * poundforce;
}
constexpr QForce operator"" _lbf(unsigned long long int x) {
  return static_cast<double>(x) * poundforce;
}
constexpr QForce operator"" _kp(long double x) {
  return static_cast<double>(x) * kilopond;
}
constexpr QForce operator"" _kp(unsigned long long int x) {
  return static_cast<double>(x) * kilopond;
}
} // namespace literals
} // namespace okapi
