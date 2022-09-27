/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

/** @mainpage OkapiLib Index Page
 *
 * @section intro_sec Introduction
 *
 * **OkapiLib** is a PROS library for programming VEX V5 robots. This library is intended to raise
 * the floor for teams with all levels of experience. New teams should have an easier time getting
 * their robot up and running, and veteran teams should find that OkapiLib doesn't get in the way or
 * place any limits on functionality.
 *
 * For tutorials on how to get the most out of OkapiLib, see the
 * [Tutorials](docs/tutorials/index.md) section. For documentation on using the OkapiLib API, see
 * the [API](docs/api/index.md) section.
 *
 * @section getting_started Getting Started
 * Not sure where to start? Take a look at the
 * [Getting Started](docs/tutorials/walkthrough/gettingStarted.md) tutorial.
 * Once you have OkapiLib set up, check out the
 * [Clawbot](docs/tutorials/walkthrough/clawbot.md) tutorial.
 *
 * @section using_docs Using The Documentation
 *
 * Start with reading the [Tutorials](docs/tutorials/index.md). Use the [API](docs/api/index.md)
 * section to explore the class hierarchy. To see a list of all available classes, use the
 * [Classes](annotated.html) section.
 *
 * This documentation has a powerful search feature, which can be brought up with the keyboard
 * shortcuts `Tab` or `T`. All exports to the `okapi` namespace such as enums, constants, units, or
 * functions can be found [here](@ref okapi).
 */

#include "okapi/api/chassis/controller/chassisControllerIntegrated.hpp"
#include "okapi/api/chassis/controller/chassisControllerPid.hpp"
#include "okapi/api/chassis/controller/chassisScales.hpp"
#include "okapi/api/chassis/controller/defaultOdomChassisController.hpp"
#include "okapi/api/chassis/controller/odomChassisController.hpp"
#include "okapi/api/chassis/model/hDriveModel.hpp"
#include "okapi/api/chassis/model/readOnlyChassisModel.hpp"
#include "okapi/api/chassis/model/skidSteerModel.hpp"
#include "okapi/api/chassis/model/threeEncoderSkidSteerModel.hpp"
#include "okapi/api/chassis/model/threeEncoderXDriveModel.hpp"
#include "okapi/api/chassis/model/xDriveModel.hpp"
#include "okapi/impl/chassis/controller/chassisControllerBuilder.hpp"

#include "okapi/api/control/async/asyncLinearMotionProfileController.hpp"
#include "okapi/api/control/async/asyncMotionProfileController.hpp"
#include "okapi/api/control/async/asyncPosIntegratedController.hpp"
#include "okapi/api/control/async/asyncPosPidController.hpp"
#include "okapi/api/control/async/asyncVelIntegratedController.hpp"
#include "okapi/api/control/async/asyncVelPidController.hpp"
#include "okapi/api/control/async/asyncWrapper.hpp"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/control/iterative/iterativeMotorVelocityController.hpp"
#include "okapi/api/control/iterative/iterativePosPidController.hpp"
#include "okapi/api/control/iterative/iterativeVelPidController.hpp"
#include "okapi/api/control/util/controllerRunner.hpp"
#include "okapi/api/control/util/flywheelSimulator.hpp"
#include "okapi/api/control/util/pidTuner.hpp"
#include "okapi/api/control/util/settledUtil.hpp"
#include "okapi/impl/control/async/asyncMotionProfileControllerBuilder.hpp"
#include "okapi/impl/control/async/asyncPosControllerBuilder.hpp"
#include "okapi/impl/control/async/asyncVelControllerBuilder.hpp"
#include "okapi/impl/control/iterative/iterativeControllerFactory.hpp"
#include "okapi/impl/control/util/controllerRunnerFactory.hpp"
#include "okapi/impl/control/util/pidTunerFactory.hpp"

#include "okapi/api/odometry/odomMath.hpp"
#include "okapi/api/odometry/odometry.hpp"
#include "okapi/api/odometry/threeEncoderOdometry.hpp"

#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"
#include "okapi/api/device/rotarysensor/rotarySensor.hpp"
#include "okapi/impl/device/adiUltrasonic.hpp"
#include "okapi/impl/device/button/adiButton.hpp"
#include "okapi/impl/device/button/controllerButton.hpp"
#include "okapi/impl/device/controller.hpp"
#include "okapi/impl/device/distanceSensor.hpp"
#include "okapi/impl/device/motor/adiMotor.hpp"
#include "okapi/impl/device/motor/motor.hpp"
#include "okapi/impl/device/motor/motorGroup.hpp"
#include "okapi/impl/device/opticalSensor.hpp"
#include "okapi/impl/device/rotarysensor/IMU.hpp"
#include "okapi/impl/device/rotarysensor/adiEncoder.hpp"
#include "okapi/impl/device/rotarysensor/adiGyro.hpp"
#include "okapi/impl/device/rotarysensor/integratedEncoder.hpp"
#include "okapi/impl/device/rotarysensor/potentiometer.hpp"
#include "okapi/impl/device/rotarysensor/rotationSensor.hpp"

#include "okapi/api/filter/averageFilter.hpp"
#include "okapi/api/filter/composableFilter.hpp"
#include "okapi/api/filter/demaFilter.hpp"
#include "okapi/api/filter/ekfFilter.hpp"
#include "okapi/api/filter/emaFilter.hpp"
#include "okapi/api/filter/filter.hpp"
#include "okapi/api/filter/filteredControllerInput.hpp"
#include "okapi/api/filter/medianFilter.hpp"
#include "okapi/api/filter/passthroughFilter.hpp"
#include "okapi/api/filter/velMath.hpp"
#include "okapi/impl/filter/velMathFactory.hpp"

#include "okapi/api/units/QAcceleration.hpp"
#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QAngularAcceleration.hpp"
#include "okapi/api/units/QAngularJerk.hpp"
#include "okapi/api/units/QAngularSpeed.hpp"
#include "okapi/api/units/QArea.hpp"
#include "okapi/api/units/QForce.hpp"
#include "okapi/api/units/QFrequency.hpp"
#include "okapi/api/units/QJerk.hpp"
#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/QMass.hpp"
#include "okapi/api/units/QPressure.hpp"
#include "okapi/api/units/QSpeed.hpp"
#include "okapi/api/units/QTime.hpp"
#include "okapi/api/units/QTorque.hpp"
#include "okapi/api/units/QVolume.hpp"
#include "okapi/api/units/RQuantityName.hpp"

#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/abstractTimer.hpp"
#include "okapi/api/util/mathUtil.hpp"
#include "okapi/api/util/supplier.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include "okapi/impl/util/configurableTimeUtilFactory.hpp"
#include "okapi/impl/util/rate.hpp"
#include "okapi/impl/util/timeUtilFactory.hpp"
#include "okapi/impl/util/timer.hpp"
