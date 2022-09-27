/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/async/asyncController.hpp"
#include <memory>

namespace okapi {
template <typename Input, typename Output>
class AsyncVelocityController : virtual public AsyncController<Input, Output> {};
} // namespace okapi
