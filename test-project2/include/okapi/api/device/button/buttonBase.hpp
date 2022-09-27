/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/device/button/abstractButton.hpp"

namespace okapi {
class ButtonBase : public AbstractButton {
  public:
  /**
   * @param iinverted Whether the button is inverted (`true` meaning default pressed and `false`
   * meaning default not pressed).
   */
  explicit ButtonBase(bool iinverted = false);

  /**
   * Return whether the button is currently pressed.
   **/
  bool isPressed() override;

  /**
   * Return whether the state of the button changed since the last time this method was called.
   **/
  bool changed() override;

  /**
   * Return whether the state of the button changed to pressed since the last time this method was
   *called.
   **/
  bool changedToPressed() override;

  /**
   * Return whether the state of the button to not pressed since the last time this method was
   *called.
   **/
  bool changedToReleased() override;

  protected:
  bool inverted{false};
  bool wasPressedLast_c{false};
  bool wasPressedLast_ctp{false};
  bool wasPressedLast_ctr{false};

  virtual bool currentlyPressed() = 0;

  private:
  bool changedImpl(bool &prevState);
};
} // namespace okapi
