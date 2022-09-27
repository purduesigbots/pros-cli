/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

namespace okapi {
/**
 * The mode for the OdomState calculated by Odometry.
 */
enum class StateMode {
  FRAME_TRANSFORMATION, ///< +x is forward, +y is right, 0 degrees is along +x
  CARTESIAN             ///< +x is right, +y is forward, 0 degrees is along +y
};

} // namespace okapi
