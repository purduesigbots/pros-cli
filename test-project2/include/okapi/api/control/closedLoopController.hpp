/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/units/QTime.hpp"

namespace okapi {
/**
 * An abstract closed-loop controller.
 *
 * @tparam Input The target/input type.
 * @tparam Output The error/output type.
 */
template <typename Input, typename Output>
class ClosedLoopController : public ControllerOutput<Input> {
  public:
  virtual ~ClosedLoopController() = default;

  /**
   * Sets the target for the controller.
   *
   * @param itarget the new target
   */
  virtual void setTarget(Input itarget) = 0;

  /**
   * Gets the last set target, or the default target if none was set.
   *
   * @return the last target
   */
  virtual Input getTarget() = 0;

  /**
   * @return The most recent value of the process variable.
   */
  virtual Input getProcessValue() const = 0;

  /**
   * Returns the last error of the controller. Does not update when disabled.
   *
   * @return the last error
   */
  virtual Output getError() const = 0;

  /**
   * Returns whether the controller has settled at the target. Determining what settling means is
   * implementation-dependent.
   *
   * If the controller is disabled, this method must return `true`.
   *
   * @return whether the controller is settled
   */
  virtual bool isSettled() = 0;

  /**
   * Resets the controller's internal state so it is similar to when it was first initialized, while
   * keeping any user-configured information.
   */
  virtual void reset() = 0;

  /**
   * Changes whether the controller is off or on. Turning the controller on after it was off will
   * cause the controller to move to its last set target, unless it was reset in that time.
   */
  virtual void flipDisable() = 0;

  /**
   * Sets whether the controller is off or on. Turning the controller on after it was off will
   * cause the controller to move to its last set target, unless it was reset in that time.
   *
   * @param iisDisabled whether the controller is disabled
   */
  virtual void flipDisable(bool iisDisabled) = 0;

  /**
   * Returns whether the controller is currently disabled.
   *
   * @return whether the controller is currently disabled
   */
  virtual bool isDisabled() const = 0;
};
} // namespace okapi
