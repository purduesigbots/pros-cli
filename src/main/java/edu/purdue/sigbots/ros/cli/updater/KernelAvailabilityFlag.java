package edu.purdue.sigbots.ros.cli.updater;

import com.sun.istack.internal.NotNull;

import java.util.*;

public enum KernelAvailabilityFlag {
    KERNEL_AVAILABLE_ONLINE(1 << 0),
    KERNEL_AVAILABLE_LOCAL(1 << 1);

    private final int value;

    KernelAvailabilityFlag(int value) {
        this.value = value;
    }

    public static int getValue(KernelAvailabilityFlag flag) {
        return flag.value;
    }

    public static EnumSet<KernelAvailabilityFlag> getFlags(int statusValue) {
        EnumSet<KernelAvailabilityFlag> flags = EnumSet.noneOf(KernelAvailabilityFlag.class);
        for (KernelAvailabilityFlag flag : KernelAvailabilityFlag.values()) {
            if ((flag.value & statusValue) == flag.value) {
                flags.add(flag);
            }
        }
        return flags;
    }

    public static int getValue(Set<KernelAvailabilityFlag> flags) {
        final int[] value = {0};
        flags.forEach(f -> value[0] |= f.value);
        return value[0];
    }

    public static <T> Set<T> valueToMappedSet(Map<KernelAvailabilityFlag, T> map, int value) {
        HashSet<T> set = new HashSet<>();
        map.forEach((kernelAvailabilityFlag, t) -> {
            if ((value & kernelAvailabilityFlag.value) == kernelAvailabilityFlag.value) {
                set.add(t);
            }
        });
        return set;
    }

    public int getValue() {
        return value;
    }

    public EnumSet<KernelAvailabilityFlag> getFlags() {
        return getFlags(value);
    }

    /**
     * @return Returns a default map to be used by <code>valueToMappedSet</code>. KERNEL_AVAILABLE_LOCAL maps to
     * the string "local" and KERNEL_AVAILABLE_ONLINE maps to the string "online"
     */
    @NotNull
    public static Map<KernelAvailabilityFlag, String> getSuggestedKernelMapping() {
        HashMap<KernelAvailabilityFlag, String> map = new HashMap<>();
        map.put(KernelAvailabilityFlag.KERNEL_AVAILABLE_LOCAL, "local");
        map.put(KernelAvailabilityFlag.KERNEL_AVAILABLE_ONLINE, "online");
        return map;
    }
}
