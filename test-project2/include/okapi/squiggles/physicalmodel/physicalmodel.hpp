/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _PHYSICAL_MODEL_PHYSICAL_MODEL_HPP_
#define _PHYSICAL_MODEL_PHYSICAL_MODEL_HPP_

#include "constraints.hpp"
#include "geometry/pose.hpp"

namespace squiggles {
class PhysicalModel {
  public:
  /**
   * Calculate a set of stricter constraints for the path at the given state
   * than the general constraints based on the robot's kinematics.
   *
   * @param pose The 2D pose for this state in the path.
   * @param curvature The change in heading at this state in the path in 1 /
   *                  meters.
   * @param vel The linear velocity at this state in the path in meters per
   * second.
   */
  virtual Constraints
  constraints(const Pose pose, double curvature, double vel) = 0;

  /**
   * Converts a linear velocity and desired curvature into the component for
   * each wheel of the robot.
   *
   * @param linear The linear velocity for the robot in meters per second.
   * @param curvature The change in heading for the robot in 1 / meters.
   */
  virtual std::vector<double> linear_to_wheel_vels(double linear,
                                                   double curvature) = 0;

  virtual std::string to_string() const = 0;
};
} // namespace squiggles

#endif
