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

#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/RQuantity.hpp"

namespace okapi {
QUANTITY_TYPE(0, 2, 0, 0, QArea)

constexpr QArea kilometer2 = kilometer * kilometer;
constexpr QArea meter2 = meter * meter;
constexpr QArea decimeter2 = decimeter * decimeter;
constexpr QArea centimeter2 = centimeter * centimeter;
constexpr QArea millimeter2 = millimeter * millimeter;
constexpr QArea inch2 = inch * inch;
constexpr QArea foot2 = foot * foot;
constexpr QArea mile2 = mile * mile;
} // namespace okapi
