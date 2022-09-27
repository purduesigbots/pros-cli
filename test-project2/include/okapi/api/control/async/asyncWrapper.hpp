/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncController.hpp"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/control/iterative/iterativeController.hpp"
#include "okapi/api/control/util/settledUtil.hpp"
#include "okapi/api/coreProsAPI.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/mathUtil.hpp"
#include "okapi/api/util/supplier.hpp"
#include <atomic>
#include <memory>

namespace okapi {
template <typename Input, typename Output>
class AsyncWrapper : virtual public AsyncController<Input, Output> {
  public:
  /**
   * A wrapper class that transforms an `IterativeController` into an `AsyncController` by running
   * it in another task. The input controller will act like an `AsyncController`.
   *
   * @param iinput controller input, passed to the `IterativeController`
   * @param ioutput controller output, written to from the `IterativeController`
   * @param icontroller the controller to use
   * @param irateSupplier used for rates used in the main loop and in `waitUntilSettled`
   * @param iratio Any external gear ratio.
   * @param ilogger The logger this instance will log to.
   */
  AsyncWrapper(const std::shared_ptr<ControllerInput<Input>> &iinput,
               const std::shared_ptr<ControllerOutput<Output>> &ioutput,
               const std::shared_ptr<IterativeController<Input, Output>> &icontroller,
               const Supplier<std::unique_ptr<AbstractRate>> &irateSupplier,
               const double iratio = 1,
               std::shared_ptr<Logger> ilogger = Logger::getDefaultLogger())
    : logger(std::move(ilogger)),
      rateSupplier(irateSupplier),
      input(iinput),
      output(ioutput),
      controller(icontroller),
      ratio(iratio) {
  }

  AsyncWrapper(AsyncWrapper<Input, Output> &&other) = delete;

  AsyncWrapper<Input, Output> &operator=(AsyncWrapper<Input, Output> &&other) = delete;

  ~AsyncWrapper() override {
    dtorCalled.store(true, std::memory_order_release);
    delete task;
  }

  /**
   * Sets the target for the controller.
   */
  void setTarget(const Input itarget) override {
    LOG_INFO("AsyncWrapper: Set target to " + std::to_string(itarget));
    hasFirstTarget = true;
    controller->setTarget(itarget * ratio);
    lastTarget = itarget;
  }

  /**
   * Writes the value of the controller output. This method might be automatically called in another
   * thread by the controller.
   *
   * @param ivalue the controller's output
   */
  void controllerSet(const Input ivalue) override {
    controller->controllerSet(ivalue);
  }

  /**
   * Gets the last set target, or the default target if none was set.
   *
   * @return the last target
   */
  Input getTarget() override {
    return controller->getTarget();
  }

  /**
   * @return The most recent value of the process variable.
   */
  Input getProcessValue() const override {
    return controller->getProcessValue();
  }

  /**
   * Returns the last calculated output of the controller.
   */
  Output getOutput() const {
    return controller->getOutput();
  }

  /**
   * Returns the last error of the controller. Does not update when disabled.
   */
  Output getError() const override {
    return controller->getError();
  }

  /**
   * Returns whether the controller has settled at the target. Determining what settling means is
   * implementation-dependent.
   *
   * If the controller is disabled, this method must return true.
   *
   * @return whether the controller is settled
   */
  bool isSettled() override {
    return isDisabled() || controller->isSettled();
  }

  /**
   * Set time between loops.
   *
   * @param isampleTime time between loops
   */
  void setSampleTime(const QTime &isampleTime) {
    controller->setSampleTime(isampleTime);
  }

  /**
   * Set controller output bounds.
   *
   * @param imax max output
   * @param imin min output
   */
  void setOutputLimits(const Output imax, const Output imin) {
    controller->setOutputLimits(imax, imin);
  }

