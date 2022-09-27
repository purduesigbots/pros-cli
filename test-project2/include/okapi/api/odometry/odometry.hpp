/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/controller/chassisScales.hpp"
#include "okapi/api/chassis/model/readOnlyChassisModel.hpp"
#include "okapi/api/odometry/odomState.hpp"
#include "okapi/api/odometry/stateMode.hpp"

namespace okapi {
class Odometry {
  public:
  /**
   * Odometry. Tracks the movement of the robot and estimates its position in coordinates
   * relative to the start (assumed to be (0, 0, 0)).
   */
  explicit Odometry() = default;

  virtual ~Odometry() = default;

  /**
   * Sets the drive and turn scales.
   */
  virtual void setScales(const ChassisScales &ichassisScales) = 0;

  /**
   * Do one odometry step.
   */
  virtual void step() = 0;

  /**
   * Returns the current state.
   *
   * @param imode The mode to return the state in.
   * @return The current state in the given format.
   */
  virtual OdomState getState(const StateMode &imode = StateMode::FRAME_TRANSFORMATION) const = 0;

  /**
   * Sets a new state to be the current state.
   *
   * @param istate The new state in the given format.
   * @param imode The mode to treat the input state as.
   */
  virtual void setState(const OdomState &istate,
                        const StateMode &imode = StateMode::FRAME_TRANSFORMATION) = 0;

  /**
   * @return The internal ChassisModel.
   */
  virtual std::shared_ptr<ReadOnlyChassisModel> getModel() = 0;

  /**
   * @return The internal ChassisScales.
   */
  virtual ChassisScales getScales() = 0;
};
} // namespace okapi
