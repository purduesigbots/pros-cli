/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/device/rotarysensor/rotarySensor.hpp"

namespace okapi {
class Potentiometer : public RotarySensor {
  public:
  /**
   * A potentiometer in an ADI port.
   *
   * ```cpp
   * auto pot = Potentiometer('A');
   * ```
   *
   * @param iport The ADI port number (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   */
  Potentiometer(std::uint8_t iport);

  /**
   * A potentiometer in an ADI port.
   *
   * ```cpp
   * auto pot = Potentiometer({1, 'A'});
   * ```
   *
   * @param iports The ports the potentiometer is plugged in to in the order ``{smart port,
   * potentiometer port}``. The smart port is the smart port number (``[1, 21]``). The potentiometer
   * port is the ADI port number (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   */
  Potentiometer(std::pair<std::uint8_t, std::uint8_t> iports);

  /**
   * Get the current sensor value.
   *
   * @return the current sensor value, or ``PROS_ERR`` on a failure.
   */
  virtual double get() const override;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current sensor value, or ``PROS_ERR`` on a failure.
   */
  virtual double controllerGet() override;

  protected:
  std::uint8_t smartPort;
  std::uint8_t port;
};
} // namespace okapi
