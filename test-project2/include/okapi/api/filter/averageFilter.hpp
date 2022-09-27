/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/filter.hpp"
#include <array>
#include <cstddef>

namespace okapi {
/**
 * A filter which returns the average of a list of values.
 *
 * @tparam n number of taps in the filter
 */
template <std::size_t n> class AverageFilter : public Filter {
  public:
  /**
   * Averaging filter.
   */
  AverageFilter() = default;

  /**
   * Filters a value, like a sensor reading.
   *
   * @param ireading new measurement
   * @return filtered result
   */
  double filter(const double ireading) override {
    data[index++] = ireading;
    if (index >= n) {
      index = 0;
    }

    output = 0.0;
    for (size_t i = 0; i < n; i++)
      output += data[i];
    output /= (double)n;

    return output;
  }

  /**
   * Returns the previous output from filter.
   *
   * @return the previous output from filter
   */
  double getOutput() const override {
    return output;
  }

  protected:
  std::array<double, n> data{0};
  std::size_t index = 0;
  double output = 0;
};
} // namespace okapi
