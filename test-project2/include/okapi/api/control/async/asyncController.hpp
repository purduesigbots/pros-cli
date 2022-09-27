/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/closedLoopController.hpp"

namespace okapi {
/**
 * Closed-loop controller that steps on its own in another thread and automatically writes to the
 * output.
 */
template <typename Input, typename Output>
class AsyncController : public ClosedLoopController<Input, Output> {
  public:
  /**
   * Blocks the current task until the controller has settled. Determining what settling means is
   * implementation-dependent.
   */
  virtual void waitUntilSettled() = 0;
};
} // namespace okapi
