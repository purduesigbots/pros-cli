/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _GEOMETRY_PROFILE_POINT_HPP_
#define _GEOMETRY_PROFILE_POINT_HPP_

#include <iostream>
#include <string>
#include <vector>

#include "controlvector.hpp"
#include "math/utils.hpp"

namespace squiggles {
struct ProfilePoint {
  /**
   * Defines a state along a motion profiled path.
   *
   * @param ivector The pose and associated dynamics at this state in the path.
   * @param iwheel_velocities The component of the robot's velocity provided by
   *                          each wheel in meters per second.
   * @param icurvature The degree to which the curve deviates from a straight
   *                   line at this point in 1 / meters.
   * @param itime The timestamp for this state relative to the start of the
   *              path in seconds.
   */
  ProfilePoint(ControlVector ivector,
               std::vector<double> iwheel_velocities,
               double icurvature,
               double itime)
    : vector(ivector),
      wheel_velocities(iwheel_velocities),
      curvature(icurvature),
      time(itime) {}

  ProfilePoint() = default;

  /**
   * Serializes the Profile Point data for debugging.
   *
   * @return The Profile Point data.
   */
  std::string to_string() const {
    std::string wheels = "{";
    for (auto& w : wheel_velocities) {
      wheels += std::to_string(w);
      wheels += ", ";
    }
    wheels += "}";
    return "ProfilePoint: {" + vector.to_string() + ", wheels: " + wheels +
           ", k: " + std::to_string(curvature) +
           ", t: " + std::to_string(time) + "}";
  }

  std::string to_csv() const {
    std::string wheels = "";
    for (auto& w : wheel_velocities) {
      wheels += ",";
      wheels += std::to_string(w);
    }
    return vector.to_csv() + "," + std::to_string(curvature) + "," +
           std::to_string(time) + wheels;
  }

  bool operator==(const ProfilePoint& other) const {
    for (std::size_t i = 0; i < wheel_velocities.size(); ++i) {
      if (!nearly_equal(wheel_velocities[i], other.wheel_velocities[i])) {
        return false;
      }
    }
    return vector == other.vector && nearly_equal(curvature, other.curvature) &&
           nearly_equal(time, other.time);
  }

  friend std::ostream& operator<<(std::ostream& os, const ProfilePoint& p) {
    return os << "ProfilePoint(ControlVector(Pose(" +
                   std::to_string(p.vector.pose.x) + "," +
                   std::to_string(p.vector.pose.y) + "," +
                   std::to_string(p.vector.pose.yaw) + ")," +
                   std::to_string(p.vector.vel) + "," +
                   std::to_string(p.vector.accel) + "," +
                   std::to_string(p.vector.jerk) + "),{" +
                   std::to_string(p.wheel_velocities[0]) + "," +
                   std::to_string(p.wheel_velocities[1]) + "}," +
                   std::to_string(p.curvature) + "," + std::to_string(p.time) +
                   "),";
    // return os << p.to_string();
  }

  ControlVector vector;
  std::vector<double> wheel_velocities;
  double curvature;
  double time;
};
} // namespace squiggles

#endif