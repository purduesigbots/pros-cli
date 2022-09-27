/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QLength.hpp"

namespace okapi {
struct PathfinderPoint {
  QLength x;    // X coordinate relative to the start of the movement
  QLength y;    // Y coordinate relative to the start of the movement
  QAngle theta; // Exit angle relative to the start of the movement
};

struct PathfinderLimits {
  double maxVel;   // Maximum robot velocity in m/s
  double maxAccel; // Maximum robot acceleration in m/s/s
  double maxJerk;  // Maximum robot jerk in m/s/s/s
};
} // namespace okapi
