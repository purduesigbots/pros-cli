/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
#pragma once

#include "okapi/api/coreProsAPI.hpp"
#include "okapi/api/util/abstractTimer.hpp"
#include "okapi/api/util/mathUtil.hpp"
#include <memory>
#include <mutex>

#if defined(THREADS_STD)
#else
#include "okapi/impl/util/timer.hpp"
#endif

#define LOG_DEBUG(msg) logger->debug([=]() { return msg; })
#define LOG_INFO(msg) logger->info([=]() { return msg; })
#define LOG_WARN(msg) logger->warn([=]() { return msg; })
#define LOG_ERROR(msg) logger->error([=]() { return msg; })

#define LOG_DEBUG_S(msg) LOG_DEBUG(std::string(msg))
#define LOG_INFO_S(msg) LOG_INFO(std::string(msg))
#define LOG_WARN_S(msg) LOG_WARN(std::string(msg))
#define LOG_ERROR_S(msg) LOG_ERROR(std::string(msg))

namespace okapi {
class Logger {
  public:
  enum class LogLevel {
    debug = 4, ///< debug
    info = 3,  ///< info
    warn = 2,  ///< warn
    error = 1, ///< error
    off = 0    ///< off
  };

  /**
   * A logger that does nothing.
   */
  Logger() noexcept;

  /**
   * A logger that opens the input file by name. If the file contains `/ser/`, the file will be
   * opened in write mode. Otherwise, the file will be opened in append mode. The file will be
   * closed when the logger is destructed.
   *
   * @param itimer A timer used to get the current time for log statements.
   * @param ifileName The name of the log file to open.
   * @param ilevel The log level. Log statements more verbose than this level will be disabled.
   */
  Logger(std::unique_ptr<AbstractTimer> itimer,
         std::string_view ifileName,
         const LogLevel &ilevel) noexcept;

  /**
   * A logger that uses an existing file handle. The file will be closed when the logger is
   * destructed.
   *
   * @param itimer A timer used to get the current time for log statements.
   * @param ifile The log file to open. Will be closed by the logger!
   * @param ilevel The log level. Log statements more verbose than this level will be disabled.
   */
  Logger(std::unique_ptr<AbstractTimer> itimer, FILE *ifile, const LogLevel &ilevel) noexcept;

  ~Logger();

  constexpr bool isDebugLevelEnabled() const noexcept {
    return toUnderlyingType(logLevel) >= toUnderlyingType(LogLevel::debug);
  }

  template <typename T> void debug(T ilazyMessage) noexcept {
    if (isDebugLevelEnabled() && logfile && timer) {
      std::scoped_lock lock(logfileMutex);
      fprintf(logfile,
              "%ld (%s) DEBUG: %s\n",
              static_cast<long>(timer->millis().convert(millisecond)),
              CrossplatformThread::getName().c_str(),
              ilazyMessage().c_str());
    }
  }

  constexpr bool isInfoLevelEnabled() const noexcept {
    return toUnderlyingType(logLevel) >= toUnderlyingType(LogLevel::info);
  }

  template <typename T> void info(T ilazyMessage) noexcept {
    if (isInfoLevelEnabled() && logfile && timer) {
      std::scoped_lock lock(logfileMutex);
      fprintf(logfile,
              "%ld (%s) INFO: %s\n",
              static_cast<long>(timer->millis().convert(millisecond)),
              CrossplatformThread::getName().c_str(),
              ilazyMessage().c_str());
    }
  }

  constexpr bool isWarnLevelEnabled() const noexcept {
    return toUnderlyingType(logLevel) >= toUnderlyingType(LogLevel::warn);
  }

  template <typename T> void warn(T ilazyMessage) noexcept {
    if (isWarnLevelEnabled() && logfile && timer) {
      std::scoped_lock lock(logfileMutex);
      fprintf(logfile,
              "%ld (%s) WARN: %s\n",
              static_cast<long>(timer->millis().convert(millisecond)),
              CrossplatformThread::getName().c_str(),
              ilazyMessage().c_str());
    }
  }

  constexpr bool isErrorLevelEnabled() const noexcept {
    return toUnderlyingType(logLevel) >= toUnderlyingType(LogLevel::error);
  }

  template <typename T> void error(T ilazyMessage) noexcept {
    if (isErrorLevelEnabled() && logfile && timer) {
      std::scoped_lock lock(logfileMutex);
      fprintf(logfile,
              "%ld (%s) ERROR: %s\n",
              static_cast<long>(timer->millis().convert(millisecond)),
              CrossplatformThread::getName().c_str(),
              ilazyMessage().c_str());
    }
  }

  /**
   * Closes the connection to the log file.
   */
  constexpr void close() noexcept {
    if (logfile) {
      fclose(logfile);
      logfile = nullptr;
    }
  }

  /**
   * @return The default logger.
   */
  static std::shared_ptr<Logger> getDefaultLogger();

  /**
   * Sets a new default logger. OkapiLib classes use the default logger unless given another logger
   * in their constructor.
   *
   * @param ilogger The new logger instance.
   */
  static void setDefaultLogger(std::shared_ptr<Logger> ilogger);

  private:
  const std::unique_ptr<AbstractTimer> timer;
  const LogLevel logLevel;
  FILE *logfile;
  CrossplatformMutex logfileMutex;

  static bool isSerialStream(std::string_view filename);
};

extern std::shared_ptr<Logger> defaultLogger;

struct DefaultLoggerInitializer {
  DefaultLoggerInitializer() {
    if (count++ == 0) {
      init();
    }
  }
  ~DefaultLoggerInitializer() {
    if (--count == 0) {
      cleanup();
    }
  }

  static int count;

  static void init() {
#if defined(THREADS_STD)
    defaultLogger = std::make_shared<Logger>();
#else
    defaultLogger =
      std::make_shared<Logger>(std::make_unique<Timer>(), "/ser/sout", Logger::LogLevel::warn);
#endif
  }

  static void cleanup() {
  }
};

static DefaultLoggerInitializer defaultLoggerInitializer; // NOLINT(cert-err58-cpp)
} // namespace okapi
