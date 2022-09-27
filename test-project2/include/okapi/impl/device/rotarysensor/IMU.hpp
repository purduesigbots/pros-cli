/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"

namespace okapi {
enum class IMUAxes {
  z, ///< Yaw Axis
  y, ///< Pitch Axis
  x  ///< Roll Axis
};

class IMU : public ContinuousRotarySensor {
  public:
  /**
   * An inertial sensor on the given port. The IMU returns an angle about the selected axis in
   * degrees.
   *
   * ```cpp
   * auto imuZ = IMU(1);
   * auto imuX = IMU(1, IMUAxes::x);
   * ```
   *
   * @param iport The port number in the range ``[1, 21]``.
   * @param iaxis The axis of the inertial sensor to measure, default `IMUAxes::z`.
   */
  IMU(std::uint8_t iport, IMUAxes iaxis = IMUAxes::z);

  /**
   * Get the current rotation about the configured axis.
   *
   * @return The current sensor value or ``PROS_ERR``.
   */
  double get() const override;

  /**
   * Get the current sensor value remapped into the target range (``[-1800, 1800]`` by default).
   *
   * @param iupperBound The upper bound of the range.
   * @param ilowerBound The lower bound of the range.
   * @return The remapped sensor value.
   */
  double getRemapped(double iupperBound = 1800, double ilowerBound = -1800) const;

  /**
   * Get the current acceleration along the configured axis.
   *
   * @return The current sensor value or ``PROS_ERR``.
   */
  double getAcceleration() const;

  /**
   * Reset the rotation value to zero.
   *
   * @return ``1`` or ``PROS_ERR``.
   */
  std::int32_t reset() override;

  /**
   * Resets rotation value to desired value
   * For example, ``reset(0)`` will reset the sensor to zero.
   * But ``reset(90)`` will reset the sensor to 90 degrees.
   *
   * @param inewAngle desired reset value
   * @return ``1`` or ``PROS_ERR``.
   */
  std::int32_t reset(double inewAngle);

  /**
   * Calibrate the IMU. Resets the rotation value to zero. Calibration is expected to take two
   * seconds, but is bounded to five seconds.
   *
   * @return ``1`` or ``PROS_ERR``.
   */
  std::int32_t calibrate();

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return The current sensor value or ``PROS_ERR``.
   */
  double controllerGet() override;

  /**
   * @return Whether the IMU is calibrating.
   */
  bool isCalibrating() const;

  protected:
  std::uint8_t port;
  IMUAxes axis;
  double offset = 0;

  /**
   * Get the current rotation about the configured axis. The internal offset is not accounted for
   * or modified. This just reads from the sensor.
   *
   * @return The current sensor value or ``PROS_ERR``.
   */
  double readAngle() const;
};
} // namespace okapi
