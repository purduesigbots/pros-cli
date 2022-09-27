/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _GEOMETRY_CONTROL_VECTOR_HPP_
#define _GEOMETRY_CONTROL_VECTOR_HPP_

#include <cmath>
#include <string>

#include "pose.hpp"

namespace squiggles {
class ControlVector {
  public:
  /**
   * A vector used to specify a state along a hermite spline.
   *
   * @param ipose The 2D position and heading.
   * @param ivel The velocity component of the vector.
   * @param iaccel The acceleration component of the vector.
   * @param ijerk The jerk component of the vector.
   */
  ControlVector(Pose ipose,
                double ivel = std::nan(""),
                double iaccel = 0.0,
                double ijerk = 0.0)
    : pose(ipose), vel(ivel), accel(iaccel), jerk(ijerk) {}

  ControlVector() = default;

  /**
   * Serializes the Control Vector data for debugging.
   *
   * @return The Control Vector data.
   */
  std::string to_string() const {
    return "ControlVector: {" + pose.to_string() +
           ", v: " + std::to_string(vel) + ", a: " + std::to_string(accel) +
           ", j: " + std::to_string(jerk) + "}";
  }

  std::string to_csv() const {
    return pose.to_csv() + "," + std::to_string(vel) + "," +
           std::to_string(accel) + "," + std::to_string(jerk);
  }

  bool operator==(const ControlVector& other) const {
    return pose == other.pose && nearly_equal(vel, other.vel) &&
           nearly_equal(accel, other.accel) && nearly_equal(jerk, other.jerk);
  }

  Pose pose;
  double vel;
  double accel;
  double jerk;
};
} // namespace squiggles

#endif