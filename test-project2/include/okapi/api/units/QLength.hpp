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
QUANTITY_TYPE(0, 1, 0, 0, QLength)

constexpr QLength meter(1.0); // SI base unit
constexpr QLength decimeter = meter / 10;
constexpr QLength centimeter = meter / 100;
constexpr QLength millimeter = meter / 1000;
constexpr QLength kilometer = 1000 * meter;
constexpr QLength inch = 2.54 * centimeter;
constexpr QLength foot = 12 * inch;
constexpr QLength yard = 3 * foot;
constexpr QLength mile = 5280 * foot;
constexpr QLength tile = 24 * inch;

inline namespace literals {
constexpr QLength operator"" _mm(long double x) {
  return static_cast<double>(x) * millimeter;
}
constexpr QLength operator"" _cm(long double x) {
  return static_cast<double>(x) * centimeter;
}
constexpr QLength operator"" _m(long double x) {
  return static_cast<double>(x) * meter;
}
constexpr QLength operator"" _km(long double x) {
  return static_cast<double>(x) * kilometer;
}
constexpr QLength operator"" _mi(long double x) {
  return static_cast<double>(x) * mile;
}
constexpr QLength operator"" _yd(long double x) {
  return static_cast<double>(x) * yard;
}
constexpr QLength operator"" _ft(long double x) {
  return static_cast<double>(x) * foot;
}
constexpr QLength operator"" _in(long double x) {
  return static_cast<double>(x) * inch;
}
constexpr QLength operator"" _tile(long double x) {
  return static_cast<double>(x) * tile;
}
constexpr QLength operator"" _mm(unsigned long long int x) {
  return static_cast<double>(x) * millimeter;
}
constexpr QLength operator"" _cm(unsigned long long int x) {
  return static_cast<double>(x) * centimeter;
}
constexpr QLength operator"" _m(unsigned long long int x) {
  return static_cast<double>(x) * meter;
}
constexpr QLength operator"" _km(unsigned long long int x) {
  return static_cast<double>(x) * kilometer;
}
constexpr QLength operator"" _mi(unsigned long long int x) {
  return static_cast<double>(x) * mile;
}
constexpr QLength operator"" _yd(unsigned long long int x) {
  return static_cast<double>(x) * yard;
}
constexpr QLength operator"" _ft(unsigned long long int x) {
  return static_cast<double>(x) * foot;
}
constexpr QLength operator"" _in(unsigned long long int x) {
  return static_cast<double>(x) * inch;
}
constexpr QLength operator"" _tile(unsigned long long int x) {
  return static_cast<double>(x) * tile;
}
} // namespace literals
} // namespace okapi
