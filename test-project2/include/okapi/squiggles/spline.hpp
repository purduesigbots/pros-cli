/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _SQUIGGLES_SPLINE_HPP_
#define _SQUIGGLES_SPLINE_HPP_

#include <initializer_list>
#include <memory>
#include <vector>

#include "constraints.hpp"
#include "geometry/controlvector.hpp"
#include "geometry/profilepoint.hpp"
#include "math/quinticpolynomial.hpp"
#include "physicalmodel/passthroughmodel.hpp"
#include "physicalmodel/physicalmodel.hpp"

namespace squiggles {
class SplineGenerator {
  public:
  /**
   * Generates curves that match the given motion constraints.
   *
   * @param iconstraints The maximum allowable values for the robot's motion.
   * @param imodel The robot's physical characteristics and constraints
   * @param idt The difference in time in seconds between each state for the
   *            generated paths.
   */
  SplineGenerator(Constraints iconstraints,
                  std::shared_ptr<PhysicalModel> imodel =
                    std::make_shared<PassthroughModel>(),
                  double idt = 0.1);

  /**
   * Creates a motion profiled path between the given waypoints.
   *
   * @param iwaypoints The list of poses that the robot should reach along the
   *                   path.
   * @param fast If true, the path optimization process will stop as soon as the
   *             constraints are met. If false, the optimizer will find the
   *             smoothest possible path between the points.
   *
   * @return A series of robot states defining a path between the poses.
   */
  std::vector<ProfilePoint> generate(std::vector<Pose> iwaypoints,
                                     bool fast = false);
  std::vector<ProfilePoint> generate(std::initializer_list<Pose> iwaypoints,
                                     bool fast = false);

  /**
   * Creates a motion profiled path between the given waypoints.
   *
   * @param iwaypoints The list of vectors that the robot should reach along the
   *                   path.
   *
   * @return A series of robot states defining a path between the vectors.
   */
  std::vector<ProfilePoint> generate(std::vector<ControlVector> iwaypoints);
  std::vector<ProfilePoint>
  generate(std::initializer_list<ControlVector> iwaypoints);

  protected:
  /**
   * The maximum allowable values for the robot's motion.
   */
  Constraints constraints;

  /**
   * Defines the physical structure of the robot and translates the linear
   * kinematics to wheel velocities.
   */
  std::shared_ptr<PhysicalModel> model;

  /**
   * The time difference between each value in the generated path.
   */
  double dt;

  /**
   * The minimum and maximum durations for a path to take. A larger range allows
   * for longer possible paths at the expense of a longer path generation time.
   */
  const int T_MIN = 2;
  const int T_MAX = 15;
  const int MAX_GRAD_DESCENT_ITERATIONS = 10;

  /**
   * This is factor is used to create a "dummy velocity" in the initial path
   * generation step one or both of the preferred start or end velocities is
   * zero. The velocity will be replaced with the preferred start/end velocity
   * in parameterization but a nonzero velocity is needed for the spline
   * calculation.
   *
   * This was 1.2 in the WPILib example but that large of a value seems to
   * create wild paths, 0.12 worked better in testing with VEX-sized paths.
   */
  public:
  const double K_DEFAULT_VEL = 1.0;

  /**
   * The output of the initial, "naive" generation step. We discard the
   * derivative values to replace them with values from a motion profile.
   */

  struct GeneratedPoint {
    GeneratedPoint(Pose ipose, double icurvature = 0.0)
      : pose(ipose), curvature(icurvature) {}

    std::string to_string() const {
      return "GeneratedPoint: {" + pose.to_string() +
             ", curvature: " + std::to_string(curvature) + "}";
    }

    Pose pose;
    double curvature;
  };

  /**
   * An intermediate value used in the "naive" generation step. Contains the
   * final GeneratedPoint value that will be returned as well as the spline's
   * derivative values to perform the initial check against the constraints.
   */
  struct GeneratedVector {
    GeneratedVector(GeneratedPoint ipoint,
                    double ivel,
                    double iaccel,
                    double ijerk)
      : point(ipoint), vel(ivel), accel(iaccel), jerk(ijerk) {}

    GeneratedPoint point;
    double vel;
    double accel;
    double jerk;

    std::string to_string() const {
      return "GeneratedVector: {" + point.to_string() +
             ", vel: " + std::to_string(vel) +
             ", accel: " + std::to_string(accel) +
             ", jerk: " + std::to_string(jerk) + "}";
    }
  };

