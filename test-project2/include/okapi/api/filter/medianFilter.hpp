/*
 * Uses the median filter algorithm from N. Wirth’s book, implementation by N. Devillard.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/filter.hpp"
#include <algorithm>
#include <array>
#include <cstddef>

namespace okapi {
/**
 * A filter which returns the median value of list of values.
 *
 * @tparam n number of taps in the filter
 */
template <std::size_t n> class MedianFilter : public Filter {
  public:
  MedianFilter() : middleIndex((((n)&1) ? ((n) / 2) : (((n) / 2) - 1))) {
  }

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

    output = kth_smallset();
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
  const size_t middleIndex;

  /**
   * Algorithm from N. Wirth’s book, implementation by N. Devillard.
   */
  double kth_smallset() {
    std::array<double, n> dataCopy = data;
    size_t j, l, m;
    l = 0;
    m = n - 1;

    while (l < m) {
      double x = dataCopy[middleIndex];
      size_t i = l;
      j = m;
      do {
        while (dataCopy[i] < x) {
          i++;
        }
        while (x < dataCopy[j]) {
          j--;
        }
        if (i <= j) {
          const double t = dataCopy[i];
          dataCopy[i] = dataCopy[j];
          dataCopy[j] = t;
          i++;
          j--;
        }
      } while (i <= j);
      if (j < middleIndex)
        l = i;
      if (middleIndex < i)
        m = j;
    }

    return dataCopy[middleIndex];
  }
};
} // namespace okapi
