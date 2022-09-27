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
QUANTITY_TYPE(0, 0, 1, 0, QTime)

constexpr QTime second(1.0); // SI base unit
constexpr QTime millisecond = second / 1000;
constexpr QTime minute = 60 * second;
constexpr QTime hour = 60 * minute;
constexpr QTime day = 24 * hour;

inline namespace literals {
constexpr QTime operator"" _s(long double x) {
  return QTime(x);
}
constexpr QTime operator"" _ms(long double x) {
  return static_cast<double>(x) * millisecond;
}
constexpr QTime operator"" _min(long double x) {
  return static_cast<double>(x) * minute;
}
constexpr QTime operator"" _h(long double x) {
  return static_cast<double>(x) * hour;
}
constexpr QTime operator"" _day(long double x) {
  return static_cast<double>(x) * day;
}
constexpr QTime operator"" _s(unsigned long long int x) {
  return QTime(static_cast<double>(x));
}
constexpr QTime operator"" _ms(unsigned long long int x) {
  return static_cast<double>(x) * millisecond;
}
constexpr QTime operator"" _min(unsigned long long int x) {
  return static_cast<double>(x) * minute;
}
constexpr QTime operator"" _h(unsigned long long int x) {
  return static_cast<double>(x) * hour;
}
constexpr QTime operator"" _day(unsigned long long int x) {
  return static_cast<double>(x) * day;
}
} // namespace literals
} // namespace okapi
