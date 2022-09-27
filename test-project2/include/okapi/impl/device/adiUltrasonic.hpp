/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/filter/passthroughFilter.hpp"
#include <memory>

namespace okapi {
class ADIUltrasonic : public ControllerInput<double> {
  public:
  /**
   * An ultrasonic sensor in the ADI (3-wire) ports.
   *
   * ```cpp
   * auto ultra = ADIUltrasonic('A', 'B');
   * auto filteredUltra = ADIUltrasonic('A', 'B', std::make_unique<MedianFilter<5>>());
   * ```
   *
   * @param iportPing The port connected to the orange OUTPUT cable. This must be in port ``1``,
   * ``3``, ``5``, or ``7`` (``A``, ``C``, ``E``, or ``G``).
   * @param iportEcho The port connected to the yellow INPUT cable. This must be in the next highest
   * port following iportPing.
   * @param ifilter The filter to use for filtering the distance measurements.
   */
  ADIUltrasonic(std::uint8_t iportPing,
                std::uint8_t iportEcho,
                std::unique_ptr<Filter> ifilter = std::make_unique<PassthroughFilter>());

  /**
   * An ultrasonic sensor in the ADI (3-wire) ports.
   *
   * ```cpp
   * auto ultra = ADIUltrasonic({1, 'A', 'B'});
   * auto filteredUltra = ADIUltrasonic({1, 'A', 'B'}, std::make_unique<MedianFilter<5>>());
   * ```
   *
   * @param iports The ports the ultrasonic is plugged in to in the order ``{smart port, ping port,
   * echo port}``. The smart port is the smart port number (``[1, 21]``). The ping port is the port
   * connected to the orange OUTPUT cable. This must be in port ``1``, ``3``, ``5``, or ``7``
   * (``A``, ``C``, ``E``, or ``G``). The echo port is the port connected to the yellow INPUT cable.
   * This must be in the next highest port following the ping port.
   * @param ifilter The filter to use for filtering the distance measurements.
   */
  ADIUltrasonic(std::tuple<std::uint8_t, std::uint8_t, std::uint8_t> iports,
                std::unique_ptr<Filter> ifilter = std::make_unique<PassthroughFilter>());

  virtual ~ADIUltrasonic();

  /**
   * Returns the current filtered sensor value.
   *
   * @return current value
   */
  virtual double get();

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller. Calls get().
   */
  virtual double controllerGet() override;

  protected:
  pros::c::ext_adi_ultrasonic_t ultra;
  std::unique_ptr<Filter> filter;
};
} // namespace okapi
