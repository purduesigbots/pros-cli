/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/iterative/iterativeMotorVelocityController.hpp"
#include "okapi/api/control/iterative/iterativePosPidController.hpp"
#include "okapi/api/control/iterative/iterativeVelPidController.hpp"
#include "okapi/api/util/mathUtil.hpp"
#include "okapi/impl/device/motor/motor.hpp"
#include "okapi/impl/device/motor/motorGroup.hpp"
#include "okapi/impl/filter/velMathFactory.hpp"

namespace okapi {
class IterativeControllerFactory {
  public:
  /**
   * Position PID controller.
   *
   * @param ikP proportional gain
   * @param ikI integral gain
   * @param ikD derivative gain
   * @param ikBias controller bias (constant offset added to the output)
   * @param iderivativeFilter A filter for filtering the derivative term.
   * @param ilogger The logger this instance will log to.
   */
  static IterativePosPIDController
  posPID(double ikP,
         double ikI,
         double ikD,
         double ikBias = 0,
         std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
         const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity PD controller.
   *
   * @param ikP proportional gain
   * @param ikD derivative gain
   * @param ikF feed-forward gain
   * @param ikSF a feed-forward gain to counteract static friction
   * @param iderivativeFilter A filter for filtering the derivative term.
   * @param ilogger The logger this instance will log to.
   */
  static IterativeVelPIDController
  velPID(double ikP,
         double ikD,
         double ikF = 0,
         double ikSF = 0,
         std::unique_ptr<VelMath> ivelMath = VelMathFactory::createPtr(imev5GreenTPR),
         std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
         const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity PD controller that automatically writes to the motor.
   *
   * @param imotor output motor
   * @param ikP proportional gain
   * @param ikD derivative gain
   * @param ikF feed-forward gain
   * @param ikSF a feed-forward gain to counteract static friction
   * @param ivelMath The VelMath.
   * @param iderivativeFilter A filter for filtering the derivative term.
   * @param ilogger The logger this instance will log to.
   */
  static IterativeMotorVelocityController
  motorVelocity(Motor imotor,
                double ikP,
                double ikD,
                double ikF = 0,
                double ikSF = 0,
                std::unique_ptr<VelMath> ivelMath = VelMathFactory::createPtr(imev5GreenTPR),
                std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
                const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity PD controller that automatically writes to the motor.
   *
   * @param imotor output motor
   * @param ikP proportional gain
   * @param ikD derivative gain
   * @param ikF feed-forward gain
   * @param ikSF a feed-forward gain to counteract static friction
   * @param ivelMath The VelMath.
   * @param iderivativeFilter A filter for filtering the derivative term.
   * @param ilogger The logger this instance will log to.
   */
  static IterativeMotorVelocityController
  motorVelocity(MotorGroup imotor,
                double ikP,
                double ikD,
                double ikF = 0,
                double ikSF = 0,
                std::unique_ptr<VelMath> ivelMath = VelMathFactory::createPtr(imev5GreenTPR),
                std::unique_ptr<Filter> iderivativeFilter = std::make_unique<PassthroughFilter>(),
                const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity PD controller that automatically writes to the motor.
   *
   * @param imotor output motor
   * @param icontroller controller to use
   */
  static IterativeMotorVelocityController
  motorVelocity(Motor imotor,
                std::shared_ptr<IterativeVelocityController<double, double>> icontroller);

  /**
   * Velocity PD controller that automatically writes to the motor.
   *
   * @param imotor output motor
   * @param icontroller controller to use
   */
  static IterativeMotorVelocityController
  motorVelocity(MotorGroup imotor,
                std::shared_ptr<IterativeVelocityController<double, double>> icontroller);
};
} // namespace okapi
