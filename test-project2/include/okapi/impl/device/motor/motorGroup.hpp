/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/device/motor/abstractMotor.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/impl/device/motor/motor.hpp"
#include <initializer_list>
#include <vector>

namespace okapi {
class MotorGroup : public AbstractMotor {
  public:
  /**
   * A group of V5 motors which act as one motor (i.e. they are mechanically linked). A MotorGroup
   * requires at least one motor. If no motors are supplied, a `std::invalid_argument` exception is
   * thrown.
   *
   * @param imotors The motors in this group.
   * @param ilogger The logger this instance will log initialization warnings to.
   */
  MotorGroup(const std::initializer_list<Motor> &imotors,
             const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * A group of V5 motors which act as one motor (i.e. they are mechanically linked). A MotorGroup
   * requires at least one motor. If no motors are supplied, a `std::invalid_argument` exception is
   * thrown.
   *
   * @param imotors The motors in this group.
   * @param ilogger The logger this instance will log initialization warnings to.
   */
  MotorGroup(const std::initializer_list<std::shared_ptr<AbstractMotor>> &imotors,
             const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /******************************************************************************/
  /**                         Motor movement functions                         **/
  /**                                                                          **/
  /**          These functions allow programmers to make motors move           **/
  /******************************************************************************/

  /**
   * Sets the target absolute position for the motor to move to.
   *
   * This movement is relative to the position of the motor when initialized or
   * the position when it was most recently reset with setZeroPosition().
   *
   * @note This function simply sets the target for the motor, it does not block program execution
   * until the movement finishes.
   *
   * @param iposition The absolute position to move to in the motor's encoder units
   * @param ivelocity The maximum allowable velocity for the movement in RPM
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t moveAbsolute(double iposition, std::int32_t ivelocity) override;

  /**
   * Sets the relative target position for the motor to move to.
   *
   * This movement is relative to the current position of the motor. Providing 10.0 as the position
   * parameter would result in the motor moving clockwise 10 units, no matter what the current
   * position is.
   *
   * @note This function simply sets the target for the motor, it does not block program execution
   * until the movement finishes.
   *
   * @param iposition The relative position to move to in the motor's encoder units
   * @param ivelocity The maximum allowable velocity for the movement in RPM
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t moveRelative(double iposition, std::int32_t ivelocity) override;

  /**
   * Sets the velocity for the motor.
   *
   * This velocity corresponds to different actual speeds depending on the gearset
   * used for the motor. This results in a range of +-100 for pros::c::red,
   * +-200 for green, and +-600 for blue. The velocity
   * is held with PID to ensure consistent speed, as opposed to setting the motor's
   * voltage.
   *
   * @param ivelocity The new motor velocity from -+-100, +-200, or +-600 depending on the motor's
   * gearset
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t moveVelocity(std::int16_t ivelocity) override;

  /**
   * Sets the voltage for the motor from `-12000` to `12000`.
   *
   * @param ivoltage The new voltage value from `-12000` to `12000`.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t moveVoltage(std::int16_t ivoltage) override;

  /**
   * Changes the output velocity for a profiled movement (moveAbsolute or moveRelative). This will
   * have no effect if the motor is not following a profiled movement.
   *
   * @param ivelocity The new motor velocity from `+-100`, `+-200`, or `+-600` depending on the
   * motor's gearset.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t modifyProfiledVelocity(std::int32_t ivelocity) override;

  /******************************************************************************/
  /**                        Motor telemetry functions                         **/
  /**                                                                          **/
  /**    These functions allow programmers to collect telemetry from motors    **/
  /******************************************************************************/

  /**
   * Gets the target position set for the motor by the user.
   *
   * @return The target position in its encoder units or `PROS_ERR_F` if the operation failed,
   * setting errno.
   */
  double getTargetPosition() override;

  /**
   * Gets the absolute position of the motor in its encoder units.
   *
   * @return The motor's absolute position in its encoder units or `PROS_ERR_F` if the operation
   * failed, setting errno.
   */
  double getPosition() override;

  /**
   * Sets the "absolute" zero position of the motor to its current position.
   *
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t tarePosition() override;

  /**
   * Gets the velocity commanded to the motor by the user.
   *
   * @return The commanded motor velocity from +-100, +-200, or +-600, or `PROS_ERR` if the
   * operation failed, setting errno.
   */
  std::int32_t getTargetVelocity() override;

  /**
   * Gets the actual velocity of the motor.
   *
   * @return The motor's actual velocity in RPM or `PROS_ERR_F` if the operation failed, setting
   * errno.
   */
  double getActualVelocity() override;

  /**
   * Gets the current drawn by the motor in mA.
   *
   * @return The motor's current in mA or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t getCurrentDraw() override;

  /**
   * Gets the direction of movement for the motor.
   *
   * @return 1 for moving in the positive direction, -1 for moving in the negative direction, and
   * `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t getDirection() override;

  /**
   * Gets the efficiency of the motor in percent.
   *
   * An efficiency of 100% means that the motor is moving electrically while
   * drawing no electrical power, and an efficiency of 0% means that the motor
   * is drawing power but not moving.
   *
   * @return The motor's efficiency in percent or `PROS_ERR_F` if the operation failed, setting
   * errno.
   */
  double getEfficiency() override;

  /**
   * Checks if the motor is drawing over its current limit.
   *
   * @return 1 if the motor's current limit is being exceeded and 0 if the current limit is not
   * exceeded, or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t isOverCurrent() override;

  /**
   * Checks if the motor's temperature is above its limit.
   *
   * @return 1 if the temperature limit is exceeded and 0 if the the temperature is below the limit,
   * or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t isOverTemp() override;

  /**
   * Checks if the motor is stopped.
   *
   * Although this function forwards data from the motor, the motor presently does not provide any
   * value. This function returns `PROS_ERR` with errno set to `ENOSYS`.
   *
   * @return 1 if the motor is not moving, 0 if the motor is moving, or `PROS_ERR` if the operation
   * failed, setting errno
   */
  std::int32_t isStopped() override;

  /**
   * Checks if the motor is at its zero position.
   *
   * Although this function forwards data from the motor, the motor presently does not provide any
   * value. This function returns `PROS_ERR` with errno set to `ENOSYS`.
   *
   * @return 1 if the motor is at zero absolute position, `0` if the motor has moved from its
   * absolute zero, or `PROS_ERR` if the operation failed, setting errno
   */
  std::int32_t getZeroPositionFlag() override;

  /**
   * Gets the faults experienced by the motor. Compare this bitfield to the bitmasks in
   * pros::motor_fault_e_t.
   *
   * @return A currently unknown bitfield containing the motor's faults. `0b00000100` = Current
   * Limit Hit
   */
  uint32_t getFaults() override;

  /**
   * Gets the flags set by the motor's operation. Compare this bitfield to the bitmasks in
   * pros::motor_flag_e_t.
   *
   * @return A currently unknown bitfield containing the motor's flags. These seem to be unrelated
   * to the individual get_specific_flag functions
   */
  uint32_t getFlags() override;

  /**
   * Gets the raw encoder count of the motor at a given timestamp.
   *
   * @param timestamp A pointer to a time in milliseconds for which the encoder count will be
   * returned. If `NULL`, the timestamp at which the encoder count was read will not be supplied.
   * @return The raw encoder count at the given timestamp or `PROS_ERR` if the operation failed.
   */
  std::int32_t getRawPosition(std::uint32_t *timestamp) override;

  /**
   * Gets the power drawn by the motor in Watts.
   *
   * @return The motor's power draw in Watts or `PROS_ERR_F` if the operation failed, setting errno.
   */
  double getPower() override;

  /**
   * Gets the temperature of the motor in degrees Celsius.
   *
   * @return The motor's temperature in degrees Celsius or `PROS_ERR_F` if the operation failed,
   * setting errno.
   */
  double getTemperature() override;

  /**
   * Gets the torque generated by the motor in Newton Metres (Nm).
   *
   * @return The motor's torque in NM or `PROS_ERR_F` if the operation failed, setting errno.
   */
  double getTorque() override;

  /**
   * Gets the voltage delivered to the motor in millivolts.
   *
   * @return The motor's voltage in V or `PROS_ERR_F` if the operation failed, setting errno.
   */
  std::int32_t getVoltage() override;

  /******************************************************************************/
  /**                      Motor configuration functions                       **/
  /**                                                                          **/
  /**  These functions allow programmers to configure the behavior of motors   **/
  /******************************************************************************/

  /**
   * Sets one of AbstractMotor::brakeMode to the motor.
   *
   * This function uses the following values of errno when an error state is reached:
   * EACCES - Another resource is currently trying to access the port.
   *
   * @param imode The new motor brake mode to set for the motor.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setBrakeMode(AbstractMotor::brakeMode imode) override;

  /**
   * Gets the brake mode that was set for the motor.
   *
   * @return One of brakeMode, according to what was set for the motor, or brakeMode::invalid if the
   * operation failed, setting errno.
   */
  brakeMode getBrakeMode() override;

  /**
   * Sets the current limit for the motor in mA.
   *
   * This function uses the following values of errno when an error state is reached:
   * EACCES - Another resource is currently trying to access the port.
   *
   * @param ilimit The new current limit in mA.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setCurrentLimit(std::int32_t ilimit) override;

  /**
   * Gets the current limit for the motor in mA. The default value is `2500` mA.
   *
   * @return The motor's current limit in mA or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t getCurrentLimit() override;

  /**
   * Sets one of AbstractMotor::encoderUnits for the motor encoder.
   *
   * @param iunits The new motor encoder units.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setEncoderUnits(AbstractMotor::encoderUnits iunits) override;

  /**
   * Gets the encoder units that were set for the motor.
   *
   * @return One of encoderUnits according to what is set for the motor or encoderUnits::invalid if
   * the operation failed.
   */
  encoderUnits getEncoderUnits() override;

  /**
   * Sets one of AbstractMotor::gearset for the motor.
   *
   * @param igearset The new motor gearset.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setGearing(AbstractMotor::gearset igearset) override;

  /**
   * Gets the gearset that was set for the motor.
   *
   * @return One of gearset according to what is set for the motor, or `gearset::invalid` if the
   * operation failed.
   */
  gearset getGearing() override;

  /**
   * Sets the reverse flag for the motor. This will invert its movements and the values returned for
   * its position.
   *
   * @param ireverse True reverses the motor, false is default.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setReversed(bool ireverse) override;

  /**
   * Sets the voltage limit for the motor in Volts.
   *
   * @param ilimit The new voltage limit in Volts.
   * @return 1 if the operation was successful or `PROS_ERR` if the operation failed, setting errno.
   */
  std::int32_t setVoltageLimit(std::int32_t ilimit) override;

  /**
   * Writes the value of the controller output. This method might be automatically called in another
   * thread by the controller. The range of input values is expected to be `[-1, 1]`.
   *
   * @param ivalue the controller's output in the range `[-1, 1]`
   */
  void controllerSet(double ivalue) override;

  /**
   * Gets the number of motors in the motor group.
   *
   * @return size_t
   */
  size_t getSize();

  /**
   * Get the encoder associated with the first motor in this group.
   *
   * @return The encoder for the motor at index `0`.
   */
  std::shared_ptr<ContinuousRotarySensor> getEncoder() override;

  /**
   * Get the encoder associated with this motor.
   *
   * @param index The index in `motors` to get the encoder from.
   * @return The encoder for the motor at `index`.
   */
  virtual std::shared_ptr<ContinuousRotarySensor> getEncoder(std::size_t index);

  protected:
  std::vector<std::shared_ptr<AbstractMotor>> motors;
};
} // namespace okapi
