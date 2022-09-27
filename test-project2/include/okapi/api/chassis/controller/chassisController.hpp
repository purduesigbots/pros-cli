/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/controller/chassisScales.hpp"
#include "okapi/api/chassis/model/chassisModel.hpp"
#include "okapi/api/device/motor/abstractMotor.hpp"
#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QLength.hpp"
#include <memory>
#include <valarray>

namespace okapi {
class ChassisController {
  public:
  /**
   * A ChassisController adds a closed-loop layer on top of a ChassisModel. moveDistance and
   * turnAngle both use closed-loop control to move the robot. There are passthrough functions for
   * everything defined in ChassisModel.
   *
   * @param imodel underlying ChassisModel
   */
  explicit ChassisController() = default;

  virtual ~ChassisController() = default;

  /**
   * Drives the robot straight for a distance (using closed-loop control).
   *
   * @param itarget distance to travel
   */
  virtual void moveDistance(QLength itarget) = 0;

  /**
   * Drives the robot straight for a distance (using closed-loop control).
   *
   * @param itarget distance to travel in motor degrees
   */
  virtual void moveRaw(double itarget) = 0;

  /**
   * Sets the target distance for the robot to drive straight (using closed-loop control).
   *
   * @param itarget distance to travel
   */
  virtual void moveDistanceAsync(QLength itarget) = 0;

  /**
   * Sets the target distance for the robot to drive straight (using closed-loop control).
   *
   * @param itarget distance to travel in motor degrees
   */
  virtual void moveRawAsync(double itarget) = 0;

  /**
   * Turns the robot clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for
   */
  virtual void turnAngle(QAngle idegTarget) = 0;

  /**
   * Turns the robot clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for in motor degrees
   */
  virtual void turnRaw(double idegTarget) = 0;

  /**
   * Sets the target angle for the robot to turn clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for
   */
  virtual void turnAngleAsync(QAngle idegTarget) = 0;

  /**
   * Sets the target angle for the robot to turn clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for in motor degrees
   */
  virtual void turnRawAsync(double idegTarget) = 0;

  /**
   * Sets whether turns should be mirrored.
   *
   * @param ishouldMirror whether turns should be mirrored
   */
  virtual void setTurnsMirrored(bool ishouldMirror) = 0;

  /**
   * Checks whether the internal controllers are currently settled.
   *
   * @return Whether this ChassisController is settled.
   */
  virtual bool isSettled() = 0;

  /**
   * Delays until the currently executing movement completes.
   */
  virtual void waitUntilSettled() = 0;

  /**
   * Interrupts the current movement to stop the robot.
   */
  virtual void stop() = 0;

  /**
   * Sets a new maximum velocity in RPM [0-600].
   *
   * @param imaxVelocity The new maximum velocity.
   */
  virtual void setMaxVelocity(double imaxVelocity) = 0;

  /**
   * @return The maximum velocity in RPM [0-600].
   */
  virtual double getMaxVelocity() const = 0;

  /**
   * Get the ChassisScales.
   */
  virtual ChassisScales getChassisScales() const = 0;

  /**
   * Get the GearsetRatioPair.
   */
  virtual AbstractMotor::GearsetRatioPair getGearsetRatioPair() const = 0;

  /**
   * @return The internal ChassisModel.
   */
  virtual std::shared_ptr<ChassisModel> getModel() = 0;

  /**
   * @return The internal ChassisModel.
   */
  virtual ChassisModel &model() = 0;
};
} // namespace okapi
