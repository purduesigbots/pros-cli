/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/impl/util/timeUtilFactory.hpp"

namespace okapi {
/**
 * A TimeUtilFactory that supplies the SettledUtil parameters passed in the constructor to every
 * new TimeUtil instance.
 */
class ConfigurableTimeUtilFactory : public TimeUtilFactory {
  public:
  ConfigurableTimeUtilFactory(double iatTargetError = 50,
                              double iatTargetDerivative = 5,
                              const QTime &iatTargetTime = 250_ms);

  /**
   * Creates a TimeUtil with the SettledUtil parameters specified in the constructor by
   * delegating to TimeUtilFactory::withSettledUtilParams.
   *
   * @return A TimeUtil with the SettledUtil parameters specified in the constructor.
   */
  TimeUtil create() override;

  private:
  double atTargetError;
  double atTargetDerivative;
  QTime atTargetTime;
};
} // namespace okapi