  /**
   * Sets the (soft) limits for the target range that controllerSet() scales into. The target
   * computed by controllerSet() is scaled into the range [-itargetMin, itargetMax].
   *
   * @param itargetMax The new max target for controllerSet().
   * @param itargetMin The new min target for controllerSet().
   */
  void setControllerSetTargetLimits(double itargetMax, double itargetMin) {
    controller->setControllerSetTargetLimits(itargetMax, itargetMin);
  }

  /**
   * Get the upper output bound.
   *
   * @return  the upper output bound
   */
  Output getMaxOutput() {
    return controller->getMaxOutput();
  }

  /**
   * Get the lower output bound.
   *
   * @return the lower output bound
   */
  Output getMinOutput() {
    return controller->getMinOutput();
  }

  /**
   * Resets the controller's internal state so it is similar to when it was first initialized, while
   * keeping any user-configured information.
   */
  void reset() override {
    LOG_INFO_S("AsyncWrapper: Reset");
    controller->reset();
    hasFirstTarget = false;
  }

  /**
   * Changes whether the controller is off or on. Turning the controller on after it was off will
   * cause the controller to move to its last set target, unless it was reset in that time.
   */
  void flipDisable() override {
    LOG_INFO("AsyncWrapper: flipDisable " + std::to_string(!controller->isDisabled()));
    controller->flipDisable();
    resumeMovement();
  }

  /**
   * Sets whether the controller is off or on. Turning the controller on after it was off will
   * cause the controller to move to its last set target, unless it was reset in that time.
   *
   * @param iisDisabled whether the controller is disabled
   */
  void flipDisable(const bool iisDisabled) override {
    LOG_INFO("AsyncWrapper: flipDisable " + std::to_string(iisDisabled));
    controller->flipDisable(iisDisabled);
    resumeMovement();
  }

  /**
   * Returns whether the controller is currently disabled.
   *
   * @return whether the controller is currently disabled
   */
  bool isDisabled() const override {
    return controller->isDisabled();
  }

  /**
   * Blocks the current task until the controller has settled. Determining what settling means is
   * implementation-dependent.
   */
  void waitUntilSettled() override {
    LOG_INFO_S("AsyncWrapper: Waiting to settle");

    auto rate = rateSupplier.get();
    while (!isSettled()) {
      rate->delayUntil(motorUpdateRate);
    }

    LOG_INFO_S("AsyncWrapper: Done waiting to settle");
  }

  /**
   * Starts the internal thread. This should not be called by normal users. This method is called
   * by the AsyncControllerFactory when making a new instance of this class.
   */
  void startThread() {
    if (!task) {
      task = new CrossplatformThread(trampoline, this, "AsyncWrapper");
    }
  }

  /**
   * Returns the underlying thread handle.
   *
   * @return The underlying thread handle.
   */
  CrossplatformThread *getThread() const {
    return task;
  }

  protected:
  std::shared_ptr<Logger> logger;
  Supplier<std::unique_ptr<AbstractRate>> rateSupplier;
  std::shared_ptr<ControllerInput<Input>> input;
  std::shared_ptr<ControllerOutput<Output>> output;
  std::shared_ptr<IterativeController<Input, Output>> controller;
  bool hasFirstTarget{false};
  Input lastTarget;
  double ratio;
  std::atomic_bool dtorCalled{false};
  CrossplatformThread *task{nullptr};

  static void trampoline(void *context) {
    if (context) {
      static_cast<AsyncWrapper *>(context)->loop();
    }
  }

  void loop() {
    auto rate = rateSupplier.get();
    while (!dtorCalled.load(std::memory_order_acquire) && !task->notifyTake(0)) {
      if (!isDisabled()) {
        output->controllerSet(controller->step(input->controllerGet()));
      }

      rate->delayUntil(controller->getSampleTime());
    }
  }

  /**
   * Resumes moving after the controller is reset. Should not cause movement if the controller is
   * turned off, reset, and turned back on.
   */
  virtual void resumeMovement() {
    if (isDisabled()) {
      // This will grab the output *when disabled*
      output->controllerSet(controller->getOutput());
    } else {
      if (hasFirstTarget) {
        setTarget(lastTarget);
      }
    }
  }
};
} // namespace okapi
