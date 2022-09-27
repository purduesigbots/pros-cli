/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/composableFilter.hpp"
#include "okapi/api/units/QAngularAcceleration.hpp"
#include "okapi/api/units/QAngularSpeed.hpp"
#include "okapi/api/units/QTime.hpp"
#include "okapi/api/util/abstractTimer.hpp"
#include "okapi/api/util/logging.hpp"
#include <memory>

namespace okapi {
class VelMath {
  public:
  /**
   * Velocity math helper. Calculates filtered velocity. Throws a `std::invalid_argument` exception
   * if `iticksPerRev` is zero.
   *
   * @param iticksPerRev The number of ticks per revolution (or whatever units you are using).
   * @param ifilter The filter used for filtering the calculated velocity.
   * @param isampleTime The minimum time between velocity measurements.
   * @param ilogger The logger this instance will log to.
   */
  VelMath(double iticksPerRev,
          std::unique_ptr<Filter> ifilter,
          QTime isampleTime,
          std::unique_ptr<AbstractTimer> iloopDtTimer,
          std::shared_ptr<Logger> ilogger = Logger::getDefaultLogger());

  virtual ~VelMath();

  /**
   * Calculates the current velocity and acceleration. Returns the (filtered) velocity.
   *
   * @param inewPos The new position measurement.
   * @return The new velocity estimate.
   */
  virtual QAngularSpeed step(double inewPos);

  /**
   * Sets ticks per revolution (or whatever units you are using). Throws a `std::invalid_argument`
   * exception if iticksPerRev is zero.
   *
   * @param iTPR The number of ticks per revolution.
   */
  virtual void setTicksPerRev(double iTPR);

  /**
   * @return The last calculated velocity.
   */
  virtual QAngularSpeed getVelocity() const;

  /**
   * @return The last calculated acceleration.
   */
  virtual QAngularAcceleration getAccel() const;

  protected:
  std::shared_ptr<Logger> logger;
  QAngularSpeed vel{0_rpm};
  QAngularSpeed lastVel{0_rpm};
  QAngularAcceleration accel{0.0};
  double lastPos{0};
  double ticksPerRev;

  QTime sampleTime;
  std::unique_ptr<AbstractTimer> loopDtTimer;
  std::unique_ptr<Filter> filter;
};
} // namespace okapi
