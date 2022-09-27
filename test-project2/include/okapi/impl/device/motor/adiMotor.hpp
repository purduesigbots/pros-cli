/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/util/logging.hpp"

namespace okapi {
class ADIMotor : public ControllerOutput<double> {
  public:
  /**
   * A motor in an ADI port.
   *
   * ```cpp
   * auto mtr = ADIMotor('A');
   * auto reversedMtr = ADIMotor('A', true);
   * ```
   *
   * @param iport The ADI port number (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   * @param ireverse Whether the motor is reversed.
   * @param logger The logger that initialization warnings will be logged to.
   */
  ADIMotor(std::uint8_t iport,
           bool ireverse = false,
           const std::shared_ptr<Logger> &logger = Logger::getDefaultLogger());

  /**
   * A motor in an ADI port.
   *
   * ```cpp
   * auto mtr = ADIMotor({1, 'A'}, false);
   * auto reversedMtr = ADIMotor({1, 'A'}, true);
   * ```
   *
   * @param iports The ports the motor is plugged in to in the order ``{smart port, motor port}``.
   * The smart port is the smart port number (``[1, 21]``). The motor port is the ADI port number
   * (``[1, 8]``, ``[a, h]``, ``[A, H]``).
   * @param ireverse Whether the motor is reversed.
   * @param logger The logger that initialization warnings will be logged to.
   */
  ADIMotor(std::pair<std::uint8_t, std::uint8_t> iports,
           bool ireverse = false,
           const std::shared_ptr<Logger> &logger = Logger::getDefaultLogger());

  /**
   * Set the voltage to the motor.
   *
   * @param ivoltage voltage in the range [-127, 127].
   */
  virtual void moveVoltage(std::int8_t ivoltage) const;

  /**
   * Writes the value of the controller output. This method might be automatically called in another
   * thread by the controller. The range of input values is expected to be [-1, 1].
   *
   * @param ivalue the controller's output in the range [-1, 1]
   */
  void controllerSet(double ivalue) override;

  protected:
  std::uint8_t smartPort;
  std::uint8_t port;
  std::int8_t reversed;
};
} // namespace okapi
