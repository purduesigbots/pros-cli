/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _PHYSICAL_MODEL_TANK_MODEL_HPP_
#define _PHYSICAL_MODEL_TANK_MODEL_HPP_

#include <tuple>
#include <vector>

#include "physicalmodel/physicalmodel.hpp"

namespace squiggles {
class TankModel : public PhysicalModel {
  public:
  /**
   * Defines a model of a tank drive or differential drive robot.
   *
   * @param itrack_width The distance between the the wheels on each side of the
   *                     robot in meters.
   * @param ilinear_constraints The maximum values for the robot's movement.
   */
  TankModel(double itrack_width, Constraints ilinear_constraints);

  Constraints
  constraints(const Pose pose, double curvature, double vel) override;

  std::vector<double> linear_to_wheel_vels(double lin_vel,
                                           double curvature) override;

  std::string to_string() const override;

  private:
  double vel_constraint(const Pose pose, double curvature, double vel);
  std::tuple<double, double>
  accel_constraint(const Pose pose, double curvature, double vel) const;

  double track_width;
  Constraints linear_constraints;
};
} // namespace squiggles

#endif