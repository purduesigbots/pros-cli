/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

namespace okapi {
template <typename T> class ControllerOutput {
  public:
  /**
   * Writes the value of the controller output. This method might be automatically called in another
   * thread by the controller. The range of input values is expected to be `[-1, 1]`.
   *
   * @param ivalue the controller's output in the range `[-1, 1]`
   */
  virtual void controllerSet(T ivalue) = 0;
};
} // namespace okapi
