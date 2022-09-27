/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/coreProsAPI.hpp"

namespace okapi {
class RotarySensor : public ControllerInput<double> {
  public:
  virtual ~RotarySensor();

  /**
   * Get the current sensor value.
   *
   * @return the current sensor value, or `PROS_ERR` on a failure.
   */
  virtual double get() const = 0;
};
} // namespace okapi
