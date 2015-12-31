package edu.purdue.sigbots.ros.cli.commands;

import edu.purdue.sigbots.ros.cli.updater.KernelAvailabilityFlag;
import edu.purdue.sigbots.ros.cli.updater.PROSActions;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.IOException;
import java.net.URL;
import java.util.Map;
import java.util.Set;

public class FetchCommand extends Command {
    @Override
    public void handleArguments(Namespace arguments, PROSActions actions) {
        try {
            actions.setUpdateSite(new URL(arguments.getString("site")), false);
        } catch (IOException e) {
            e.printStackTrace();
        }
        String kernel = arguments.getString("kernel");
        if (kernel.equalsIgnoreCase("all") || kernel.matches(" *")) {
            kernel = ".*";
        }
        if (arguments.getBoolean("environments")) {
            try {
                Map<String, Set<String>> environmentsMap = actions.listEnvironments(kernel);
                if (environmentsMap.size() == 0) {
                    System.out.println("No local kernels downloaded! Use `pros fetch latest -d` to download the latest kernel");
                    System.exit(1);
                }
                System.out.println("Kernel\tEnvironment(s)");
                environmentsMap.entrySet().forEach(e -> System.out.printf("%s\t%s\r\n", e.getKey(), e.getValue()));
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else if (arguments.getBoolean("download")) {
            try {
                for (String k : actions.resolveKernelUpdateRequest(kernel)) {
                    System.out.println("Downloading " + k);
                    actions.downloadKernel(k);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else if (arguments.getBoolean("clean")) {
            try {
                for(String k : actions.resolveKernelLocalRequest(kernel)) {
                    actions.deleteKernel(k);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            try {
                Map<String, Integer> kernels = actions.getAllKernels(kernel);
                System.out.println("Kernel\tAvailability");
                kernels.entrySet().stream()
                        .forEach(entry -> System.out.printf("%s\t%s\r\n", entry.getKey(),
                                KernelAvailabilityFlag.valueToMappedSet(KernelAvailabilityFlag.getSuggestedKernelMapping(), entry.getValue())));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
