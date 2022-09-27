/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/controller/chassisController.hpp"
#include "okapi/api/chassis/model/skidSteerModel.hpp"
#include "okapi/api/coreProsAPI.hpp"
#include "okapi/api/odometry/odometry.hpp"
#include "okapi/api/odometry/point.hpp"
#include "okapi/api/units/QSpeed.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <atomic>
#include <memory>
#include <valarray>

namespace okapi {
class OdomChassisController : public ChassisController {
  public:
  /**
   * Odometry based chassis controller. Starts task at the default for odometry when constructed,
   * which calls `Odometry::step` every `10ms`. The default StateMode is
   * `StateMode::FRAME_TRANSFORMATION`.
   *
   * Moves the robot around in the odom frame. Instead of telling the robot to drive forward or
   * turn some amount, you instead tell it to drive to a specific point on the field or turn to
   * a specific angle relative to its starting position.
   *
   * @param itimeUtil The TimeUtil.
   * @param iodometry The Odometry instance to run in a new task.
   * @param imode The new default StateMode used to interpret target points and query the Odometry
   * state.
   * @param imoveThreshold minimum length movement (smaller movements will be skipped)
   * @param iturnThreshold minimum angle turn (smaller turns will be skipped)
   */
  OdomChassisController(TimeUtil itimeUtil,
                        std::shared_ptr<Odometry> iodometry,
                        const StateMode &imode = StateMode::FRAME_TRANSFORMATION,
                        const QLength &imoveThreshold = 0_mm,
                        const QAngle &iturnThreshold = 0_deg,
                        std::shared_ptr<Logger> ilogger = Logger::getDefaultLogger());

  ~OdomChassisController() override;

  OdomChassisController(const OdomChassisController &) = delete;
  OdomChassisController(OdomChassisController &&other) = delete;
  OdomChassisController &operator=(const OdomChassisController &other) = delete;
  OdomChassisController &operator=(OdomChassisController &&other) = delete;

  /**
   * Drives the robot straight to a point in the odom frame.
   *
   * @param ipoint The target point to navigate to.
   * @param ibackwards Whether to drive to the target point backwards.
   * @param ioffset An offset from the target point in the direction pointing towards the robot. The
   * robot will stop this far away from the target point.
   */
  virtual void
  driveToPoint(const Point &ipoint, bool ibackwards = false, const QLength &ioffset = 0_mm) = 0;

  /**
   * Turns the robot to face a point in the odom frame.
   *
   * @param ipoint The target point to turn to face.
   */
  virtual void turnToPoint(const Point &ipoint) = 0;

  /**
   * Turns the robot to face an angle in the odom frame.
   *
   * @param iangle The angle to turn to.
   */
  virtual void turnToAngle(const QAngle &iangle) = 0;

  /**
   * @return The current state.
   */
  virtual OdomState getState() const;

  /**
   * Set a new state to be the current state. The default StateMode is
   * `StateMode::FRAME_TRANSFORMATION`.
   *
   * @param istate The new state in the given format.
   * @param imode The mode to treat the input state as.
   */
  virtual void setState(const OdomState &istate);

  /**
   * Sets a default StateMode that will be used to interpret target points and query the Odometry
   * state.
   *
   * @param imode The new default StateMode.
   */
  void setDefaultStateMode(const StateMode &imode);

  /**
   * Set a new move threshold. Any requested movements smaller than this threshold will be skipped.
   *
   * @param imoveThreshold new move threshold
   */
  virtual void setMoveThreshold(const QLength &imoveThreshold);

  /**
   * Set a new turn threshold. Any requested turns smaller than this threshold will be skipped.
   *
   * @param iturnTreshold new turn threshold
   */
  virtual void setTurnThreshold(const QAngle &iturnTreshold);

  /**
   * @return The current move threshold.
   */
  virtual QLength getMoveThreshold() const;

  /**
   * @return The current turn threshold.
   */
  virtual QAngle getTurnThreshold() const;

  /**
   * Starts the internal odometry thread. This should not be called by normal users.
   */
  void startOdomThread();

  /**
   * @return The underlying thread handle.
   */
  CrossplatformThread *getOdomThread() const;

  /**
   * @return The internal odometry.
   */
  std::shared_ptr<Odometry> getOdometry();

  protected:
  std::shared_ptr<Logger> logger;
  TimeUtil timeUtil;
  QLength moveThreshold;
  QAngle turnThreshold;
  std::shared_ptr<Odometry> odom;
  CrossplatformThread *odomTask{nullptr};
  std::atomic_bool dtorCalled{false};
  StateMode defaultStateMode{StateMode::FRAME_TRANSFORMATION};
  std::atomic_bool odomTaskRunning{false};

  static void trampoline(void *context);
  void loop();
};
} // namespace okapi
