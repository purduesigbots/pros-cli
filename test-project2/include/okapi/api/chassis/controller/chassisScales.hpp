/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/RQuantity.hpp"
#include "okapi/api/util/logging.hpp"
#include <initializer_list>
#include <stdexcept>
#include <vector>

namespace okapi {
class ChassisScales {
  public:
  /**
   * The scales a ChassisController needs to do all of its closed-loop control. The first element is
   * the wheel diameter, the second element is the wheel track. For three-encoder configurations,
   * the length from the center of rotation to the middle wheel and the middle wheel diameter are
   * passed as the third and fourth elements.
   *
   * The wheel track is the center-to-center distance between the wheels (center-to-center
   * meaning the width between the centers of both wheels). For example, if you are using four inch
   * omni wheels and there are 11.5 inches between the centers of each wheel, you would call the
   * constructor like so:
   *   `ChassisScales scales({4_in, 11.5_in}, imev5GreenTPR); // imev5GreenTPR for a green gearset`
   *
   *                             Wheel diameter
   *
   *                              +-+      Center of rotation
   *                              | |      |
   *                              v v      +----------+ Length to middle wheel
   *                                       |          | from center of rotation
   *                     +--->    ===      |      === |
   *                     |         +       v       +  |
   *                     |        ++---------------++ |
   *                     |        |                 | v
   *       Wheel track   |        |                 |
   *                     |        |        x        |+|  <-- Middle wheel
   *                     |        |                 |
   *                     |        |                 |
   *                     |        ++---------------++
   *                     |         +               +
   *                     +--->    ===             ===
   *
   *
   * @param idimensions {wheel diameter, wheel track} or {wheel diameter, wheel track, length to
   * middle wheel, middle wheel diameter}.
   * @param itpr The ticks per revolution of the encoders.
   * @param ilogger The logger this instance will log to.
   */
  ChassisScales(const std::initializer_list<QLength> &idimensions,
                double itpr,
                const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  /**
   * The scales a ChassisController needs to do all of its closed-loop control. The first element is
   * the straight scale, the second element is the turn scale. Optionally, the length from the
   * center of rotation to the middle wheel and the middle scale can be passed as the third and
   * fourth elements. The straight scale converts motor degrees to meters, the turn scale converts
   * motor degrees to robot turn degrees, and the middle scale converts middle wheel degrees to
   * meters.
   *
   * @param iscales {straight scale, turn scale} or {straight scale, turn scale, length to middle
   * wheel in meters, middle scale}.
   * @param itpr The ticks per revolution of the encoders.
   * @param ilogger The logger this instance will log to.
   */
  ChassisScales(const std::initializer_list<double> &iscales,
                double itpr,
                const std::shared_ptr<Logger> &ilogger = Logger::getDefaultLogger());

  QLength wheelDiameter;
  QLength wheelTrack;
  QLength middleWheelDistance;
  QLength middleWheelDiameter;
  double straight;
  double turn;
  double middle;
  double tpr;

  protected:
  static void validateInputSize(std::size_t inputSize, const std::shared_ptr<Logger> &logger);
};
} // namespace okapi
