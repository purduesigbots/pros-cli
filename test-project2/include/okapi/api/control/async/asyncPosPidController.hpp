/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncPositionController.hpp"
#include "okapi/api/control/async/asyncWrapper.hpp"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/control/iterative/iterativePosPidController.hpp"
#include "okapi/api/control/offsettableControllerInput.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <memory>

namespace okapi {
class AsyncPosPIDController : public AsyncWrapper<double, double>,
                              public AsyncPositionController<double, double> {
  public:
  /**
   * An async position PID controller.
   *
   * @param iinput The controller input. Will be turned into an OffsettableControllerInput.
   * @param ioutput The controller output.
   * @param itimeUtil The TimeUtil.
   * @param ikP The proportional gain.
   * @param ikI The integral gain.
   * @param ikD The derivative gain.
   * @param ikBias The controller bias.
   * @param iratio Any external gear ratio.
   * @param iderivativeFilter The derivative filter.
   */
  AsyncPosPIDController(
    const std::shared_ptr<ControllerInput<double>> &iinput,
    const std::shared_ptr<ControllerOutput<double>> &ioutput,
    const TimeUtil &itimeUtil,
    double ikP,
    double ikI,
    double ikD,
    double ikBias = 0,
    double iratio = 1,
    std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
    const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * An async position PID controller.
   *
   * @param iinput The controller input.
   * @param ioutput The controller output.
   * @param itimeUtil The TimeUtil.
   * @param ikP The proportional gain.
   * @param ikI The integral gain.
   * @param ikD The derivative gain.
   * @param ikBias The controller bias.
   * @param iratio Any external gear ratio.
   * @param iderivativeFilter The derivative filter.
   */
  AsyncPosPIDController(
    const std::shared_ptr<OffsetableControllerInput> &iinput,
    const std::shared_ptr<ControllerOutput<double>> &ioutput,
    const TimeUtil &itimeUtil,
    double ikP,
    double ikI,
    double ikD,
    double ikBias = 0,
    double iratio = 1,
    std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
    const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Sets the "absolute" zero position of the controller to its current position.
   */
  void tarePosition() override;

  /**
   * This implementation does not respect the maximum velocity.
   *
   * @param imaxVelocity Ignored.
   */
  void setMaxVelocity(std::int32_t imaxVelocity) override;

  /**
   * Set controller gains.
   *
   * @param igains The new gains.
   */
  void setGains(const IterativePosPIDController::Gains &igains);

  /**
   * Gets the current gains.
   *
   * @return The current gains.
   */
  IterativePosPIDController::Gains getGains() const;

  protected:
  std::shared_ptr<OffsetableControllerInput> offsettableInput;
  std::shared_ptr<IterativePosPIDController> internalController;
};
} // namespace okapi
