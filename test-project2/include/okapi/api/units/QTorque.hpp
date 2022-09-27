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

#include "okapi/api/units/QForce.hpp"
#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/RQuantity.hpp"

namespace okapi {
QUANTITY_TYPE(1, 2, -2, 0, QTorque)

constexpr QTorque newtonMeter = newton * meter;
constexpr QTorque footPound = 1.355817948 * newtonMeter;
constexpr QTorque inchPound = 0.083333333 * footPound;

inline namespace literals {
constexpr QTorque operator"" _nM(long double x) {
  return QTorque(x);
}
constexpr QTorque operator"" _nM(unsigned long long int x) {
  return QTorque(static_cast<double>(x));
}
constexpr QTorque operator"" _inLb(long double x) {
  return static_cast<double>(x) * inchPound;
}
constexpr QTorque operator"" _inLb(unsigned long long int x) {
  return static_cast<double>(x) * inchPound;
}
constexpr QTorque operator"" _ftLb(long double x) {
  return static_cast<double>(x) * footPound;
}
constexpr QTorque operator"" _ftLb(unsigned long long int x) {
  return static_cast<double>(x) * footPound;
}
} // namespace literals
} // namespace okapi
