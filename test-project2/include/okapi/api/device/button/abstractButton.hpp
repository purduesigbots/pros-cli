/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerInput.hpp"

namespace okapi {
class AbstractButton : public ControllerInput<bool> {
  public:
  virtual ~AbstractButton();

  /**
   * Return whether the button is currently pressed.
   **/
  virtual bool isPressed() = 0;

  /**
   * Return whether the state of the button changed since the last time this method was
   * called.
   **/
  virtual bool changed() = 0;

  /**
   * Return whether the state of the button changed to being pressed since the last time this method
   * was called.
   **/
  virtual bool changedToPressed() = 0;

  /**
   * Return whether the state of the button to being not pressed changed since the last time this
   * method was called.
   **/
  virtual bool changedToReleased() = 0;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current sensor value. This is the same as the output of the pressed() method.
   */
  virtual bool controllerGet() override;
};
} // namespace okapi
