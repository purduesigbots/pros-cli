/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/RQuantityName.hpp"
#include <string>

namespace okapi {
struct OdomState {
  QLength x{0_m};
  QLength y{0_m};
  QAngle theta{0_deg};

  /**
   * Get a string for the current odometry state (optionally with the specified units).
   *
   * Examples:
   *   - `OdomState::str(1_m, 1_deg)`: The default (no arguments specified).
   *   - `OdomState::str(1_tile, 1_radian)`: distance tiles and angle radians.
   *
   * Throws std::domain_error if the units passed are undefined.
   *
   * @param idistanceUnit The units you want your distance to be in. This must be an exact, predefined QLength (such as foot, meter, inch, tile etc.).
   * @param iangleUnit The units you want your angle to be in. This must be an exact, predefined QAngle (degree or radian).
   * @return A string representing the state.
   */
  std::string str(QLength idistanceUnit, QAngle iangleUnit) const;

  /**
   * Get a string for the current odometry state (optionally with the specified units).
   *
   * Examples:
   *   - `OdomState::str(1_m, "_m", 1_deg, "_deg")`: The default (no arguments specified), prints in meters and degrees.
   *   - `OdomState::str(1_in, "_in", 1_deg, "_deg")` or `OdomState::str(1_in, "\"", 1_deg, "°")`: to print values in inches and degrees with different suffixes.
   *   - `OdomState::str(6_tile / 100, "%", 360_deg / 100, "%")` to get the distance values in % of the vex field, and angle values in % of a full rotation.
   *
   * @param idistanceUnit The units you want your distance to be in. The x or y position will be output in multiples of this length.
   * @param distUnitName The suffix you as your distance unit.
   * @param iangleUnit The units you want your angle to be in. The angle will be output in multiples of this unit.
   * @param angleUnitName The suffix you want as your angle unit.
   * @return A string representing the state.
   */
  std::string str(QLength idistanceUnit = meter,
                  std::string distUnitName = "_m",
                  QAngle iangleUnit = degree,
                  std::string angleUnitName = "_deg") const;

  bool operator==(const OdomState &rhs) const;

  bool operator!=(const OdomState &rhs) const;
};
} // namespace okapi
