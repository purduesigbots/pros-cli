/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/filter/filter.hpp"
#include "okapi/api/util/mathUtil.hpp"

namespace okapi {
class EKFFilter : public Filter {
  public:
  /**
   * One dimensional extended Kalman filter. The default arguments should work fine for most signal
   * filtering. It won't hurt to graph your signal and the filtered result, and check if the filter
   * is doing its job.
   *
   * Q is the covariance of the process noise and R is the
   * covariance of the observation noise. The default values for Q and R should be a modest balance
   * between trust in the sensor and FIR filtering.
   *
   * Think of R as how noisy your sensor is. Its value can be found mathematically by computing the
   * standard deviation of your sensor reading vs. "truth" (of course, "truth" is still an estimate;
   * try to calibrate your robot in a controlled setting where you can minimize the error in what
   * "truth" is).
   *
   * Think of Q as how noisy your model is. It decides how much "smoothing" the filter does and how
   * far it lags behind the true signal. This parameter is most often used as a "tuning" parameter
   * to adjust the response of the filter.
   *
   * @param iQ process noise covariance
   * @param iR measurement noise covariance
   */
  explicit EKFFilter(double iQ = 0.0001, double iR = ipow(0.2, 2));

  /**
   * Filters a value, like a sensor reading. Assumes the control input is zero.
   *
   * @param ireading new measurement
   * @return filtered result
   */
  double filter(double ireading) override;

  /**
   * Filters a reading with a control input.
   *
   * @param ireading new measurement
   * @param icontrol control input
   * @return filtered result
   */
  virtual double filter(double ireading, double icontrol);

  /**
   * Returns the previous output from filter.
   *
   * @return the previous output from filter
   */
  double getOutput() const override;

  protected:
  const double Q, R;
  double xHat = 0;
  double xHatPrev = 0;
  double xHatMinus = 0;
  double P = 0;
  double Pprev = 1;
  double Pminus = 0;
  double K = 0;
};
} // namespace okapi
