/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/model/readOnlyChassisModel.hpp"
#include "okapi/api/device/motor/abstractMotor.hpp"
#include <array>
#include <initializer_list>
#include <memory>
#include <vector>

namespace okapi {
/**
 * A version of the ReadOnlyChassisModel that also supports write methods, such as setting motor
 * speed. Because this class can write to motors, there can only be one owner and as such copying
 * is disabled.
 */
class ChassisModel : public ReadOnlyChassisModel {
  public:
  explicit ChassisModel() = default;
  ChassisModel(const ChassisModel &) = delete;
  ChassisModel &operator=(const ChassisModel &) = delete;

  /**
   * Drive the robot forwards (using open-loop control). Uses velocity mode.
   *
   * @param ipower motor power
   */
  virtual void forward(double ispeed) = 0;

  /**
   * Drive the robot in an arc (using open-loop control). Uses velocity mode.
   * The algorithm is (approximately):
   *   leftPower = forwardSpeed + yaw
   *   rightPower = forwardSpeed - yaw
   *
   * @param iforwadSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   */
  virtual void driveVector(double iforwardSpeed, double iyaw) = 0;

  /**
   * Drive the robot in an arc. Uses voltage mode.
   * The algorithm is (approximately):
   *   leftPower = forwardSpeed + yaw
   *   rightPower = forwardSpeed - yaw
   *
   * @param iforwadSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   */
  virtual void driveVectorVoltage(double iforwardSpeed, double iyaw) = 0;

  /**
   * Turn the robot clockwise (using open-loop control). Uses velocity mode.
   *
   * @param ispeed motor power
   */
  virtual void rotate(double ispeed) = 0;

  /**
   * Stop the robot (set all the motors to 0). Uses velocity mode.
   */
  virtual void stop() = 0;

  /**
   * Drive the robot with a tank drive layout. Uses voltage mode.
   *
   * @param ileftSpeed left side speed
   * @param irightSpeed right side speed
   * @param ithreshold deadband on joystick values
   */
  virtual void tank(double ileftSpeed, double irightSpeed, double ithreshold = 0) = 0;

  /**
   * Drive the robot with an arcade drive layout. Uses voltage mode.
   *
   * @param iforwardSpeed speed forward direction
   * @param iyaw speed around the vertical axis
   * @param ithreshold deadband on joystick values
   */
  virtual void arcade(double iforwardSpeed, double iyaw, double ithreshold = 0) = 0;

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
  virtual void curvature(double iforwardSpeed, double icurvature, double ithreshold = 0) = 0;

  /**
   * Power the left side motors. Uses velocity mode.
   *
   * @param ipower motor power
   */
  virtual void left(double ispeed) = 0;

  /**
   * Power the right side motors. Uses velocity mode.
   *
   * @param ipower motor power
   */
  virtual void right(double ispeed) = 0;

  /**
   * Reset the sensors to their zero point.
   */
  virtual void resetSensors() = 0;

  /**
   * Set the brake mode for each motor.
   *
   * @param mode new brake mode
   */
  virtual void setBrakeMode(AbstractMotor::brakeMode mode) = 0;

  /**
   * Set the encoder units for each motor.
   *
   * @param units new motor encoder units
   */
  virtual void setEncoderUnits(AbstractMotor::encoderUnits units) = 0;

  /**
   * Set the gearset for each motor.
   *
   * @param gearset new motor gearset
   */
  virtual void setGearing(AbstractMotor::gearset gearset) = 0;

  /**
   * Sets a new maximum velocity in RPM. The usable maximum depends on the maximum velocity of the
   * currently installed gearset. If the configured maximum velocity is greater than the attainable
   * maximum velocity from the currently installed gearset, the ChassisModel will still scale to
   * that velocity.
   *
   * @param imaxVelocity The new maximum velocity.
   */
  virtual void setMaxVelocity(double imaxVelocity) = 0;

  /**
   * @return The current maximum velocity.
   */
  virtual double getMaxVelocity() const = 0;

  /**
   * Sets a new maximum voltage in mV in the range `[0-12000]`.
   *
   * @param imaxVoltage The new maximum voltage.
   */
  virtual void setMaxVoltage(double imaxVoltage) = 0;

  /**
   * @return The maximum voltage in mV `[0-12000]`.
   */
  virtual double getMaxVoltage() const = 0;
};
} // namespace okapi
