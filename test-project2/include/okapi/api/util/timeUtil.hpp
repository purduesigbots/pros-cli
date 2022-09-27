/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/util/settledUtil.hpp"
#include "okapi/api/util/abstractRate.hpp"
#include "okapi/api/util/abstractTimer.hpp"
#include "okapi/api/util/supplier.hpp"

namespace okapi {
/**
 * Utility class for holding an AbstractTimer, AbstractRate, and SettledUtil together in one
 * class since they are commonly used together.
 */
class TimeUtil {
  public:
  TimeUtil(const Supplier<std::unique_ptr<AbstractTimer>> &itimerSupplier,
           const Supplier<std::unique_ptr<AbstractRate>> &irateSupplier,
           const Supplier<std::unique_ptr<SettledUtil>> &isettledUtilSupplier);

  std::unique_ptr<AbstractTimer> getTimer() const;

  std::unique_ptr<AbstractRate> getRate() const;

  std::unique_ptr<SettledUtil> getSettledUtil() const;

  Supplier<std::unique_ptr<AbstractTimer>> getTimerSupplier() const;

  Supplier<std::unique_ptr<AbstractRate>> getRateSupplier() const;

  Supplier<std::unique_ptr<SettledUtil>> getSettledUtilSupplier() const;

  protected:
  Supplier<std::unique_ptr<AbstractTimer>> timerSupplier;
  Supplier<std::unique_ptr<AbstractRate>> rateSupplier;
  Supplier<std::unique_ptr<SettledUtil>> settledUtilSupplier;
};
} // namespace okapi
