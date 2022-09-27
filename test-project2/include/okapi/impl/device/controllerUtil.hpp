/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"

namespace okapi {
/**
 * Which controller role this has.
 */
enum class ControllerId {
  master = 0, ///< master
  partner = 1 ///< partner
};

/**
 * The analog sticks.
 */
enum class ControllerAnalog {
  leftX = 0,  ///< leftX
  leftY = 1,  ///< leftY
  rightX = 2, ///< rightX
  rightY = 3  ///< rightY
};

/**
 * Various buttons.
 */
enum class ControllerDigital {
  L1 = 6,     ///< L1
  L2 = 7,     ///< L2
  R1 = 8,     ///< R1
  R2 = 9,     ///< R2
  up = 10,    ///< up
  down = 11,  ///< down
  left = 12,  ///< left
  right = 13, ///< right
  X = 14,     ///< X
  B = 15,     ///< B
  Y = 16,     ///< Y
  A = 17      ///< A
};

class ControllerUtil {
  public:
  /**
   * Maps an `id` to the PROS enum equivalent.
   */
  static pros::controller_id_e_t idToProsEnum(ControllerId in);

  /**
   * Maps an `analog` to the PROS enum equivalent.
   */
  static pros::controller_analog_e_t analogToProsEnum(ControllerAnalog in);

  /**
   * Maps a `digital` to the PROS enum equivalent.
   */
  static pros::controller_digital_e_t digitalToProsEnum(ControllerDigital in);
};
} // namespace okapi
