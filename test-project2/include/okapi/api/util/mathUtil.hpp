/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/device/motor/abstractMotor.hpp"
#include <algorithm>
#include <cstdint>
#include <math.h>
#include <type_traits>

namespace okapi {
/**
 * Converts inches to millimeters.
 */
static constexpr double inchToMM = 25.4;

/**
 * Converts millimeters to inches.
 */
static constexpr double mmToInch = 0.0393700787;

/**
 * Converts degrees to radians.
 */
static constexpr double degreeToRadian = 0.01745329252;

/**
 * Converts radians to degrees.
 */
static constexpr double radianToDegree = 57.2957795;

/**
 * The ticks per rotation of the 393 IME with torque gearing.
 */
static constexpr double imeTorqueTPR = 627.2;

/**
 * The ticks per rotation of the 393 IME with speed gearing.
 */
static constexpr std::int32_t imeSpeedTPR = 392;

/**
 * The ticks per rotation of the 393 IME with turbo gearing.
 */
static constexpr double imeTurboTPR = 261.333;

/**
 * The ticks per rotation of the 269 IME.
 */
static constexpr double ime269TPR = 240.448;

/**
 * The ticks per rotation of the V5 motor with a red gearset.
 */
static constexpr std::int32_t imev5RedTPR = 1800;

/**
 * The ticks per rotation of the V5 motor with a green gearset.
 */
static constexpr std::int32_t imev5GreenTPR = 900;

/**
 * The ticks per rotation of the V5 motor with a blue gearset.
 */
static constexpr std::int32_t imev5BlueTPR = 300;

/**
 * The ticks per rotation of the red quadrature encoders.
 */
static constexpr std::int32_t quadEncoderTPR = 360;

/**
 * The value of pi.
 */
static constexpr double pi = 3.1415926535897932;

/**
 * The value of pi divided by 2.
 */
static constexpr double pi2 = 1.5707963267948966;

/**
 * The conventional value of gravity of Earth.
 */
static constexpr double gravity = 9.80665;

/**
 * Same as PROS_ERR.
 */
static constexpr auto OKAPI_PROS_ERR = INT32_MAX;

/**
 * Same as PROS_ERR_F.
 */
static constexpr auto OKAPI_PROS_ERR_F = INFINITY;

/**
 * The maximum voltage that can be sent to V5 motors.
 */
static constexpr double v5MotorMaxVoltage = 12000;

/**
 * The polling frequency of V5 motors in milliseconds.
 */
static constexpr std::int8_t motorUpdateRate = 10;

/**
 * The polling frequency of the ADI ports in milliseconds.
 */
static constexpr std::int8_t adiUpdateRate = 10;

/**
 * Integer power function. Computes `base^expo`.
 *
 * @param base The base.
 * @param expo The exponent.
 * @return `base^expo`.
 */
constexpr double ipow(const double base, const int expo) {
  return (expo == 0) ? 1
         : expo == 1 ? base
         : expo > 1  ? ((expo & 1) ? base * ipow(base, expo - 1)
                                   : ipow(base, expo / 2) * ipow(base, expo / 2))
                     : 1 / ipow(base, -expo);
}

/**
 * Cuts out a range from the number. The new range of the input number will be
 * `(-inf, min]U[max, +inf)`. If value sits equally between `min` and `max`, `max` will be returned.
 *
 * @param value The number to bound.
 * @param min The lower bound of range.
 * @param max The upper bound of range.
 * @return The remapped value.
 */
constexpr double cutRange(const double value, const double min, const double max) {
  const double middle = max - ((max - min) / 2);

  if (value > min && value < middle) {
    return min;
  } else if (value <= max && value >= middle) {
    return max;
  }

  return value;
}

/**
 * Deadbands a range of the number. Returns the input value, or `0` if it is in the range `[min,
 * max]`.
 *
 * @param value The number to deadband.
 * @param min The lower bound of deadband.
 * @param max The upper bound of deadband.
 * @return The input value or `0` if it is in the range `[min, max]`.
 */
constexpr double deadband(const double value, const double min, const double max) {
  return std::clamp(value, min, max) == value ? 0 : value;
}

/**
 * Remap a value in the range `[oldMin, oldMax]` to the range `[newMin, newMax]`.
 *
 * @param value The value in the old range.
 * @param oldMin The old range lower bound.
 * @param oldMax The old range upper bound.
 * @param newMin The new range lower bound.
 * @param newMax The new range upper bound.
 * @return The input value in the new range `[newMin, newMax]`.
 */
constexpr double remapRange(const double value,
                            const double oldMin,
                            const double oldMax,
                            const double newMin,
                            const double newMax) {
  return (value - oldMin) * ((newMax - newMin) / (oldMax - oldMin)) + newMin;
}

/**
 * Converts an enum to its value type.
 *
 * @param e The enum value.
 * @return The corresponding value.
 */
template <typename E> constexpr auto toUnderlyingType(const E e) noexcept {
  return static_cast<std::underlying_type_t<E>>(e);
}

/**
 * Converts a bool to a sign.
 *
 * @param b The bool.
 * @return True corresponds to `1` and false corresponds to `-1`.
 */
constexpr auto boolToSign(const bool b) noexcept {
  return b ? 1 : -1;
}

/**
 * Computes `lhs mod rhs` using Euclidean division. C's `%` symbol computes the remainder, not
 * modulus.
 *
 * @param lhs The left-hand side.
 * @param rhs The right-hand side.
 * @return `lhs` mod `rhs`.
 */
constexpr long modulus(const long lhs, const long rhs) noexcept {
  return ((lhs % rhs) + rhs) % rhs;
}

/**
 * Converts a gearset to its TPR.
 *
 * @param igearset The gearset.
 * @return The corresponding TPR.
 */
constexpr std::int32_t gearsetToTPR(const AbstractMotor::gearset igearset) noexcept {
  switch (igearset) {
  case AbstractMotor::gearset::red:
    return imev5RedTPR;
  case AbstractMotor::gearset::green:
    return imev5GreenTPR;
  case AbstractMotor::gearset::blue:
  case AbstractMotor::gearset::invalid:
  default:
    return imev5BlueTPR;
  }
}

/**
 * Maps ADI port numbers/chars to numbers:
 * ```
 * when (port) {
 *   in ['a', 'h'] -> [1, 8]
 *   in ['A', 'H'] -> [1, 8]
 *   else -> [1, 8]
 * }
 * ```
 *
 * @param port The ADI port number or char.
 * @return An equivalent ADI port number.
 */
constexpr std::int8_t transformADIPort(const std::int8_t port) {
  if (port >= 'a' && port <= 'h') {
    return port - ('a' - 1);
  } else if (port >= 'A' && port <= 'H') {
    return port - ('A' - 1);
  } else {
    return port;
  }
}
} // namespace okapi
