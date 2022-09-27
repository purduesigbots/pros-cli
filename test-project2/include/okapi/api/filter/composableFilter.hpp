/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/filter.hpp"
#include <functional>
#include <initializer_list>
#include <memory>
#include <vector>

namespace okapi {
class ComposableFilter : public Filter {
  public:
  /**
   * A composable filter is a filter that consists of other filters. The input signal is passed
   * through each filter in sequence. The final output of this filter is the output of the last
   * filter.
   *
   * @param ilist The filters to use in sequence.
   */
  ComposableFilter(const std::initializer_list<std::shared_ptr<Filter>> &ilist);

  /**
   * Filters a value.
   *
   * @param ireading A new measurement.
   * @return The filtered result.
   */
  double filter(double ireading) override;

  /**
   * @return The previous output from filter.
   */
  double getOutput() const override;

  /**
   * Adds a filter to the end of the sequence.
   *
   * @param ifilter The filter to add.
   */
  virtual void addFilter(std::shared_ptr<Filter> ifilter);

  protected:
  std::vector<std::shared_ptr<Filter>> filters;
  double output = 0;
};
} // namespace okapi
