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
            // Will not change update site if no update site was specified as the default site is the site determined be PROSActions
            actions.setUpdateSite(new URL(arguments.getString("site")), false);
        } catch (IOException ignored) { // safely ignored as not serializing
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
                environmentsMap.entrySet()
                        .forEach(e -> System.out.printf("%s\t%s\r\n", e.getKey(), e.getValue()));
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
                if (actions.resolveKernelLocalRequest(kernel).size() == 0) {
                    System.out.println("No kernels matched. Nothing to clean.");
                } else {
                    for (String k : actions.resolveKernelLocalRequest(kernel)) {
                        System.out.println("Deleting " + k);
                        actions.deleteKernel(k);
                    }
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
