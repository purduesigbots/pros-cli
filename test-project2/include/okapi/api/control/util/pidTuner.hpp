/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/control/controllerOutput.hpp"
#include "okapi/api/control/iterative/iterativePosPidController.hpp"
#include "okapi/api/units/QTime.hpp"
#include "okapi/api/util/logging.hpp"
#include "okapi/api/util/timeUtil.hpp"
#include <memory>
#include <vector>

namespace okapi {
class PIDTuner {
  public:
  struct Output {
    double kP, kI, kD;
  };

  PIDTuner(const std::shared_ptr<ControllerInput<double>> &iinput,
           const std::shared_ptr<ControllerOutput<double>> &ioutput,
           const TimeUtil &itimeUtil,
           QTime itimeout,
           std::int32_t igoal,
           double ikPMin,
           double ikPMax,
           double ikIMin,
           double ikIMax,
           double ikDMin,
           double ikDMax,
           std::size_t inumIterations = 5,
           std::size_t inumParticles = 16,
           double ikSettle = 1,
           double ikITAE = 2,
           const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  virtual ~PIDTuner();

  virtual Output autotune();

  protected:
  static constexpr double inertia = 0.5;   // Particle inertia
  static constexpr double confSelf = 1.1;  // Self confidence
  static constexpr double confSwarm = 1.2; // Particle swarm confidence
  static constexpr int increment = 5;
  static constexpr int divisor = 5;
  static constexpr QTime loopDelta = 10_ms; // NOLINT

  struct Particle {
    double pos, vel, best;
  };

  struct ParticleSet {
    Particle kP, kI, kD;
    double bestError;
  };

  std::shared_ptr<Logger> logger;
  TimeUtil timeUtil;
  std::shared_ptr<ControllerInput<double>> input;
  std::shared_ptr<ControllerOutput<double>> output;

  const QTime timeout;
  const std::int32_t goal;
  const double kPMin;
  const double kPMax;
  const double kIMin;
  const double kIMax;
  const double kDMin;
  const double kDMax;
  const std::size_t numIterations;
  const std::size_t numParticles;
  const double kSettle;
  const double kITAE;
};
} // namespace okapi
