/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _SQUIGGLES_CONSTRAINTS_HPP_
#define _SQUIGGLES_CONSTRAINTS_HPP_

#include <cmath>
#include <string>

namespace squiggles {
struct Constraints {
  /**
   * Defines the motion constraints for a path.
   *
   * @param imax_vel The maximum allowable velocity for the robot in meters per
   *                 second.
   * @param imax_accel The maximum allowable acceleration for the robot in
   *                   meters per second per second.
   * @param imax_jerk The maximum allowable jerk for the robot in meters per
   *                  second per second per second (m/s^3).
   * @param imax_curvature The maximum allowable change in heading in radians
   *                       per second. This is not set to the numeric limits by
   *                       default as that will allow for wild paths.
   * @param imin_accel The minimum allowable acceleration for the robot in
   *                   meters per second per second.
   */
  Constraints(double imax_vel,
              double imax_accel = std::numeric_limits<double>::max(),
              double imax_jerk = std::numeric_limits<double>::max(),
              double imax_curvature = 1000,
              double imin_accel = std::nan(""))
    : max_vel(imax_vel),
      max_accel(imax_accel),
      max_jerk(imax_jerk),
      max_curvature(imax_curvature) {
    if (imax_accel == std::numeric_limits<double>::max()) {
      min_accel = std::numeric_limits<double>::lowest();
    } else {
      min_accel = std::isnan(imin_accel) ? -imax_accel : imin_accel;
    }
  }

  /**
   * Serializes the Constraints data for debugging.
   *
   * @return The Constraints data.
   */
  std::string to_string() const {
    return "Constraints: {max_vel: " + std::to_string(max_vel) +
           ", max_accel: " + std::to_string(max_accel) +
           ", max_jerk: " + std::to_string(max_jerk) +
           ", min_accel: " + std::to_string(min_accel) + "}";
  }

  double max_vel;
  double max_accel;
  double max_jerk;
  double min_accel;
  double max_curvature;
};
} // namespace squiggles
#endif
