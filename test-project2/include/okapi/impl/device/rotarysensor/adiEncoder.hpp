/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/device/rotarysensor/continuousRotarySensor.hpp"

namespace okapi {
class ADIEncoder : public ContinuousRotarySensor {
  public:
  /**
   * An encoder in an ADI port.
   *
   * ```cpp
   * auto enc = ADIEncoder('A', 'B', false);
   * auto reversedEnc = ADIEncoder('A', 'B', true);
   * ```
   *
   * @param iportTop The "top" wire from the encoder with the removable cover side up. This must be
   * in port ``1``, ``3``, ``5``, or ``7`` (``A``, ``C``, ``E``, or ``G``).
   * @param iportBottom The "bottom" wire from the encoder. This must be in port ``2``, ``4``,
   * ``6``, or ``8`` (``B``, ``D``, ``F``, or ``H``).
   * @param ireversed Whether the encoder is reversed.
   */
  ADIEncoder(std::uint8_t iportTop, std::uint8_t iportBottom, bool ireversed = false);

  /**
   * An encoder in an ADI port.
   *
   * ```cpp
   * auto enc = ADIEncoder({1, 'A', 'B'}, false);
   * auto reversedEnc = ADIEncoder({1, 'A', 'B'}, true);
   * ```
   *
   * @param iports The ports the encoder is plugged in to in the order ``{smart port, top port,
   * bottom port}``. The smart port is the smart port number (``[1, 21]``). The top port is the
   * "top" wire from the encoder with the removable cover side up. This must be in port ``1``,
   * ``3``, ``5``, or
   * ``7`` (``A``, ``C``, ``E``, or ``G``). The bottom port is the "bottom" wire from the encoder.
   * This must be in port ``2``, ``4``, ``6``, or ``8`` (``B``, ``D``, ``F``, or ``H``).
   * @param ireversed Whether the encoder is reversed.
   */
  ADIEncoder(std::tuple<std::uint8_t, std::uint8_t, std::uint8_t> iports, bool ireversed = false);

  /**
   * Get the current sensor value.
   *
   * @return the current sensor value, or `PROS_ERR` on a failure.
   */
  virtual double get() const override;

  /**
   * Reset the sensor to zero.
   *
   * @return `1` on success, `PROS_ERR` on fail
   */
  virtual std::int32_t reset() override;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current sensor value, or `PROS_ERR` on a failure.
   */
  virtual double controllerGet() override;

  protected:
  pros::c::ext_adi_encoder_t enc;
};
} // namespace okapi
