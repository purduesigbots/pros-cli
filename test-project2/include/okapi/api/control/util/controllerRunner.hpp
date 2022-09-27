/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncController.hpp"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/control/iterative/iterativeController.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <memory>

namespace okapi {
template <typename Input, typename Output> class ControllerRunner {
  public:
  /**
   * A utility class that runs a closed-loop controller.
   *
   * @param itimeUtil The TimeUtil.
   * @param ilogger The logger this instance will log to.
   */
  explicit ControllerRunner(const TimeUtil &itimeUtil,
                            const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger())
    : logger(ilogger), rate(itimeUtil.getRate()) {
  }

  /**
   * Runs the controller until it has settled.
   *
   * @param itarget the new target
   * @param icontroller the controller to run
   * @return the error when settled
   */
  virtual Output runUntilSettled(const Input itarget, AsyncController<Input, Output> &icontroller) {
    LOG_INFO("ControllerRunner: runUntilSettled(AsyncController): Set target to " +
             std::to_string(itarget));
    icontroller.setTarget(itarget);

    while (!icontroller.isSettled()) {
      rate->delayUntil(10_ms);
    }

    LOG_INFO("ControllerRunner: runUntilSettled(AsyncController): Done waiting to settle");
    return icontroller.getError();
  }

  /**
   * Runs the controller until it has settled.
   *
   * @param itarget the new target
   * @param icontroller the controller to run
   * @param ioutput the output to write to
   * @return the error when settled
   */
  virtual Output runUntilSettled(const Input itarget,
                                 IterativeController<Input, Output> &icontroller,
                                 ControllerOutput<Output> &ioutput) {
    LOG_INFO("ControllerRunner: runUntilSettled(IterativeController): Set target to " +
             std::to_string(itarget));
    icontroller.setTarget(itarget);

    while (!icontroller.isSettled()) {
      ioutput.controllerSet(icontroller.getOutput());
      rate->delayUntil(10_ms);
    }

    LOG_INFO("ControllerRunner: runUntilSettled(IterativeController): Done waiting to settle");
    return icontroller.getError();
  }

  /**
   * Runs the controller until it has reached its target, but not necessarily settled.
   *
   * @param itarget the new target
   * @param icontroller the controller to run
   * @return the error when settled
   */
  virtual Output runUntilAtTarget(const Input itarget,
                                  AsyncController<Input, Output> &icontroller) {
    LOG_INFO("ControllerRunner: runUntilAtTarget(AsyncController): Set target to " +
             std::to_string(itarget));
    icontroller.setTarget(itarget);

    double error = icontroller.getError();
    double lastError = error;
    while (error != 0 && std::copysign(1.0, error) == std::copysign(1.0, lastError)) {
      lastError = error;
      rate->delayUntil(10_ms);
      error = icontroller.getError();
    }

    LOG_INFO("ControllerRunner: runUntilAtTarget(AsyncController): Done waiting to settle");
    return icontroller.getError();
  }

  /**
   * Runs the controller until it has reached its target, but not necessarily settled.
   *
   * @param itarget the new target
   * @param icontroller the controller to run
   * @param ioutput the output to write to
   * @return the error when settled
   */
  virtual Output runUntilAtTarget(const Input itarget,
                                  IterativeController<Input, Output> &icontroller,
                                  ControllerOutput<Output> &ioutput) {
    LOG_INFO("ControllerRunner: runUntilAtTarget(IterativeController): Set target to " +
             std::to_string(itarget));
    icontroller.setTarget(itarget);

    double error = icontroller.getError();
    double lastError = error;
    while (error != 0 && std::copysign(1.0, error) == std::copysign(1.0, lastError)) {
      ioutput.controllerSet(icontroller.getOutput());
      lastError = error;
      rate->delayUntil(10_ms);
      error = icontroller.getError();
    }

    LOG_INFO("ControllerRunner: runUntilAtTarget(IterativeController): Done waiting to settle");
    return icontroller.getError();
  }

  protected:
  std::shared_ptr<Logger> logger;
  std::unique_ptr<AbstractRate> rate;
};
} // namespace okapi
