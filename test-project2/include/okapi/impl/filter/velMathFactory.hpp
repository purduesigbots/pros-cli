/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/velMath.hpp"
#include <memory>

namespace okapi {
class VelMathFactory {
  public:
  /**
   * Velocity math helper. Calculates filtered velocity. Throws a std::invalid_argument exception
   * if iticksPerRev is zero. Averages the last two readings.
   *
   * @param iticksPerRev The number of ticks per revolution.
   * @param isampleTime The minimum time between samples.
   * @param ilogger The logger this instance will log to.
   */
  static VelMath create(double iticksPerRev,
                        QTime isampleTime = 0_ms,
                        const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity math helper. Calculates filtered velocity. Throws a std::invalid_argument exception
   * if iticksPerRev is zero. Averages the last two readings.
   *
   * @param iticksPerRev The number of ticks per revolution.
   * @param isampleTime The minimum time between samples.
   * @param ilogger The logger this instance will log to.
   */
  static std::unique_ptr<VelMath>
  createPtr(double iticksPerRev,
            QTime isampleTime = 0_ms,
            const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity math helper. Calculates filtered velocity. Throws a std::invalid_argument exception
   * if iticksPerRev is zero.
   *
   * @param iticksPerRev The number of ticks per revolution.
   * @param ifilter The filter used for filtering the calculated velocity.
   * @param isampleTime The minimum time between samples.
   * @param ilogger The logger this instance will log to.
   */
  static VelMath create(double iticksPerRev,
                        std::unique_ptr<Filter> ifilter,
                        QTime isampleTime = 0_ms,
                        const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * Velocity math helper. Calculates filtered velocity. Throws a std::invalid_argument exception
   * if iticksPerRev is zero.
   *
   * @param iticksPerRev The number of ticks per revolution.
   * @param ifilter The filter used for filtering the calculated velocity.
   * @param isampleTime The minimum time between samples.
   * @param ilogger The logger this instance will log to.
   */
  static std::unique_ptr<VelMath>
  createPtr(double iticksPerRev,
            std::unique_ptr<Filter> ifilter,
            QTime isampleTime = 0_ms,
            const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());
};
} // namespace okapi
