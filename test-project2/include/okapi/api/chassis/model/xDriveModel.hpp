/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/chassis/model/chassisModel.hpp"
#include "okapi/api/device/motor/abstractMotor.hpp"
#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"
#include "okapi/api/units/QAngle.hpp"

namespace okapi {
class XDriveModel : public ChassisModel {
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
   */
  XDriveModel(std::shared_ptr<AbstractMotor> itopLeftMotor,
              std::shared_ptr<AbstractMotor> itopRightMotor,
              std::shared_ptr<AbstractMotor> ibottomRightMotor,
              std::shared_ptr<AbstractMotor> ibottomLeftMotor,
              std::shared_ptr<ContinuousRotarySensor> ileftEnc,
              std::shared_ptr<ContinuousRotarySensor> irightEnc,
              double imaxVelocity,
              double imaxVoltage);

  /**
   * Drive the robot forwards (using open-loop control). Uses velocity mode.
   *
   * @param ispeed motor power
   */
  void forward(double ipower) override;

  /**
   * Drive the robot in an arc (using open-loop control). Uses velocity mode.
   * The algorithm is (approximately):
   *   leftPower = forwardSpeed + yaw
   *   rightPower = forwardSpeed - yaw
   *
   * @param iforwardSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   */
  void driveVector(double iforwardSpeed, double iyaw) override;

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
   * @param ipower motor power
   */
  void rotate(double ipower) override;

  /**
   * Drive the robot side-ways (using open-loop control) where positive ipower is
   * to the right and negative ipower is to the left. Uses velocity mode.
   *
   * @param ispeed motor power
   */
  void strafe(double ipower);

  /**
   * Strafe the robot in an arc (using open-loop control) where positive istrafeSpeed is
   * to the right and negative istrafeSpeed is to the left. Uses velocity mode.
   * The algorithm is (approximately):
   *   topLeftPower = -1 * istrafeSpeed + yaw
   *   topRightPower = istrafeSpeed - yaw
   *   bottomRightPower = -1 * istrafeSpeed - yaw
   *   bottomLeftPower = istrafeSpeed + yaw
   *
   * @param istrafeSpeed speed to the right
   * @param iyaw speed around the vertical axis
   */
  void strafeVector(double istrafeSpeed, double iyaw);

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
   * @param iforwardSpeed speed forward direction
   * @param icurvature curvature (inverse of radius) to drive in
   * @param ithreshold deadband on joystick values
   */
  void curvature(double iforwardSpeed, double icurvature, double ithreshold = 0) override;

  /**
   * Drive the robot with an arcade drive layout. Uses voltage mode.
   *
   * @param irightSpeed speed to the right
   * @param iforwardSpeed speed in the forward direction
   * @param iyaw speed around the vertical axis
   * @param ithreshold deadband on joystick values
   */
  virtual void
  xArcade(double irightSpeed, double iforwardSpeed, double iyaw, double ithreshold = 0);

  /**
   * Drive the robot with a field-oriented arcade drive layout. Uses voltage mode.
   * For example:
   *    Both `fieldOrientedXArcade(1, 0, 0, 0_deg)` and `fieldOrientedXArcade(1, 0, 0, 90_deg)`
   *    will drive the chassis in the forward/north direction. In other words, no matter
   *    the robot's heading, the robot will move forward/north when you tell it
   *    to move forward/north and will move right/east when you tell it to move right/east.
   *
   *
   * @param ixSpeed forward speed -- (`+1`) forward, (`-1`) backward
   * @param iySpeed sideways speed -- (`+1`) right, (`-1`) left
   * @param iyaw turn speed -- (`+1`) clockwise, (`-1`) counter-clockwise
   * @param iangle current chassis angle (`0_deg` = no correction, winds clockwise)
   * @param ithreshold deadband on joystick values
   */
  virtual void fieldOrientedXArcade(double ixSpeed,
                                    double iySpeed,
                                    double iyaw,
                                    QAngle iangle,
                                    double ithreshold = 0);

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
   * Returns the top left motor.
   *
   * @return the top left motor
   */
  std::shared_ptr<AbstractMotor> getTopLeftMotor() const;

  /**
   * Returns the top right motor.
   *
   * @return the top right motor
   */
  std::shared_ptr<AbstractMotor> getTopRightMotor() const;

  /**
   * Returns the bottom right motor.
   *
   * @return the bottom right motor
   */
  std::shared_ptr<AbstractMotor> getBottomRightMotor() const;

  /**
   * Returns the bottom left motor.
   *
   * @return the bottom left motor
   */
  std::shared_ptr<AbstractMotor> getBottomLeftMotor() const;

  protected:
  double maxVelocity;
  double maxVoltage;
  std::shared_ptr<AbstractMotor> topLeftMotor;
  std::shared_ptr<AbstractMotor> topRightMotor;
  std::shared_ptr<AbstractMotor> bottomRightMotor;
  std::shared_ptr<AbstractMotor> bottomLeftMotor;
  std::shared_ptr<ContinuousRotarySensor> leftSensor;
  std::shared_ptr<ContinuousRotarySensor> rightSensor;
};
} // namespace okapi
