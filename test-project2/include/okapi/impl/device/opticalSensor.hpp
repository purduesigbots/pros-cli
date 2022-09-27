/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "api.h"
#include "okapi/api/control/controllerInput.hpp"
#include "okapi/api/filter/passthroughFilter.hpp"
#include <memory>

namespace okapi {
enum class OpticalSensorOutput {
  hue,        ///< The color.
  saturation, ///< The color's intensity relative to its brightness.
  brightness  ///< The amount of light.
};

class OpticalSensor : public ControllerInput<double> {
  public:
  /**
   * An optical sensor on a V5 port.
   *
   * ```cpp
   * auto osHue = OpticalSensor(1);
   * auto osSat = OpticalSensor(1, OpticalSensorOutput::saturation);
   * ```
   *
   * @param iport The V5 port the device uses.
   * @param ioutput Which sensor output to return from (@ref okapi::OpticalSensor::get).
   * @param idisableGestures Whether to automatically disable the gesture sensor. Typically, the
   * gesture sensor should be disabled unless you are going to use gestures because the optical
   * sensor does not update color information while detecting a gesture.
   * @param ifilter The filter to use to filter the sensor output. Only the selected output (via
   * ``ioutput``) is filtered; the other outputs are untouched.
   */
  OpticalSensor(std::uint8_t iport,
                OpticalSensorOutput ioutput = OpticalSensorOutput::hue,
                bool idisableGestures = true,
                std::unique_ptr<Filter> ifilter = std::make_unique<PassthroughFilter>());

  virtual ~OpticalSensor() = default;

  /**
   * Get the current filtered value of the selected output (configured by the constructor).
   *
   * @return The current filtered value of the selected output (configured by the constructor).
   */
  double get();

  /**
   * Get the current hue value in the range ``[0, 360)``.
   *
   * @return The current hue value in the range ``[0, 360)``.
   */
  double getHue() const;

  /**
   * Get the current brightness value in the range ``[0, 1]``.
   *
   * @return The current brightness value in the range ``[0, 1]``.
   */
  double getBrightness() const;

  /**
   * Get the current saturation value in the range ``[0, 1]``.
   *
   * @return The current saturation value in the range ``[0, 1]``.
   */
  double getSaturation() const;

  /**
   * Get the PWM value of the white LED in the range ``[0, 100]``.
   *
   * @return The PWM value of the white LED in the range ``[0, 100]`` or ``PROS_ERR`` if the
   * operation failed, setting ``errno``.
   */
  int32_t getLedPWM() const;

  /**
   * Set the PWM value of the white LED in the range ``[0, 100]``.
   *
   * @param value The PWM value in the range ``[0, 100]``.
   * @return ``1`` if the operation was successful or ``PROS_ERR`` if the operation failed, setting
   * ``errno``.
   */
  int32_t setLedPWM(std::uint8_t ivalue) const;

  /**
   * Get the current proximity value in the range ``[0, 255]``. This is not available if gestures
   * are being detected.
   *
   * @return The current proximity value in the range ``[0, 255]``.
   */
  int32_t getProximity() const;

  /**
   * Get the processed RGBC data from the sensor.
   *
   * @return The RGBC value if the operation was successful. If the operation failed, all field are
   * set to ``PROS_ERR`` and ``errno`` is set.
   */
  pros::c::optical_rgb_s_t getRGB() const;

  /**
   * Get the sensor value for use in a control loop. This method might be automatically called in
   * another thread by the controller.
   *
   * @return The same as [get](@ref okapi::OpticalSensor::get).
   */
  double controllerGet() override;

  /**
   * Enable gestures.
   *
   * @return ``1`` if the operation was successful or ``PROS_ERR`` if the operation failed, setting
   * ``errno``.
   */
  int32_t enableGestures() const;

  /**
   * Disable gestures.
   *
   * @return ``1`` if the operation was successful or ``PROS_ERR`` if the operation failed, setting
   * ``errno``.
   */
  int32_t disableGestures() const;

  protected:
  std::uint8_t port;
  OpticalSensorOutput output;
  std::unique_ptr<Filter> filter;

  /**
   * Gets the output directly from the sensor using the selected output.
   */
  double getSelectedOutput();
};
} // namespace okapi
