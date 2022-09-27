/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/units/QFrequency.hpp"
#include "okapi/api/units/QTime.hpp"

namespace okapi {
class AbstractTimer {
  public:
  /**
   * A Timer base class which implements its methods in terms of millis().
   *
   * @param ifirstCalled the current time
   */
  explicit AbstractTimer(QTime ifirstCalled);

  virtual ~AbstractTimer();

  /**
   * Returns the current time in units of QTime.
   *
   * @return the current time
   */
  virtual QTime millis() const = 0;

  /**
   * Returns the time passed in ms since the previous call of this function.
   *
   * @return The time passed in ms since the previous call of this function
   */
  virtual QTime getDt();

  /**
   * Returns the time passed in ms since the previous call of getDt(). Does not change the time
   * recorded by getDt().
   *
   * @return The time passed in ms since the previous call of getDt()
   */
  virtual QTime readDt() const;

  /**
   * Returns the time the timer was first constructed.
   *
   * @return The time the timer was first constructed
   */
  virtual QTime getStartingTime() const;

  /**
   * Returns the time since the timer was first constructed.
   *
   * @return The time since the timer was first constructed
   */
  virtual QTime getDtFromStart() const;

  /**
   * Place a time marker. Placing another marker will overwrite the previous one.
   */
  virtual void placeMark();

  /**
   * Clears the marker.
   *
   * @return The old marker
   */
  virtual QTime clearMark();

  /**
   * Place a hard time marker. Placing another hard marker will not overwrite the previous one;
   * instead, call clearHardMark() and then place another.
   */
  virtual void placeHardMark();

  /**
   * Clears the hard marker.
   *
   * @return The old hard marker
   */
  virtual QTime clearHardMark();

  /**
   * Returns the time since the time marker. Returns 0_ms if there is no marker.
   *
   * @return The time since the time marker
   */
  virtual QTime getDtFromMark() const;

  /**
   * Returns the time since the hard time marker. Returns 0_ms if there is no hard marker set.
   *
   * @return The time since the hard time marker
   */
  virtual QTime getDtFromHardMark() const;

  /**
   * Returns true when the input time period has passed, then resets. Meant to be used in loops
   * to run an action every time period without blocking.
   *
   * @param time time period
   * @return true when the input time period has passed, false after reading true until the
   *   period has passed again
   */
  virtual bool repeat(QTime time);

  /**
   * Returns true when the input time period has passed, then resets. Meant to be used in loops
   * to run an action every time period without blocking.
   *
   * @param frequency the repeat frequency
   * @return true when the input time period has passed, false after reading true until the
   *   period has passed again
   */
  virtual bool repeat(QFrequency frequency);

  protected:
  QTime firstCalled;
  QTime lastCalled;
  QTime mark;
  QTime hardMark;
  QTime repeatMark;
};
} // namespace okapi
