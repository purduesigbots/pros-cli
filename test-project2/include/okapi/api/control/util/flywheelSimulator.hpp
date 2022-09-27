/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include <functional>

namespace okapi {
class FlywheelSimulator {
  public:
  /**
   * A simulator for an inverted pendulum. The center of mass of the system changes as the link
   * rotates (by default, you can set a new torque function with setExternalTorqueFunction()).
   */
  explicit FlywheelSimulator(double imass = 0.01,
                             double ilinkLen = 1,
                             double imuStatic = 0.1,
                             double imuDynamic = 0.9,
                             double itimestep = 0.01);

  virtual ~FlywheelSimulator();

  /**
   * Step the simulation by the timestep.
   *
   * @return the current angle
   */
  double step();

  /**
   * Step the simulation by the timestep.
   *
   * @param itorque new input torque
   * @return the current angle
   */
  double step(double itorque);

  /**
   * Sets the torque function used to calculate the torque due to external forces. This torque gets
   * summed with the input torque.
   *
   * For example, the default torque function has the torque due to gravity vary as the link swings:
   * [](double angle, double mass, double linkLength) {
   *   return (linkLength * std::cos(angle)) * (mass * -1 * gravity);
   * }
   *
   * @param itorqueFunc the torque function. The return value is the torque due to external forces
   */
  void setExternalTorqueFunction(
    std::function<double(double angle, double mass, double linkLength)> itorqueFunc);

  /**
   * Sets the input torque. The input will be bounded by the max torque.
   *
   * @param itorque new input torque
   */
  void setTorque(double itorque);

  /**
   * Sets the max torque. The input torque cannot exceed this maximum torque.
   *
   * @param imaxTorque new maximum torque
   */
  void setMaxTorque(double imaxTorque);

  /**
   * Sets the current angle.
   *
   * @param iangle new angle
   **/
  void setAngle(double iangle);

  /**
   * Sets the mass (kg).
   *
   * @param imass new mass
   */
  void setMass(double imass);

  /**
   * Sets the link length (m).
   *
   * @param ilinkLen new link length
   */
  void setLinkLength(double ilinkLen);

  /**
   * Sets the static friction (N*m).
   *
   * @param imuStatic new static friction
   */
  void setStaticFriction(double imuStatic);

  /**
   * Sets the dynamic friction (N*m).
   *
   * @param imuDynamic new dynamic friction
   */
  void setDynamicFriction(double imuDynamic);

  /**
   * Sets the timestep (sec).
   *
   * @param itimestep new timestep
   */
  void setTimestep(double itimestep);

  /**
   * Returns the current angle (angle in rad).
   *
   * @return the current angle
   */
  double getAngle() const;

  /**
   * Returns the current omgea (angular velocity in rad / sec).
   *
   * @return the current omega
   */
  double getOmega() const;

  /**
   * Returns the current acceleration (angular acceleration in rad / sec^2).
   *
   * @return the current acceleration
   */
  double getAcceleration() const;

  /**
   * Returns the maximum torque input.
   *
   * @return the max torque input
   */
  double getMaxTorque() const;

  protected:
  double inputTorque = 0;    // N*m
  double maxTorque = 0.5649; // N*m
  double angle = 0;          // rad
  double omega = 0;          // rad / sec
  double accel = 0;          // rad / sec^2
  double mass;               // kg
  double linkLen;            // m
  double muStatic;           // N*m
  double muDynamic;          // N*m
  double timestep;           // sec
  double I = 0;              // moment of inertia
  std::function<double(double, double, double)> torqueFunc;

  const double minTimestep = 0.000001; // 1 us

  virtual double stepImpl();
};
} // namespace okapi
