/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerInput.hpp"
#include <memory>

namespace okapi {
class OffsetableControllerInput : public ControllerInput<double> {
  public:
  /**
   * A ControllerInput which can be tared to change the zero position.
   *
   * @param iinput The ControllerInput to reference.
   */
  explicit OffsetableControllerInput(const std::shared_ptr<ControllerInput<double>> &iinput);

  virtual ~OffsetableControllerInput();

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current sensor value, or PROS_ERR on a failure.
   */
  double controllerGet() override;

  /**
   * Sets the "absolute" zero position of this controller input to its current position. This does
   * nothing if the underlying controller input returns PROS_ERR.
   */
  virtual void tarePosition();

  protected:
  std::shared_ptr<ControllerInput<double>> input;
  double offset{0};
};
} // namespace okapi
