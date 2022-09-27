/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/device/button/buttonBase.hpp"
#include "okapi/impl/device/controllerUtil.hpp"

namespace okapi {
class ControllerButton : public ButtonBase {
  public:
  /**
   * A button on a Controller.
   *
   * @param ibtn The button id.
   * @param iinverted Whether the button is inverted (default pressed instead of default released).
   */
  ControllerButton(ControllerDigital ibtn, bool iinverted = false);

  /**
   * A button on a Controller.
   *
   * @param icontroller The Controller the button is on.
   * @param ibtn The button id.
   * @param iinverted Whether the button is inverted (default pressed instead of default released).
   */
  ControllerButton(ControllerId icontroller, ControllerDigital ibtn, bool iinverted = false);

  protected:
  pros::controller_id_e_t id;
  pros::controller_digital_e_t btn;

  virtual bool currentlyPressed() override;
};
} // namespace okapi
