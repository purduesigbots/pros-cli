/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/util/pidTuner.hpp"
#include <memory>

namespace okapi {
class PIDTunerFactory {
  public:
  static PIDTuner create(const std::shared_ptr<ControllerInput<double>> &iinput,
                         const std::shared_ptr<ControllerOutput<double>> &ioutput,
                         QTime itimeout,
                         std::int32_t igoal,
                         double ikPMin,
                         double ikPMax,
                         double ikIMin,
                         double ikIMax,
                         double ikDMin,
                         double ikDMax,
                         std::int32_t inumIterations = 5,
                         std::int32_t inumParticles = 16,
                         double ikSettle = 1,
                         double ikITAE = 2,
                         const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  static std::unique_ptr<PIDTuner>
  createPtr(const std::shared_ptr<ControllerInput<double>> &iinput,
            const std::shared_ptr<ControllerOutput<double>> &ioutput,
            QTime itimeout,
            std::int32_t igoal,
            double ikPMin,
            double ikPMax,
            double ikIMin,
            double ikIMax,
            double ikDMin,
            double ikDMax,
            std::int32_t inumIterations = 5,
            std::int32_t inumParticles = 16,
            double ikSettle = 1,
            double ikITAE = 2,
            const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());
};
} // namespace okapi
