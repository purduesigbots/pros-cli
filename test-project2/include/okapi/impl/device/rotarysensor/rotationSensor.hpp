/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"

namespace okapi {
class RotationSensor : public ContinuousRotarySensor {
  public:
  /**
   * A rotation sensor in a V5 port.
   *
   * ```cpp
   * auto r = RotationSensor(1);
   * auto reversedR = RotationSensor(1, true);
   * ```
   *
   * @param iport The V5 port the device uses.
   * @param ireversed Whether the sensor is reversed. This will set the reversed state in the
   * kernel.
   */
  RotationSensor(std::uint8_t iport, bool ireversed = false);

  /**
   * Get the current rotation in degrees.
   *
   * @return The current rotation in degrees or ``PROS_ERR_F`` if the operation failed, setting
   * ``errno``.
   */
  double get() const override;

  /**
   * Reset the sensor to zero.
   *
   * @return ``1`` if the operation was successful or ``PROS_ERR`` if the operation failed, setting
   * ``errno``.
   */
  std::int32_t reset() override;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return The same as [get](@ref okapi::RotationSensor::get).
   */
  double controllerGet() override;

  /**
   * Get the current rotational velocity estimate in degrees per second.
   *
   * @return The current rotational velocity estimate in degrees per second or ``PROS_ERR_F`` if the
   * operation failed, setting ``errno``.
   */
  double getVelocity() const;

  protected:
  std::uint8_t port;
  std::int8_t reversed{1};
};
} // namespace okapi
