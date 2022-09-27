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

#include "okapi/api/units/RQuantity.hpp"

namespace okapi {
QUANTITY_TYPE(0, 0, -1, 0, QFrequency)

constexpr QFrequency Hz(1.0);

inline namespace literals {
constexpr QFrequency operator"" _Hz(long double x) {
  return QFrequency(x);
}
constexpr QFrequency operator"" _Hz(unsigned long long int x) {
  return QFrequency(static_cast<long double>(x));
}
} // namespace literals
} // namespace okapi
