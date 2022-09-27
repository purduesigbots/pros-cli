/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/controller/chassisController.hpp"
#include "okapi/api/control/iterative/iterativePosPidController.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <atomic>
#include <memory>
#include <tuple>

namespace okapi {
class ChassisControllerPID : public ChassisController {
  public:
  /**
   * ChassisController using PID control. Puts the motors into encoder count units. Throws a
   * `std::invalid_argument` exception if the gear ratio is zero.
   *
   * @param itimeUtil The TimeUtil.
   * @param imodel The ChassisModel used to read from sensors/write to motors.
   * @param idistanceController The PID controller that controls chassis distance for driving
   * straight.
   * @param iturnController The PID controller that controls chassis angle for turning.
   * @param iangleController The PID controller that controls chassis angle for driving straight.
   * @param igearset The internal gearset and external ratio used on the drive motors.
   * @param iscales The ChassisScales.
   * @param ilogger The logger this instance will log to.
   */
  ChassisControllerPID(
    TimeUtil itimeUtil,
    std::shared_ptr<ChassisModel> imodel,
    std::unique_ptr<IterativePosPIDController> idistanceController,
    std::unique_ptr<IterativePosPIDController> iturnController,
    std::unique_ptr<IterativePosPIDController> iangleController,
    const AbstractMotor::GearsetRatioPair &igearset = AbstractMotor::gearset::green,
    const ChassisScales &iscales = ChassisScales({1, 1}, imev5GreenTPR),
    std::shared_ptr<Logger> ilogger = Logger::getDefaultLogger());

  ChassisControllerPID(const ChassisControllerPID &) = delete;
  ChassisControllerPID(ChassisControllerPID &&other) = delete;
  ChassisControllerPID &operator=(const ChassisControllerPID &other) = delete;
  ChassisControllerPID &operator=(ChassisControllerPID &&other) = delete;

  ~ChassisControllerPID() override;

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
   * Gets the ChassisScales.
   */
  ChassisScales getChassisScales() const override;

  /**
   * Gets the GearsetRatioPair.
   */
  AbstractMotor::GearsetRatioPair getGearsetRatioPair() const override;

  /**
   * Sets the velocity mode flag. When the controller is in velocity mode, the control loop will
   * set motor velocities. When the controller is in voltage mode (`ivelocityMode = false`), the
   * control loop will set motor voltages. Additionally, when the controller is in voltage mode,
   * it will not obey maximum velocity limits.
   *
   * @param ivelocityMode Whether the controller should be in velocity or voltage mode.
   */
  void setVelocityMode(bool ivelocityMode);

  /**
   * Sets the gains for all controllers.
   *
   * @param idistanceGains The distance controller gains.
   * @param iturnGains The turn controller gains.
   * @param iangleGains The angle controller gains.
   */
  void setGains(const IterativePosPIDController::Gains &idistanceGains,
                const IterativePosPIDController::Gains &iturnGains,
                const IterativePosPIDController::Gains &iangleGains);

  /**
   * Gets the current controller gains.
   *
   * @return The current controller gains in the order: distance, turn, angle.
   */
  std::tuple<IterativePosPIDController::Gains,
             IterativePosPIDController::Gains,
             IterativePosPIDController::Gains>
  getGains() const;

  /**
   * Starts the internal thread. This method is called by the ChassisControllerBuilder when making a
   * new instance of this class.
   */
  void startThread();

  /**
   * Returns the underlying thread handle.
   *
   * @return The underlying thread handle.
   */
  CrossplatformThread *getThread() const;

  /**
   * Interrupts the current movement to stop the robot.
   */
  void stop() override;

  /**
   * Sets a new maximum velocity in RPM [0-600]. In voltage mode, the max velocity is ignored and a
   * max voltage should be set on the underlying ChassisModel instead.
   *
   * @param imaxVelocity The new maximum velocity.
   */
  void setMaxVelocity(double imaxVelocity) override;

  /**
   * @return The maximum velocity in RPM [0-600].
   */
  double getMaxVelocity() const override;

  /**
   * @return The internal ChassisModel.
   */
  std::shared_ptr<ChassisModel> getModel() override;

  /**
   * @return The internal ChassisModel.
   */
  ChassisModel &model() override;

  protected:
  std::shared_ptr<Logger> logger;
  bool normalTurns{true};
  std::shared_ptr<ChassisModel> chassisModel;
  TimeUtil timeUtil;
  std::unique_ptr<IterativePosPIDController> distancePid;
  std::unique_ptr<IterativePosPIDController> turnPid;
  std::unique_ptr<IterativePosPIDController> anglePid;
  ChassisScales scales;
  AbstractMotor::GearsetRatioPair gearsetRatioPair;
  bool velocityMode{true};
  std::atomic_bool doneLooping{true};
  std::atomic_bool doneLoopingSeen{true};
  std::atomic_bool newMovement{false};
  std::atomic_bool dtorCalled{false};
  QTime threadSleepTime{10_ms};

  static void trampoline(void *context);
  void loop();

  /**
   * Wait for the distance setup (distancePid and anglePid) to settle.
   *
   * @return true if done settling; false if settling should be tried again
   */
  bool waitForDistanceSettled();

  /**
   * Wait for the angle setup (anglePid) to settle.
   *
   * @return true if done settling; false if settling should be tried again
   */
  bool waitForAngleSettled();

  /**
   * Stops all the controllers and the ChassisModel.
   */
  void stopAfterSettled();

  typedef enum { distance, angle, none } modeType;
  modeType mode{none};

  CrossplatformThread *task{nullptr};
};
} // namespace okapi
