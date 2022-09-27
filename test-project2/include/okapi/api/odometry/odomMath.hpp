/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/odometry/odomState.hpp"
#include "okapi/api/odometry/point.hpp"
#include "okapi/api/util/logging.hpp"
#include <tuple>

namespace okapi {
class OdomMath {
  public:
  /**
   * Computes the distance from the given Odometry state to the given point. The point and the
   * OdomState must be in `StateMode::FRAME_TRANSFORMATION`.
   *
   * @param ipoint The point.
   * @param istate The Odometry state.
   * @return The distance between the Odometry state and the point.
   */
  static QLength computeDistanceToPoint(const Point &ipoint, const OdomState &istate);

  /**
   * Computes the angle from the given Odometry state to the given point. The point and the
   * OdomState must be in `StateMode::FRAME_TRANSFORMATION`.
   *
   * @param ipoint The point.
   * @param istate The Odometry state.
   * @return The angle between the Odometry state and the point.
   */
  static QAngle computeAngleToPoint(const Point &ipoint, const OdomState &istate);

  /**
   * Computes the distance and angle from the given Odometry state to the given point. The point and
   * the OdomState must be in `StateMode::FRAME_TRANSFORMATION`.
   *
   * @param ipoint The point.
   * @param istate The Odometry state.
   * @return The distance and angle between the Odometry state and the point.
   */
  static std::pair<QLength, QAngle> computeDistanceAndAngleToPoint(const Point &ipoint,
                                                                   const OdomState &istate);

  /**
   * Constraints the angle to [0,360] degrees.
   *
   * @param angle The input angle.
   * @return The angle normalized to [0,360] degrees.
   */
  static QAngle constrainAngle360(const QAngle &angle);

  /**
   * Constraints the angle to [-180,180) degrees.
   *
   * @param angle The input angle.
   * @return The angle normalized to [-180,180) degrees.
   */
  static QAngle constrainAngle180(const QAngle &angle);

  private:
  OdomMath();
  ~OdomMath();

  /**
   * Computes the x and y diffs in meters between the points.
   *
   * @param ipoint The point.
   * @param istate The Odometry state.
   * @return The diffs in the order `{xDiff, yDiff}`.
   */
  static std::pair<double, double> computeDiffs(const Point &ipoint, const OdomState &istate);

  /**
   * Computes the distance between the points.
   *
   * @param xDiff The x-axis diff in meters.
   * @param yDiff The y-axis diff in meters.
   * @return The cartesian distance in meters.
   */
  static double computeDistance(double xDiff, double yDiff);

  /**
   * Compites the angle between the points.
   *
   * @param xDiff The x-axis diff in meters.
   * @param yDiff The y-axis diff in meters.
   * @param theta The current robot's theta in radians.
   * @return The angle in radians.
   */
  static double computeAngle(double xDiff, double yDiff, double theta);
};
} // namespace okapi
