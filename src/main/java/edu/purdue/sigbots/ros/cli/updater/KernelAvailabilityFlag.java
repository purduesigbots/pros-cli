/*******************************************************************************
 * Copyright (c) 2016, Purdue University ACM SIG BOTS.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Purdue University ACM SIG BOTS nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 ******************************************************************************/

package edu.purdue.sigbots.ros.cli.updater;

import java.util.*;

/**
 * Enum used to denote kernels that are available online or offline
 * <p>
 * Value cheat sheet:
 * 0 (00) - none
 * 1 (01) - KERNEL_AVAILABLE_ONLINE
 * 2 (10) - KERNEL_AVAILABLE_LOCAL
 * 3 (11) - KERNEL_AVAILABLE_ONLINE and KERNEL_AVAILABLE_LOCAL
 */
@SuppressWarnings("PointlessBitwiseExpression")
public enum KernelAvailabilityFlag {
    KERNEL_AVAILABLE_ONLINE(1 << 0), // 1 (0b01)
    KERNEL_AVAILABLE_LOCAL(1 << 1); // 2  (0b10)

    private final int value;

    KernelAvailabilityFlag(int value) {
        this.value = value;
    }

    /**
     * @param flag An enum member from KernelAvailabilityFlag
     *             (KERNEL_AVAILABLE_ONLINE or KERNEL_AVAILABLE_LOCAL)
     * @return The integer value associated with the enum member
     */
    public static int getValue(KernelAvailabilityFlag flag) {
        return flag.value;
    }

    /**
     * @param statusValue An integer value that represents a number of KernelAvailabilityFlags
     * @return An EnumSet of KernelAvailabilityFlags that are associated with the integer value
     */
    public static EnumSet<KernelAvailabilityFlag> getFlags(int statusValue) {
        EnumSet<KernelAvailabilityFlag> flags = EnumSet.noneOf(KernelAvailabilityFlag.class);
        for (KernelAvailabilityFlag flag : KernelAvailabilityFlag.values()) {
            if ((flag.value & statusValue) == flag.value) {
                flags.add(flag);
            }
        }
        return flags;
    }

    /**
     * Calling KernelAvailabilityFlag.getValue(KernelAvailabilityFlag.getFlags(1)) will return 1
     *
     * @param flags An set of KernelAvailabilityFlags
     * @return The value associated with the union of all the flags
     */
    public static int getValue(Set<KernelAvailabilityFlag> flags) {
        final int[] value = {0};
        flags.forEach(f -> value[0] |= f.value);
        return value[0];
    }

    /**
     * Maps an integer value to a set of T that was determined by the KernelAvailabilityFlags
     * associated with the integer value
     *
     * @param map   A map containing at most one of each KernelAvailabilityFlag that is paired to an object of type T
     *              getSuggestedKernelMapping returns a default mapping to Strings.
     * @param value The integer value to convert
     * @param <T>   An object type to convert to (most typically a String)
     * @return The set of values that are associated with the integer value as determined by the KernelAvailabilityFlags
     */
    public static <T> Set<T> valueToMappedSet(Map<KernelAvailabilityFlag, T> map, int value) {
        HashSet<T> set = new HashSet<>();
        map.forEach((kernelAvailabilityFlag, t) -> {
            if ((value & kernelAvailabilityFlag.value) == kernelAvailabilityFlag.value) {
                set.add(t);
            }
        });
        return set;
    }

    /**
     * @return Returns a default map to be used by <code>valueToMappedSet</code>. KERNEL_AVAILABLE_LOCAL maps to
     * the string "local" and KERNEL_AVAILABLE_ONLINE maps to the string "online"
     */
    public static Map<KernelAvailabilityFlag, String> getSuggestedKernelMapping() {
        HashMap<KernelAvailabilityFlag, String> map = new HashMap<>();
        map.put(KernelAvailabilityFlag.KERNEL_AVAILABLE_LOCAL, "local");
        map.put(KernelAvailabilityFlag.KERNEL_AVAILABLE_ONLINE, "online");
        return map;
    }

    /**
     * @return Integer value of the flag
     */
    public int getValue() {
        return value;
    }
}
