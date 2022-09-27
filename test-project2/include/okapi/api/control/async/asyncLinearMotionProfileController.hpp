/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncPositionController.hpp"
#include "okapi/api/control/util/pathfinderUtil.hpp"
#include "okapi/api/device/motor/abstractMotor.hpp"
#include "okapi/api/units/QAngularSpeed.hpp"
#include "okapi/api/units/QSpeed.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <atomic>
#include <map>

#include "squiggles.hpp"

namespace okapi {
class AsyncLinearMotionProfileController : public AsyncPositionController<std::string, double> {
  public:
  /**
   * An Async Controller which generates and follows 1D motion profiles.
   *
   * @param itimeUtil The TimeUtil.
   * @param ilimits The default limits.
   * @param ioutput The output to write velocity targets to.
   * @param idiameter The effective diameter for whatever the motor spins.
   * @param ipair The gearset.
   * @param ilogger The logger this instance will log to.
   */
  AsyncLinearMotionProfileController(
    const TimeUtil &itimeUtil,
    const PathfinderLimits &ilimits,
    const std::shared_ptr<ControllerOutput<double>> &ioutput,
    const QLength &idiameter,
    const AbstractMotor::GearsetRatioPair &ipair,
    const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  AsyncLinearMotionProfileController(AsyncLinearMotionProfileController &&other) = delete;

  AsyncLinearMotionProfileController &
  operator=(AsyncLinearMotionProfileController &&other) = delete;

  ~AsyncLinearMotionProfileController() override;

  /**
   * Generates a path which intersects the given waypoints and saves it internally with a key of
   * pathId. Call `executePath()` with the same `pathId` to run it.
   *
   * If the waypoints form a path which is impossible to achieve, an instance of
   * `std::runtime_error` is thrown (and an error is logged) which describes the waypoints. If there
   * are no waypoints, no path is generated.
   *
   * @param iwaypoints The waypoints to hit on the path.
   * @param ipathId A unique identifier to save the path with.
   */
  void generatePath(std::initializer_list<QLength> iwaypoints, const std::string &ipathId);

  /**
   * Generates a path which intersects the given waypoints and saves it internally with a key of
   * pathId. Call `executePath()` with the same pathId to run it.
   *
   * If the waypoints form a path which is impossible to achieve, an instance of
   * `std::runtime_error` is thrown (and an error is logged) which describes the waypoints. If there
   * are no waypoints, no path is generated.
   *
   * @param iwaypoints The waypoints to hit on the path.
   * @param ipathId A unique identifier to save the path with.
   * @param ilimits The limits to use for this path only.
   */
  void generatePath(std::initializer_list<QLength> iwaypoints,
                    const std::string &ipathId,
                    const PathfinderLimits &ilimits);

  /**
   * Removes a path and frees the memory it used. This function returns `true` if the path was
   * either deleted or didn't exist in the first place. It returns `false` if the path could not be
   * removed because it is running.
   *
   * @param ipathId A unique identifier for the path, previously passed to generatePath()
   * @return `true` if the path no longer exists
   */
  bool removePath(const std::string &ipathId);

  /**
   * Gets the identifiers of all paths saved in this `AsyncMotionProfileController`.
   *
   * @return The identifiers of all paths
   */
  std::vector<std::string> getPaths();

  /**
   * Executes a path with the given ID. If there is no path matching the ID, the method will
   * return. Any targets set while a path is being followed will be ignored.
   *
   * @param ipathId A unique identifier for the path, previously passed to `generatePath()`.
   */
  void setTarget(std::string ipathId) override;

  /**
   * Executes a path with the given ID. If there is no path matching the ID, the method will
   * return. Any targets set while a path is being followed will be ignored.
   *
   * @param ipathId A unique identifier for the path, previously passed to `generatePath()`.
   * @param ibackwards Whether to follow the profile backwards.
   */
  void setTarget(std::string ipathId, bool ibackwards);

  /**
   * Writes the value of the controller output. This method might be automatically called in another
   * thread by the controller.
   *
   * This just calls `setTarget()`.
   */
  void controllerSet(std::string ivalue) override;

  /**
   * Gets the last set target, or the default target if none was set.
   *
   * @return the last target
   */
  std::string getTarget() override;

  /**
   * Gets the last set target, or the default target if none was set.
   *
   * @return the last target
   */
  virtual std::string getTarget() const;

  /**
   * This is overridden to return the current path.
   *
   * @return The most recent value of the process variable.
   */
  std::string getProcessValue() const override;

  /**
   * Blocks the current task until the controller has settled. This controller is settled when
   * it has finished following a path. If no path is being followed, it is settled.
   */
  void waitUntilSettled() override;

  /**
   * Generates a new path from the position (typically the current position) to the target and
   * blocks until the controller has settled. Does not save the path which was generated.
   *
   * @param iposition The starting position.
   * @param itarget The target position.
   * @param ibackwards Whether to follow the profile backwards.
   */
  void moveTo(const QLength &iposition, const QLength &itarget, bool ibackwards = false);

  /**
   * Generates a new path from the position (typically the current position) to the target and
   * blocks until the controller has settled. Does not save the path which was generated.
   *
   * @param iposition The starting position.
   * @param itarget The target position.
   * @param ilimits The limits to use for this path only.
   * @param ibackwards Whether to follow the profile backwards.
   */
  void moveTo(const QLength &iposition,
              const QLength &itarget,
              const PathfinderLimits &ilimits,
              bool ibackwards = false);

  /**
   * Returns the last error of the controller. Does not update when disabled. Returns zero if there
   * is no path currently being followed.
   *
   * @return the last error
   */
  double getError() const override;

  /**
   * Returns whether the controller has settled at the target. Determining what settling means is
   * implementation-dependent.
   *
   * If the controller is disabled, this method must return `true`.
   *
   * @return whether the controller is settled
   */
  bool isSettled() override;

  /**
   * Resets the controller's internal state so it is similar to when it was first initialized, while
   * keeping any user-configured information. This implementation also stops movement.
   */
  void reset() override;

  /**
   * Changes whether the controller is off or on. Turning the controller on after it was off will
   * NOT cause the controller to move to its last set target.
   */
  void flipDisable() override;

  /**
   * Sets whether the controller is off or on. Turning the controller on after it was off will
   * NOT cause the controller to move to its last set target, unless it was reset in that time.
   *
   * @param iisDisabled whether the controller is disabled
   */
  void flipDisable(bool iisDisabled) override;

  /**
   * Returns whether the controller is currently disabled.
   *
   * @return whether the controller is currently disabled
   */
  bool isDisabled() const override;

  /**
   * This implementation does nothing because the API always requires the starting position to be
   * specified.
   */
  void tarePosition() override;

  /**
   * This implementation does nothing because the maximum velocity is configured using
   * PathfinderLimits elsewhere.
   *
   * @param imaxVelocity Ignored.
   */
  void setMaxVelocity(std::int32_t imaxVelocity) override;

  /**
   * Starts the internal thread. This should not be called by normal users. This method is called
   * by the AsyncControllerFactory when making a new instance of this class.
   */
  void startThread();

  /**
   * Returns the underlying thread handle.
   *
   * @return The underlying thread handle.
   */
  CrossplatformThread *getThread() const;

  /**
   * Attempts to remove a path without stopping execution, then if that fails, disables the
   * controller and removes the path.
   *
   * @param ipathId The path ID that will be removed
   */
  void forceRemovePath(const std::string &ipathId);

  protected:
  std::shared_ptr<Logger> logger;
  std::map<std::string, std::vector<squiggles::ProfilePoint>> paths{};
  PathfinderLimits limits;
  std::shared_ptr<ControllerOutput<double>> output;
  QLength diameter;
  AbstractMotor::GearsetRatioPair pair;
  double currentProfilePosition{0};
  TimeUtil timeUtil;

  // This must be locked when accessing the current path
  CrossplatformMutex currentPathMutex;

  std::string currentPath{""};
  std::atomic_bool isRunning{false};
  std::atomic_int direction{1};
  std::atomic_bool disabled{false};
  std::atomic_bool dtorCalled{false};
  CrossplatformThread *task{nullptr};

  static void trampoline(void *context);
  void loop();

  /**
   * Follow the supplied path. Must follow the disabled lifecycle.
   */
  virtual void executeSinglePath(const std::vector<squiggles::ProfilePoint> &path,
                                 std::unique_ptr<AbstractRate> rate);

  /**
   * Converts linear "chassis" speed to rotational motor speed.
   *
   * @param linear "chassis" frame speed
   * @return motor frame speed
   */
  QAngularSpeed convertLinearToRotational(QSpeed linear) const;

  std::string getPathErrorMessage(const std::vector<PathfinderPoint> &points,
                                  const std::string &ipathId,
                                  int length);
};
} // namespace okapi
