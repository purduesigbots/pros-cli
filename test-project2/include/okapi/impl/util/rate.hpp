/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/util/abstractRate.hpp"

namespace okapi {
class Rate : public AbstractRate {
  public:
  Rate();

  /**
   * Delay the current task such that it runs at the given frequency. The first delay will run for
   * 1000/(ihz). Subsequent delays will adjust according to the previous runtime of the task.
   *
   * @param ihz the frequency
   */
  void delay(QFrequency ihz) override;

  /**
   * Delay the current task until itime has passed. This method can be used by periodic tasks to
   * ensure a consistent execution frequency.
   *
   * @param itime the time period
   */
  void delayUntil(QTime itime) override;

  /**
   * Delay the current task until ims milliseconds have passed. This method can be used by
   * periodic tasks to ensure a consistent execution frequency.
   *
   * @param ims the time period
   */
  void delayUntil(uint32_t ims) override;

  protected:
  std::uint32_t lastTime{0};
};
} // namespace okapi
