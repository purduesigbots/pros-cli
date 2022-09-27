/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/util/abstractTimer.hpp"

namespace okapi {
class Timer : public AbstractTimer {
  public:
  Timer();

  /**
   * Returns the current time in units of QTime.
   *
   * @return the current time
   */
  QTime millis() const override;
};
} // namespace okapi
