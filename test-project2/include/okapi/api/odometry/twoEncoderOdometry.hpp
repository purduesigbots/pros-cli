/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/odometry/odometry.hpp"
#include "okapi/api/units/QSpeed.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <atomic>
#include <memory>
#include <valarray>

namespace okapi {
class TwoEncoderOdometry : public Odometry {
  public:
  /**
   * TwoEncoderOdometry. Tracks the movement of the robot and estimates its position in coordinates
   * relative to the start (assumed to be (0, 0, 0)).
   *
   * @param itimeUtil The TimeUtil.
   * @param imodel The chassis model for reading sensors.
   * @param ichassisScales The chassis dimensions.
   * @param ilogger The logger this instance will log to.
   */
  TwoEncoderOdometry(const TimeUtil &itimeUtil,
                     const std::shared_ptr<ReadOnlyChassisModel> &imodel,
                     const ChassisScales &ichassisScales,
                     const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  virtual ~TwoEncoderOdometry() = default;

  /**
   * Sets the drive and turn scales.
   */
  void setScales(const ChassisScales &ichassisScales) override;

  /**
   * Do one odometry step.
   */
  void step() override;

  /**
   * Returns the current state.
   *
   * @param imode The mode to return the state in.
   * @return The current state in the given format.
   */
  OdomState getState(const StateMode &imode = StateMode::FRAME_TRANSFORMATION) const override;

  /**
   * Sets a new state to be the current state.
   *
   * @param istate The new state in the given format.
   * @param imode The mode to treat the input state as.
   */
  void setState(const OdomState &istate,
                const StateMode &imode = StateMode::FRAME_TRANSFORMATION) override;

  /**
   * @return The internal ChassisModel.
   */
  std::shared_ptr<ReadOnlyChassisModel> getModel() override;

  /**
   * @return The internal ChassisScales.
   */
  ChassisScales getScales() override;

  protected:
  std::shared_ptr<Logger> logger;
  std::unique_ptr<AbstractRate> rate;
  std::unique_ptr<AbstractTimer> timer;
  std::shared_ptr<ReadOnlyChassisModel> model;
  ChassisScales chassisScales;
  OdomState state;
  std::valarray<std::int32_t> newTicks{0, 0, 0}, tickDiff{0, 0, 0}, lastTicks{0, 0, 0};
  const std::int32_t maximumTickDiff{1000};

  /**
   * Does the math, side-effect free, for one odom step.
   *
   * @param itickDiff The tick difference from the previous step to this step.
   * @param ideltaT The time difference from the previous step to this step.
   * @return The newly computed OdomState.
   */
  virtual OdomState odomMathStep(const std::valarray<std::int32_t> &itickDiff,
                                 const QTime &ideltaT);
};
} // namespace okapi
