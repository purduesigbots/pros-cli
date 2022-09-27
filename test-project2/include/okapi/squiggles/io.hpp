/**
 * Copyright 2020 Jonathan Bayless
 *
 * Use of this source code is governed by an MIT-style license that can be found
 * in the LICENSE file or at https://opensource.org/licenses/MIT.
 */
#ifndef _SQUIGGLES_IO_HPP_
#define _SQUIGGLES_IO_HPP_

#include <optional>
#include <vector>

#include "geometry/profilepoint.hpp"

namespace squiggles {
/**
 * Writes the path data to a CSV file.
 *
 * @param out The output stream to write the CSV data to. This is usually a
 * file.
 * @param path The path to serialized
 *
 * @return 0 if the path was serialized succesfully or -1 if an error occurred.
 */
int serialize_path(std::ostream& out, std::vector<ProfilePoint> path);

/**
 * Converts CSV data into a path.
 *
 * @param in The input stream containing the CSV data. This is usually a file.
 *
 * @return The path specified by the CSV data or std::nullopt if de-serializing
 *         the path was unsuccessful.
 */
std::optional<std::vector<ProfilePoint>> deserialize_path(std::istream& in);

/**
 * Converts CSV data from the Pathfinder library's format to a Squiggles path.
 *
 * NOTE: this code translates data from Jaci Brunning's Pathfinder library.
 * The source for that library can be found at:
 * https://github.com/JaciBrunning/Pathfinder/
 *
 * @param left The input stream containing the left wheels' CSV data. This is
 *             usually a file.
 * @param right The input stream containing the right wheels' CSV data. This is
 *             usually a file.
 *
 * @return The path specified by the CSV data or std::nullopt if de-serializing
 *         the path was unsuccessful.
 */
std::optional<std::vector<ProfilePoint>>
deserialize_pathfinder_path(std::istream& left, std::istream& right);
} // namespace squiggles

#endif
