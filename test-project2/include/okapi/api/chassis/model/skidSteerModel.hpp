/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/model/chassisModel.hpp"
#include "okapi/api/device/motor/abstractMotor.hpp"
#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"

namespace okapi {
class SkidSteerModel : public ChassisModel {
  public:
  /**
   * Model for a skid steer drive (wheels parallel with robot's direction of motion). When all
   * motors are powered +100%, the robot should move forward in a straight line.
   *
   * @param ileftSideMotor The left side motor.
   * @param irightSideMotor The right side motor.
   * @param ileftEnc The left side encoder.
   * @param irightEnc The right side encoder.
   */
  SkidSteerModel(std::shared_ptr<AbstractMotor> ileftSideMotor,
                 std::shared_ptr<AbstractMotor> irightSideMotor,
                 std::shared_ptr<ContinuousRotarySensor> ileftEnc,
                 std::shared_ptr<ContinuousRotarySensor> irightEnc,
                 double imaxVelocity,
                 double imaxVoltage);

  /**
   * Drive the robot forwards (using open-loop control). Uses velocity mode.
   *
   * @param ispeed motor power
   */
  void forward(double ispeed) override;

  /**
   * Drive the robot in an arc (using open-loop control). Uses velocity mode.
   * The algorithm is (approximately):
   *   leftPower = ySpeed + zRotation
   *   rightPower = ySpeed - zRotation
   *
   * @param iySpeed speed on y axis (forward)
   * @param izRotation speed around z axis (up)
   */
  void driveVector(double iySpeed, double izRotation) override;

  /**
   * Drive the robot in an arc. Uses voltage mode.
   * The algorithm is (approximately):
   *   leftPower = forwardSpeed + yaw
   *   rightPower = forwardSpeed - yaw
   *
   * @param iforwadSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   */
  void driveVectorVoltage(double iforwardSpeed, double iyaw) override;

  /**
   * Turn the robot clockwise (using open-loop control). Uses velocity mode.
   *
   * @param ispeed motor power
   */
  void rotate(double ispeed) override;

  /**
   * Stop the robot (set all the motors to 0). Uses velocity mode.
   */
  void stop() override;

  /**
   * Drive the robot with a tank drive layout. Uses voltage mode.
   *
   * @param ileftSpeed left side speed
   * @param irightSpeed right side speed
   * @param ithreshold deadband on joystick values
   */
  void tank(double ileftSpeed, double irightSpeed, double ithreshold = 0) override;

  /**
   * Drive the robot with an arcade drive layout. Uses voltage mode.
   *
   * @param iforwardSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   * @param ithreshold deadband on joystick values
   */
  void arcade(double iforwardSpeed, double iyaw, double ithreshold = 0) override;

  /**
   * Drive the robot with a curvature drive layout. The robot drives in constant radius turns
   * where you control the curvature (inverse of radius) you drive in. This is advantageous
   * because the forward speed will not affect the rate of turning. The algorithm switches to
   * arcade if the forward speed is 0. Uses voltage mode.
   *
   * @param iforwardSpeed speed in the forward direction
   * @param icurvature curvature (inverse of radius) to drive in
   * @param ithreshold deadband on joystick values
   */
  void curvature(double iforwardSpeed, double icurvature, double ithreshold = 0) override;

  /**
   * Power the left side motors. Uses velocity mode.
   *
   * @param ispeed The motor power.
   */
  void left(double ispeed) override;

  /**
   * Power the right side motors. Uses velocity mode.
   *
   * @param ispeed The motor power.
   */
  void right(double ispeed) override;

  /**
   * Read the sensors.
   *
   * @return sensor readings in the format {left, right}
   */
  std::valarray<std::int32_t> getSensorVals() const override;

  /**
   * Reset the sensors to their zero point.
   */
  void resetSensors() override;

  /**
   * Set the brake mode for each motor.
   *
   * @param mode new brake mode
   */
  void setBrakeMode(AbstractMotor::brakeMode mode) override;

  /**
   * Set the encoder units for each motor.
   *
   * @param units new motor encoder units
   */
  void setEncoderUnits(AbstractMotor::encoderUnits units) override;

  /**
   * Set the gearset for each motor.
   *
   * @param gearset new motor gearset
   */
  void setGearing(AbstractMotor::gearset gearset) override;

  /**
   * Sets a new maximum velocity in RPM. The usable maximum depends on the maximum velocity of the
   * currently installed gearset. If the configured maximum velocity is greater than the attainable
   * maximum velocity from the currently installed gearset, the ChassisModel will still scale to
   * that velocity.
   *
   * @param imaxVelocity The new maximum velocity.
   */
  void setMaxVelocity(double imaxVelocity) override;

  /**
   * @return The current maximum velocity.
   */
  double getMaxVelocity() const override;

  /**
   * Sets a new maximum voltage in mV in the range `[0-12000]`.
   *
   * @param imaxVoltage The new maximum voltage.
   */
  void setMaxVoltage(double imaxVoltage) override;

  /**
   * @return The maximum voltage in mV in the range `[0-12000]`.
   */
  double getMaxVoltage() const override;

  /**
   * Returns the left side motor.
   *
   * @return the left side motor
   */
  std::shared_ptr<AbstractMotor> getLeftSideMotor() const;

  /**
   * Returns the left side motor.
   *
   * @return the left side motor
   */
  std::shared_ptr<AbstractMotor> getRightSideMotor() const;

  protected:
  double maxVelocity;
  double maxVoltage;
  std::shared_ptr<AbstractMotor> leftSideMotor;
  std::shared_ptr<AbstractMotor> rightSideMotor;
  std::shared_ptr<ContinuousRotarySensor> leftSensor;
  std::shared_ptr<ContinuousRotarySensor> rightSensor;
};
} // namespace okapi
