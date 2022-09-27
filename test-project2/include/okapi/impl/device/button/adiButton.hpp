/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/device/button/buttonBase.hpp"

namespace okapi {
class ADIButton : public ButtonBase {
  public:
  /**
   * A button in an ADI port.
   *
   * ```cpp
   * auto btn = ADIButton('A', false);
   * auto invertedBtn = ADIButton('A', true);
   * ```
   *
   * @param iport The ADI port number (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   * @param iinverted Whether the button is inverted (``true`` meaning default pressed and ``false``
   * meaning default not pressed).
   */
  ADIButton(std::uint8_t iport, bool iinverted = false);

  /**
   * A button in an ADI port.
   *
   * ```cpp
   * auto btn = ADIButton({1, 'A'}, false);
   * auto invertedBtn = ADIButton({1, 'A'}, true);
   * ```
   *
   * @param iports The ports the button is plugged in to in the order ``{smart port, button port}``.
   * The smart port is the smart port number (``[1, 21]``). The button port is the ADI port number
   * (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   * @param iinverted Whether the button is inverted (``true`` meaning default pressed and ``false``
   * meaning default not pressed).
   */
  ADIButton(std::pair<std::uint8_t, std::uint8_t> iports, bool iinverted = false);

  protected:
  std::uint8_t smartPort;
  std::uint8_t port;

  virtual bool currentlyPressed() override;
};
} // namespace okapi
