/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncVelocityController.hpp"
#include "okapi/api/control/async/asyncWrapper.hpp"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/control/iterative/iterativeVelPidController.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <memory>

namespace okapi {
class AsyncVelPIDController : public AsyncWrapper<double, double>,
                              public AsyncVelocityController<double, double> {
  public:
  /**
   * An async velocity PID controller.
   *
   * @param iinput The controller input.
   * @param ioutput The controller output.
   * @param itimeUtil The TimeUtil.
   * @param ikP The proportional gain.
   * @param ikD The derivative gain.
   * @param ikF The feed-forward gain.
   * @param ikSF A feed-forward gain to counteract static friction.
   * @param ivelMath The VelMath used for calculating velocity.
   * @param iratio Any external gear ratio.
   * @param iderivativeFilter The derivative filter.
   */
  AsyncVelPIDController(
    const std::shared_ptr<ControllerInput<double>> &iinput,
    const std::shared_ptr<ControllerOutput<double>> &ioutput,
    const TimeUtil &itimeUtil,
    double ikP,
    double ikD,
    double ikF,
    double ikSF,
    std::unique_ptr<VelMath> ivelMath,
    double iratio = 1,
    std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
    const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Set controller gains.
   *
   * @param igains The new gains.
   */
  void setGains(const IterativeVelPIDController::Gains &igains);

  /**
   * Gets the current gains.
   *
   * @return The current gains.
   */
  IterativeVelPIDController::Gains getGains() const;

  protected:
  std::shared_ptr<IterativeVelPIDController> internalController;
};
} // namespace okapi
