/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _MATH_UTILS_HPP_
#define _MATH_UTILS_HPP_

#include <cmath>
#include <iostream>

namespace squiggles {
/**
 * Returns the sign value of the given value.
 *
 * @return 1 if the value is positive, -1 if the value is negative, and 0 if
 *         the value is 0.
 */
template <class T> inline int sgn(T v) {
  return (v > T(0)) - (v < T(0));
}

inline bool
nearly_equal(const double& a, const double& b, double epsilon = 1e-5) {
  return std::fabs(a - b) < epsilon;
}
} // namespace squiggles

namespace std {
// Copied from https://github.com/emsr/cxx_linear
template <typename _Float>
constexpr std::enable_if_t<
  std::is_floating_point_v<_Float> &&
    __cplusplus <= 201703L, // Only defines this function if C++ standard < 20
  _Float>
lerp(_Float __a, _Float __b, _Float __t) {
  if (std::isnan(__a) || std::isnan(__b) || std::isnan(__t))
    return std::numeric_limits<_Float>::quiet_NaN();
  else if ((__a <= _Float{0} && __b >= _Float{0}) ||
           (__a >= _Float{0} && __b <= _Float{0}))
  // ab <= 0 but product could overflow.
#ifndef FMA
    return __t * __b + (_Float{1} - __t) * __a;
#else
    return std::fma(__t, __b, (_Float{1} - __t) * __a);
#endif
  else if (__t == _Float{1})
    return __b;
  else { // monotonic near t == 1.
#ifndef FMA
    const auto __x = __a + __t * (__b - __a);
#else
    const auto __x = std::fma(__t, __b - __a, __a);
#endif
    return (__t > _Float{1}) == (__b > __a) ? std::max(__b, __x)
                                            : std::min(__b, __x);
  }
}
} // namespace std
#endif