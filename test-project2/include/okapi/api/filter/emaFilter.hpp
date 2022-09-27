/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/filter.hpp"

namespace okapi {
class EmaFilter : public Filter {
  public:
  /**
   * Exponential moving average filter.
   *
   * @param ialpha alpha gain
   */
  explicit EmaFilter(double ialpha);

  /**
   * Filters a value, like a sensor reading.
   *
   * @param reading new measurement
   * @return filtered result
   */
  double filter(double ireading) override;

  /**
   * Returns the previous output from filter.
   *
   * @return the previous output from filter
   */
  double getOutput() const override;

  /**
   * Set filter gains.
   *
   * @param ialpha alpha gain
   */
  virtual void setGains(double ialpha);

  protected:
  double alpha;
  double output = 0;
  double lastOutput = 0;
};
} // namespace okapi
