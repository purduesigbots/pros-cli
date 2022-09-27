#include "okapi/api/units/QAngle.hpp"
#include "okapi/api/units/QLength.hpp"
#include "okapi/api/units/QSpeed.hpp"
#include <stdexcept>
#include <typeindex>
#include <unordered_map>

#pragma once

namespace okapi {

/**
* Returns a short name for a unit.
* For example: `str(1_ft)` will return "ft", so will `1 * foot` or `0.3048_m`.
* Throws std::domain_error when `q` is a unit not defined in this function.
*
* @param q Your unit. Currently only QLength and QAngle are supported.
* @return The short string suffix for that unit.
*/
template <class QType> std::string getShortUnitName(QType q) {
  const std::unordered_map<std::type_index, std::unordered_map<double, const char *>> shortNameMap =
    {{typeid(meter),
      {
        {meter.getValue(), "m"},
        {decimeter.getValue(), "dm"},
        {centimeter.getValue(), "cm"},
        {millimeter.getValue(), "mm"},
        {kilometer.getValue(), "km"},
        {inch.getValue(), "in"},
        {foot.getValue(), "ft"},
        {yard.getValue(), "yd"},
        {mile.getValue(), "mi"},
        {tile.getValue(), "tile"},
      }},
     {typeid(degree), {{degree.getValue(), "deg"}, {radian.getValue(), "rad"}}}};

  try {
    return shortNameMap.at(typeid(q)).at(q.getValue());
  } catch (const std::out_of_range &e) {
    throw std::domain_error(
      "You have requested the shortname of an unknown unit somewhere (likely odometry strings). "
      "Shortname for provided unit is unspecified. You can override this function to add more "
      "names or manually specify the name instead.");
  }
}
} // namespace okapi
