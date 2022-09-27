/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/coreProsAPI.hpp"
#include <valarray>

namespace okapi {
/**
 * A version of the ChassisModel that only supports read methods, such as querying sensor values.
 * This class does not let you write to motors, so it supports having multiple owners and as a
 * result copying is enabled.
 */
class ReadOnlyChassisModel {
  public:
  virtual ~ReadOnlyChassisModel() = default;

  /**
   * Read the sensors.
   *
   * @return sensor readings (format is implementation dependent)
   */
  virtual std::valarray<std::int32_t> getSensorVals() const = 0;
};
} // namespace okapi
