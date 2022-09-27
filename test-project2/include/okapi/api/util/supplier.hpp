/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include <functional>

namespace okapi {
/**
 * A supplier of instances of T.
 *
 * @tparam T the type to supply
 */
template <typename T> class Supplier {
  public:
  explicit Supplier(std::function<T(void)> ifunc) : func(ifunc) {
  }

  virtual ~Supplier() = default;

  /**
   * Get an instance of type T. This is usually a new instance, but it does not have to be.
   * @return an instance of T
   */
  T get() const {
    return func();
  }

  protected:
  std::function<T(void)> func;
};
} // namespace okapi
