/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/filter/filter.hpp"
#include <memory>

namespace okapi {
/**
 * A ControllerInput with a filter built in.
 *
 * @tparam InputType the type of the ControllerInput
 * @tparam FilterType the type of the Filter
 */
template <typename InputType, typename FilterType>
class FilteredControllerInput : public ControllerInput<double> {
  public:
  /**
   * A filtered controller input. Applies a filter to the controller input. Useful if you want to
   * place a filter between a control input and a control loop.
   *
   * @param iinput ControllerInput type
   * @param ifilter Filter type
   */
  FilteredControllerInput(std::unique_ptr<ControllerInput<InputType>> iinput,
                          std::unique_ptr<FilterType> ifilter)
    : input(std::move(iinput)), filter(std::move(ifilter)) {
  }

  /**
   * Gets the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return the current filtered sensor value.
   */
  double controllerGet() override {
    return filter->filter(input->controllerGet());
  }

  protected:
  std::unique_ptr<ControllerInput<InputType>> input;
  std::unique_ptr<FilterType> filter;
};
} // namespace okapi
