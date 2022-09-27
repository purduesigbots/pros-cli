/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/controller/chassisController.hpp"
#include "okapi/api/control/async/asyncPosIntegratedController.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"

namespace okapi {
class ChassisControllerIntegrated : public ChassisController {
  public:
  /**
   * ChassisController using the V5 motor's integrated control. Puts the motors into encoder count
   * units. Throws a `std::invalid_argument` exception if the gear ratio is zero. The initial
   * model's max velocity will be propagated to the controllers.
   *
   * @param itimeUtil The TimeUtil.
   * @param imodel The ChassisModel used to read from sensors/write to motors.
   * @param ileftController The controller used for the left side motors.
   * @param irightController The controller used for the right side motors.
   * @param igearset The internal gearset and external ratio used on the drive motors.
   * @param iscales The ChassisScales.
   * @param ilogger The logger this instance will log to.
   */
  ChassisControllerIntegrated(
    const TimeUtil &itimeUtil,
    std::shared_ptr<ChassisModel> imodel,
    std::unique_ptr<AsyncPosIntegratedController> ileftController,
    std::unique_ptr<AsyncPosIntegratedController> irightController,
    const AbstractMotor::GearsetRatioPair &igearset = AbstractMotor::gearset::green,
    const ChassisScales &iscales = ChassisScales({1, 1}, imev5GreenTPR),
    std::shared_ptr<Logger> ilogger = Logger::getDefaultLogger());

  /**
   * Drives the robot straight for a distance (using closed-loop control).
   *
   * ```cpp
   * // Drive forward 6 inches
   * chassis->moveDistance(6_in);
   *
   * // Drive backward 0.2 meters
   * chassis->moveDistance(-0.2_m);
   * ```
   *
   * @param itarget distance to travel
   */
  void moveDistance(QLength itarget) override;

  /**
   * Drives the robot straight for a distance (using closed-loop control).
   *
   * ```cpp
   * // Drive forward by spinning the motors 400 degrees
   * chassis->moveRaw(400);
   * ```
   *
   * @param itarget distance to travel in motor degrees
   */
  void moveRaw(double itarget) override;

  /**
   * Sets the target distance for the robot to drive straight (using closed-loop control).
   *
   * @param itarget distance to travel
   */
  void moveDistanceAsync(QLength itarget) override;

  /**
   * Sets the target distance for the robot to drive straight (using closed-loop control).
   *
   * @param itarget distance to travel in motor degrees
   */
  void moveRawAsync(double itarget) override;

  /**
   * Turns the robot clockwise in place (using closed-loop control).
   *
   * ```cpp
   * // Turn 90 degrees clockwise
   * chassis->turnAngle(90_deg);
   * ```
   *
   * @param idegTarget angle to turn for
   */
  void turnAngle(QAngle idegTarget) override;

  /**
   * Turns the robot clockwise in place (using closed-loop control).
   *
   * ```cpp
   * // Turn clockwise by spinning the motors 200 degrees
   * chassis->turnRaw(200);
   * ```
   *
   * @param idegTarget angle to turn for in motor degrees
   */
  void turnRaw(double idegTarget) override;

  /**
   * Sets the target angle for the robot to turn clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for
   */
  void turnAngleAsync(QAngle idegTarget) override;

  /**
   * Sets the target angle for the robot to turn clockwise in place (using closed-loop control).
   *
   * @param idegTarget angle to turn for in motor degrees
   */
  void turnRawAsync(double idegTarget) override;

  /**
   * Sets whether turns should be mirrored.
   *
   * @param ishouldMirror whether turns should be mirrored
   */
  void setTurnsMirrored(bool ishouldMirror) override;

  /**
   * Checks whether the internal controllers are currently settled.
   *
   * @return Whether this ChassisController is settled.
   */
  bool isSettled() override;

  /**
   * Delays until the currently executing movement completes.
   */
  void waitUntilSettled() override;

  /**
   * Interrupts the current movement to stop the robot.
   */
  void stop() override;

  /**
   * Get the ChassisScales.
   */
  ChassisScales getChassisScales() const override;

  /**
   * Get the GearsetRatioPair.
   */
  AbstractMotor::GearsetRatioPair getGearsetRatioPair() const override;

  /**
   * @return The internal ChassisModel.
   */
  std::shared_ptr<ChassisModel> getModel() override;

  /**
   * @return The internal ChassisModel.
   */
  ChassisModel &model() override;

  /**
   * Sets a new maximum velocity in RPM [0-600].
   *
   * @param imaxVelocity The new maximum velocity.
   */
  void setMaxVelocity(double imaxVelocity) override;

  /**
   * @return The maximum velocity in RPM [0-600].
   */
  double getMaxVelocity() const override;

  protected:
  std::shared_ptr<Logger> logger;
  bool normalTurns{true};
  std::shared_ptr<ChassisModel> chassisModel;
  TimeUtil timeUtil;
  std::unique_ptr<AsyncPosIntegratedController> leftController;
  std::unique_ptr<AsyncPosIntegratedController> rightController;
  int lastTarget;
  ChassisScales scales;
  AbstractMotor::GearsetRatioPair gearsetRatioPair;
};
} // namespace okapi