  std::vector<GeneratedVector> gen_single_raw_path(ControlVector start,
                                                   ControlVector end,
                                                   int duration,
                                                   double start_vel,
                                                   double end_vel);
  /**
   * Runs a Gradient Descent algorithm to minimize the linear acceleration,
   * linear jerk, and curvature for the generated path.
   *
   * This is used when there is not a start/end velocity specified for a given
   * path.
   */
  std::vector<GeneratedPoint>
  gradient_descent(ControlVector& start, ControlVector& end, bool fast);

  /**
   * An intermediate value used in the parameterization step. Adds the
   * constrained values from the motion profile to the output from the "naive"
   * generation step.
   */
  struct ConstrainedState {
    ConstrainedState(Pose ipose,
                     double icurvature,
                     double idistance,
                     double imax_vel,
                     double imin_accel,
                     double imax_accel)
      : pose(ipose),
        curvature(icurvature),
        distance(idistance),
        max_vel(imax_vel),
        min_accel(imin_accel),
        max_accel(imax_accel) {}

    ConstrainedState() = default;

    Pose pose = Pose();
    double curvature = 0;
    double distance = 0;
    double max_vel = 0;
    double min_accel = 0;
    double max_accel = 0;

    std::string to_string() const {
      return "ConstrainedState: {x: " + std::to_string(pose.x) +
             ", y: " + std::to_string(pose.y) +
             ", yaw: " + std::to_string(pose.yaw) +
             ", k: " + std::to_string(curvature) +
             ", dist: " + std::to_string(distance) +
             ", v: " + std::to_string(max_vel) +
             ", min_a: " + std::to_string(min_accel) +
             ", max_a: " + std::to_string(max_accel) + "}";
    }
  };

  /**
   * The actual function called by the "generate" functions.
   *
   * @param start An iterator pointing to the first ControlVector in the path
   * @param end An iterator pointting to the last ControlVector in the path
   *
   * @return The points from each path concatenated together
   */
  template <class Iter>
  std::vector<ProfilePoint> _generate(Iter start, Iter end, bool fast);

  public:
  /**
   * Performs the "naive" generation step.
   *
   * This step calculates the spline polynomials that fit within the
   * SplineGenerator's acceleration and jerk constraints and returns the points
   * that form the curve.
   */
  std::vector<GeneratedPoint>
  gen_raw_path(ControlVector& start, ControlVector& end, bool fast);

  /**
   * Imposes a linear motion profile on the raw path.
   *
   * This step creates the velocity and acceleration values to command the robot
   * at each point along the curve.
   */
  std::vector<ProfilePoint>
  parameterize(const ControlVector start,
               const ControlVector end,
               const std::vector<GeneratedPoint>& raw_path,
               const double preferred_start_vel,
               const double preferred_end_vel,
               const double start_time);

  /**
   * Finds the new timestamps for each point along the curve based on the motion
   * profile.
   */
  std::vector<ProfilePoint>
  integrate_constrained_states(std::vector<ConstrainedState> constrainedStates);

  /**
   * Finds the ProfilePoint on the profiled curve for the given timestamp.
   *
   * This with interpolate between points on the curve if a point with an exact
   * matching timestamp is not found.
   */
  ProfilePoint get_point_at_time(const ControlVector start,
                                 const ControlVector end,
                                 std::vector<ProfilePoint> points,
                                 double t);

  /**
   * Linearly interpolates between points along the profiled curve.
   */
  ProfilePoint lerp_point(QuinticPolynomial x_qp,
                          QuinticPolynomial y_qp,
                          ProfilePoint start,
                          ProfilePoint end,
                          double i);

  /**
   * Returns the spline curve for the given control vectors and path duration.
   */
  QuinticPolynomial get_x_spline(const ControlVector start,
                                 const ControlVector end,
                                 const double duration);
  QuinticPolynomial get_y_spline(const ControlVector start,
                                 const ControlVector end,
                                 const double duration);

  /**
   * Applies the general constraints and model constraints to the given state.
   */
  void enforce_accel_lims(ConstrainedState* state);

  /**
   * Imposes the motion profile constraints on a segment of the path from the
   * perspective of iterating forwards through the path.
   */
  void forward_pass(ConstrainedState* predecessor, ConstrainedState* successor);

  /**
   * Imposes the motion profile constraints on a segment of the path from the
   * perspective of iterating backwards through the path.
   */
  void backward_pass(ConstrainedState* predecessor,
                     ConstrainedState* successor);

  /**
   * Calculates the final velocity for a path segment.
   */
  double vf(double vi, double a, double ds);

  /**
   * Calculates the initial acceleration needed to match the segments'
   * velocities.
   */
  double ai(double vf, double vi, double s);

  /**
   * Values that are closer to each other than this value are considered equal.
   */
  static constexpr double K_EPSILON = 1e-5;
};
} // namespace squiggles

#endif
