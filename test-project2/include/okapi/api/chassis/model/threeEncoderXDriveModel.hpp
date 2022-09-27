/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/model/xDriveModel.hpp"

namespace okapi {
class ThreeEncoderXDriveModel : public XDriveModel {
  public:
  /**
   * Model for an x drive (wheels at 45 deg from a skid steer drive). When all motors are powered
   * +100%, the robot should move forward in a straight line.
   *
   * @param itopLeftMotor The top left motor.
   * @param itopRightMotor The top right motor.
   * @param ibottomRightMotor The bottom right motor.
   * @param ibottomLeftMotor The bottom left motor.
   * @param ileftEnc The left side encoder.
   * @param irightEnc The right side encoder.
   * @param imiddleEnc The middle encoder.
   */
  ThreeEncoderXDriveModel(std::shared_ptr<AbstractMotor> itopLeftMotor,
                          std::shared_ptr<AbstractMotor> itopRightMotor,
                          std::shared_ptr<AbstractMotor> ibottomRightMotor,
                          std::shared_ptr<AbstractMotor> ibottomLeftMotor,
                          std::shared_ptr<ContinuousRotarySensor> ileftEnc,
                          std::shared_ptr<ContinuousRotarySensor> irightEnc,
                          std::shared_ptr<ContinuousRotarySensor> imiddleEnc,
                          double imaxVelocity,
                          double imaxVoltage);

  /**
   * Read the sensors.
   *
   * @return sensor readings in the format {left, right, middle}
   */
  std::valarray<std::int32_t> getSensorVals() const override;

  /**
   * Reset the sensors to their zero point.
   */
  void resetSensors() override;

  protected:
  std::shared_ptr<ContinuousRotarySensor> middleSensor;
};
} // namespace okapi
