/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncController.hpp"
#include <memory>

namespace okapi {
template <typename Input, typename Output>
class AsyncPositionController : virtual public AsyncController<Input, Output> {
  public:
  /**
   * Sets the "absolute" zero position of the controller to its current position.
   */
  virtual void tarePosition() = 0;

  /**
   * Sets a new maximum velocity (typically motor RPM [0-600]). The interpretation of the units
   * of this velocity and whether it will be respected is implementation-dependent.
   *
   * @param imaxVelocity The new maximum velocity.
   */
  virtual void setMaxVelocity(std::int32_t imaxVelocity) = 0;
};
} // namespace okapi
