/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncPosIntegratedController.hpp"
#include "okapi/api/control/async/asyncPosPidController.hpp"
#include "okapi/api/control/async/asyncPositionController.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/impl/device/motor/motor.hpp"
#include "okapi/impl/device/motor/motorGroup.hpp"
#include "okapi/impl/device/rotarysensor/adiEncoder.hpp"
#include "okapi/impl/device/rotarysensor/integratedEncoder.hpp"
#include "okapi/impl/util/timeUtilFactory.hpp"

namespace okapi {
class AsyncPosControllerBuilder {
  public:
  /**
   * A builder that creates async position controllers. Use this to create an
   * AsyncPosIntegratedController or an AsyncPosPIDController.
   *
   * @param ilogger The logger this instance will log to.
   */
  explicit AsyncPosControllerBuilder(
    const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Sets the motor.
   *
   * @param imotor The motor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withMotor(const Motor &imotor);

  /**
   * Sets the motor.
   *
   * @param imotor The motor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withMotor(const MotorGroup &imotor);

  /**
   * Sets the motor.
   *
   * @param imotor The motor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withMotor(const std::shared_ptr<AbstractMotor> &imotor);

  /**
   * Sets the sensor. The default sensor is the motor's integrated encoder.
   *
   * @param isensor The sensor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withSensor(const ADIEncoder &isensor);

  /**
   * Sets the sensor. The default sensor is the motor's integrated encoder.
   *
   * @param isensor The sensor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withSensor(const IntegratedEncoder &isensor);

  /**
   * Sets the sensor. The default sensor is the motor's integrated encoder.
   *
   * @param isensor The sensor.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withSensor(const std::shared_ptr<RotarySensor> &isensor);

  /**
   * Sets the controller gains, causing the builder to generate an AsyncPosPIDController. This does
   * not set the integrated control's gains.
   *
   * @param igains The gains.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withGains(const IterativePosPIDController::Gains &igains);

  /**
   * Sets the derivative filter which filters the derivative term before it is scaled by kD. The
   * filter is ignored when using integrated control. The default derivative filter is a
   * PassthroughFilter.
   *
   * @param iderivativeFilter The derivative filter.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withDerivativeFilter(std::unique_ptr<Filter> iderivativeFilter);

  /**
   * Sets the gearset. The default gearset is derived from the motor's.
   *
   * @param igearset The gearset.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withGearset(const AbstractMotor::GearsetRatioPair &igearset);

  /**
   * Sets the maximum velocity. The default maximum velocity is derived from the motor's gearset.
   * This parameter is ignored when using an AsyncPosPIDController.
   *
   * @param imaxVelocity The maximum velocity.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withMaxVelocity(double imaxVelocity);

  /**
   * Sets the TimeUtilFactory used when building the controller. The default is the static
   * TimeUtilFactory.
   *
   * @param itimeUtilFactory The TimeUtilFactory.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withTimeUtilFactory(const TimeUtilFactory &itimeUtilFactory);

  /**
   * Sets the logger.
   *
   * @param ilogger The logger.
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &withLogger(const std::shared_ptr<Logger> &ilogger);

  /**
   * Parents the internal tasks started by this builder to the current task, meaning they will be
   * deleted once the current task is deleted. The `initialize` and `competition_initialize` tasks
   * are never parented to. This is the default behavior.
   *
   * Read more about this in the [builders and tasks tutorial]
   * (docs/tutorials/concepts/builders-and-tasks.md).
   *
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &parentedToCurrentTask();

  /**
   * Prevents parenting the internal tasks started by this builder to the current task, meaning they
   * will not be deleted once the current task is deleted. This can cause runaway tasks, but is
   * sometimes the desired behavior (e.x., if you want to use this builder once in `autonomous` and
   * then again in `opcontrol`).
   *
   * Read more about this in the [builders and tasks tutorial]
   * (docs/tutorials/concepts/builders-and-tasks.md).
   *
   * @return An ongoing builder.
   */
  AsyncPosControllerBuilder &notParentedToCurrentTask();

  /**
   * Builds the AsyncPositionController. Throws a std::runtime_exception is no motors were set.
   *
   * @return A fully built AsyncPositionController.
   */
  std::shared_ptr<AsyncPositionController<double, double>> build();

  private:
  std::shared_ptr<Logger> logger;

  bool hasMotors{false}; // Used to verify motors were passed
  std::shared_ptr<AbstractMotor> motor;

  bool sensorsSetByUser{false}; // Used so motors don't overwrite sensors set manually
  std::shared_ptr<RotarySensor> sensor;

  bool hasGains{false}; // Whether gains were passed, no gains means integrated control
  IterativePosPIDController::Gains gains;
  std::unique_ptr<Filter> derivativeFilter = std::make_unique<PassthroughFilter>();

  bool gearsetSetByUser{false}; // Used so motor's don't overwrite a gearset set manually
  AbstractMotor::GearsetRatioPair pair{AbstractMotor::gearset::invalid};

  bool maxVelSetByUser{false}; // Used so motors don't overwrite maxVelocity
  double maxVelocity{600};

  TimeUtilFactory timeUtilFactory = TimeUtilFactory();
  std::shared_ptr<Logger> controllerLogger = Logger::getDefaultLogger();

  bool isParentedToCurrentTask{true};

  std::shared_ptr<AsyncPosIntegratedController> buildAPIC();
  std::shared_ptr<AsyncPosPIDController> buildAPPC();
};
} // namespace okapi
