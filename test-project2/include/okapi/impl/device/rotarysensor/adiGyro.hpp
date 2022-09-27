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
class ADIGyro : public ContinuousRotarySensor {
  public:
  /**
   * A gyroscope on the given ADI port. If the port has not previously been configured as a gyro,
   * then the constructor will block for 1 second for calibration. The gyro measures in tenths of a
   * degree, so there are ``3600`` measurement points per revolution.
   *
   * ```cpp
   * auto gyro = ADIGyro('A');
   * ```
   *
   * @param iport The ADI port number (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   * @param imultiplier A value multiplied by the gyro heading value.
   */
  ADIGyro(std::uint8_t iport, double imultiplier = 1);

  /**
   * A gyroscope on the given ADI port. If the port has not previously been configured as a gyro,
   * then the constructor will block for 1 second for calibration. The gyro measures in tenths of a
   * degree, so there are 3600 measurement points per revolution.
   *
   * ```cpp
   * auto gyro = ADIGyro({1, 'A'}, 1);
   * ```
   *
   * Note to developers: Keep the default value on imultiplier so that users get an error if they do
   * ADIGyro({1, 'A'}). Without it, this calls the non-ext-adi constructor.
   *
   * @param iports The ports the gyro is plugged in to in the order ``{smart port, gyro port}``. The
   * smart port is the smart port number (``[1, 21]``). The gyro port is the ADI port number (``[1,
   * 8]``, ``[a, h]``, ``[A, H]``).
   * @param imultiplier A value multiplied by the gyro heading value.
   */
  ADIGyro(std::pair<std::uint8_t, std::uint8_t> iports, double imultiplier = 1);

  /**
   * Get the current sensor value.
   *
   * @return the current sensor value, or ``PROS_ERR`` on a failure.
   */
  double get() const override;

  /**
   * Get the current sensor value remapped into the target range (``[-1800, 1800]`` by default).
   *
   * @param iupperBound the upper bound of the range.
   * @param ilowerBound the lower bound of the range.
   * @return the remapped sensor value.
   */
  double getRemapped(double iupperBound = 1800, double ilowerBound = -1800) const;

  /**
   * Reset the sensor to zero.
   *
   * @return `1` on success, `PROS_ERR` on fail
   */
  std::int32_t reset() override;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current sensor value, or ``PROS_ERR`` on a failure.
   */
  double controllerGet() override;

  protected:
  pros::c::ext_adi_gyro_t gyro;
};
} // namespace okapi
