/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/util/controllerRunner.hpp"
#include "okapi/impl/util/timeUtilFactory.hpp"

namespace okapi {
template <typename Input, typename Output> class ControllerRunnerFactory {
  public:
  /**
   * A utility class that runs a closed-loop controller.
   *
   * @param ilogger The logger this instance will log to.
   * @return
   */
  static ControllerRunner<Input, Output>
  create(const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger()) {
    return ControllerRunner<Input, Output>(TimeUtilFactory::createDefault(), ilogger);
  }
};
} // namespace okapi
