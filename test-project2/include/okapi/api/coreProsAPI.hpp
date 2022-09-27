/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include <cmath>
#include <cstdbool>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <sstream>

#ifdef THREADS_STD
#include <thread>
#define CROSSPLATFORM_THREAD_T std::thread

#include <mutex>
#define CROSSPLATFORM_MUTEX_T std::mutex
#else
#include "api.h"
#include "pros/apix.h"
#define CROSSPLATFORM_THREAD_T pros::task_t
#define CROSSPLATFORM_MUTEX_T pros::Mutex
#endif

#define NOT_INITIALIZE_TASK                                                                        \
  (strcmp(pros::c::task_get_name(pros::c::task_get_current()), "User Initialization (PROS)") != 0)

#define NOT_COMP_INITIALIZE_TASK                                                                   \
  (strcmp(pros::c::task_get_name(pros::c::task_get_current()), "User Comp. Init. (PROS)") != 0)

class CrossplatformThread {
  public:
#ifdef THREADS_STD
  CrossplatformThread(void (*ptr)(void *),
                      void *params,
                      const char *const = "OkapiLibCrossplatformTask")
#else
  CrossplatformThread(void (*ptr)(void *),
                      void *params,
                      const char *const name = "OkapiLibCrossplatformTask")
#endif
    :
#ifdef THREADS_STD
      thread(ptr, params)
#else
      thread(
        pros::c::task_create(ptr, params, TASK_PRIORITY_DEFAULT, TASK_STACK_DEPTH_DEFAULT, name))
#endif
  {
  }

  ~CrossplatformThread() {
#ifdef THREADS_STD
    thread.join();
#else
    if (pros::c::task_get_state(thread) != pros::E_TASK_STATE_DELETED) {
      pros::c::task_delete(thread);
    }
#endif
  }

#ifdef THREADS_STD
  void notifyWhenDeleting(CrossplatformThread *) {
  }
#else
  void notifyWhenDeleting(CrossplatformThread *parent) {
    pros::c::task_notify_when_deleting(parent->thread, thread, 1, pros::E_NOTIFY_ACTION_INCR);
  }
#endif

#ifdef THREADS_STD
  void notifyWhenDeletingRaw(CROSSPLATFORM_THREAD_T *) {
  }
#else
  void notifyWhenDeletingRaw(CROSSPLATFORM_THREAD_T parent) {
    pros::c::task_notify_when_deleting(parent, thread, 1, pros::E_NOTIFY_ACTION_INCR);
  }
#endif

#ifdef THREADS_STD
  std::uint32_t notifyTake(const std::uint32_t) {
    return 0;
  }
#else
  std::uint32_t notifyTake(const std::uint32_t itimeout) {
    return pros::c::task_notify_take(true, itimeout);
  }
#endif

  static std::string getName() {
#ifdef THREADS_STD
    std::ostringstream ss;
    ss << std::this_thread::get_id();
    return ss.str();
#else
    return std::string(pros::c::task_get_name(NULL));
#endif
  }

  CROSSPLATFORM_THREAD_T thread;
};

class CrossplatformMutex {
  public:
  CrossplatformMutex() = default;

  void lock() {
#ifdef THREADS_STD
    mutex.lock();
#else
    while (!mutex.take(1)) {
    }
#endif
  }

  void unlock() {
#ifdef THREADS_STD
    mutex.unlock();
#else
    mutex.give();
#endif
  }

  protected:
  CROSSPLATFORM_MUTEX_T mutex;
};
