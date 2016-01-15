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

import edu.purdue.sigbots.ros.cli.updater.PROSActions;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Scanner;
import java.util.Set;

public class UpgradeCommand extends Command {

    @Override
    public void handleArguments(Namespace arguments, PROSActions actions) {
        boolean verbose = arguments.getBoolean("verbose");
        try {
            // <editor-fold desc="Resolve directory">
            Path projectPath;
            if (arguments.getString("directory").matches("^~[\\\\/].*")) {
                projectPath = Paths.get(System.getProperty("user.home") + arguments.getString("directory").substring(1));
            } else {
                projectPath = Paths.get(arguments.getString("directory"));
            }
            if (verbose) {
                System.out.printf("Resolved path to %s\r\n", projectPath.toString());
            }
            // </editor-fold>

            // <editor-fold desc="resolve requested kernel">
            Set<String> kernels = actions.resolveKernelLocalRequest(arguments.getString("kernel"));
            String kernel = null;
            if (kernels.size() == 1) {
                kernel = kernels.iterator().next();
            } else if (kernels.size() > 1) {
                String options = "";
                for (String k : kernels) {
                    options += k + ", ";
                }
                options = options.substring(0, options.lastIndexOf(", "));
                System.out.printf("Multiple kernels matched. Which kernel? (%s) ", options);
                kernel = (new Scanner(System.in)).nextLine();
                if (!kernels.contains(kernel)) {
                    System.out.println("Kernel was not a valid option.");
                    System.exit(1);
                }
            } else {
                System.out.println("No kernels were matched. If the kernel exists on the update site, " +
                        "try 'pros fetch KERNEL' to pull from the update site.");
                System.exit(1);
            }
            // </editor-fold>

            // Ensure project is acceptable to upgrade
            if (Files.exists(projectPath) && !Files.isDirectory(projectPath)) {
                System.out.println("Project is a file. Cannot upgrade a file.");
                System.exit(-1);
            }

            // Ensure environments are ok
            List<String> environments = arguments.getList("environments");
            if (!actions.listEnvironments(actions.findKernelDirectory(kernel)).containsAll(environments)) {
                System.out.println("Environments list does not match.");
                System.out.println("Available values: " + actions.listEnvironments(actions.findKernelDirectory(kernel)));
                System.out.println("Received values: " + environments);
                System.exit(-1);
            }

            actions.upgradeProject(kernel, projectPath, environments);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
