/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/coreProsAPI.hpp"
#include "okapi/api/units/QFrequency.hpp"
#include "okapi/api/units/QTime.hpp"

namespace okapi {
class AbstractRate {
  public:
  virtual ~AbstractRate();

  /**
   * Delay the current task such that it runs at the given frequency. The first delay will run for
   * 1000/(ihz). Subsequent delays will adjust according to the previous runtime of the task.
   *
   * @param ihz the frequency
   */
  virtual void delay(QFrequency ihz) = 0;

  /**
   * Delay the current task until itime has passed. This method can be used by periodic tasks to
   * ensure a consistent execution frequency.
   *
   * @param itime the time period
   */
  virtual void delayUntil(QTime itime) = 0;

  /**
   * Delay the current task until ims milliseconds have passed. This method can be used by
   * periodic tasks to ensure a consistent execution frequency.
   *
   * @param ims the time period
   */
  virtual void delayUntil(uint32_t ims) = 0;
};
} // namespace okapi
