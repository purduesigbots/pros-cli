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

package edu.purdue.sigbots.ros.cli;

import edu.purdue.sigbots.ros.cli.commands.*;
import edu.purdue.sigbots.ros.cli.management.PROSActions;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.action.StoreTrueArgumentAction;
import net.sourceforge.argparse4j.impl.action.VersionArgumentAction;
import net.sourceforge.argparse4j.inf.*;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.Scanner;

class Application {

    public static void main(String[] args) {
        ArgumentParser argumentParser = ArgumentParsers.newArgumentParser("pros");
        argumentParser.description("Create and upgrade PROS projects from an update site.");
        argumentParser.version("0.5.0");
        argumentParser.defaultHelp(true);
        argumentParser.addArgument("--version").action(new VersionArgumentAction());
        argumentParser.epilog("This program licensed under the revised BSD license. (c) 2016 PURDUE ACM SIGBOTS");

        Subparsers subparsers = argumentParser.addSubparsers().title("command");

        checkLocalKernelRepository(new PROSActions());
        getUpdateSite(new PROSActions());

        // <editor-fold desc="Create subparser">
        Subparser createParser = subparsers.addParser("create")
                .defaultHelp(true)
                .setDefault("handler", CreateCommand.class);
        createParser.addArgument("directory")
                .help("PROS project to create.");
        createParser.addArgument("--kernel")
                .nargs("?")
                .metavar("KERNEL")
                .setDefault("latest")
                .help("Specify kernel version to target. " +
                        "'latest' defaults to highest locally available repository. " +
                        "Use 'pros fetch latest' to download latest repository from update site.");
        createParser.addArgument("--environments")
                .nargs("+")
                .setDefault(Collections.singletonList("none"))
                .help("define environments to target. " +
                        "Available environments are determined by the kernel loader and " +
                        "can be found using 'pros fetch KERNEL -e'");
        createParser.addArgument("-f", "--force")
                .action(new StoreTrueArgumentAction())
                .help("Don't prompt to overwrite existing directory");
        createParser.addArgument("-v", "--verbose")
                .action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        // </editor-fold>


        // <editor-fold desc="Upgrade subparser">
        Subparser upgradeParser = subparsers.addParser("upgrade")
                .defaultHelp(true)
                .setDefault("handler", UpgradeCommand.class);
        upgradeParser.addArgument("directory")
                .help("PROS project directory to upgrade.");
        upgradeParser.addArgument("--kernel")
                .nargs("?")
                .metavar("KERNEL")
                .setDefault("latest")
                .help("Specify kernel version to upgrade to.");
        upgradeParser.addArgument("--environments")
                .nargs("+")
                .setDefault(Collections.singletonList("none"))
                .help("Define environments to target. " +
                        "Available environments are determined by the kernel kernels and " +
                        "can be found by using 'pros fetch KERNEL -e'");
        upgradeParser.addArgument("-f", "--force")
                .action(new StoreTrueArgumentAction())
                .help("Create/update files regardless if project is considered to be a PROS project.");
        upgradeParser.addArgument("-v", "--verbose")
                .action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        // </editor-fold>

        // <editor-fold desc="Fetch subparser">
        Subparser fetchParser = subparsers.addParser("fetch").defaultHelp(true)
                .setDefault("handler", FetchCommand.class);
        fetchParser.addArgument("kernel")
                .nargs("?")
                .setDefault("all")
                .help("Kernel to fetch. May be a regular expression. " +
                        "May be 'latest' to fetch latest from online site or locally available (whichever is higher). " +
                        "'all' specifies all kernels if applicable.");
        fetchParser.addArgument("--site")
                .nargs("?")
                .metavar("SITE")
                .setDefault(getUpdateSite(new PROSActions()))
                .help("Specify site to do online operations with. If an obvious Git URL is used (starting with " +
                        "'ssh://', 'git://', or ending with '.git'), then the Git update site provider will be used. " +
                        "All kernels on the remote repository will be fetched and merged-theirs - online kernel " +
                        "listings are not guaranteed to be accurate. A Git site can be forced by appending the url with " +
                        "\"git clone <url>\".");

        MutuallyExclusiveGroup mutuallyExclusiveGroup = fetchParser.addMutuallyExclusiveGroup();
        mutuallyExclusiveGroup.addArgument("-e", "--environments")
                .action(new StoreTrueArgumentAction())
                .help("List all environments that can be used with this kernel");
        mutuallyExclusiveGroup.addArgument("-d", "--download")
                .action(new StoreTrueArgumentAction())
                .help("Downloads kernel(s) from online site. Will delete kernel template if it exists locally.");
        mutuallyExclusiveGroup.addArgument("-c", "--clean")
                .action(new StoreTrueArgumentAction())
                .help("Deletes kernel template(s) from local repository.");

        fetchParser.addArgument("-v", "--verbose")
                .action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        fetchParser.epilog("Without -e, -d, or -c, will list if the specified kernel is available locally and/or online.");
        // </editor-fold>

        // <editor-fold desc="Config Command">
        Subparser configParser = subparsers.addParser("config")
                .defaultHelp(true)
                .setDefault("handler", ConfigCommand.class);
        configParser.addArgument("variable")
                .help("Variable to configure.");
        configParser.addArgument("value")
                .nargs("?")
                .help("Optional value to set. If no value is provided, the current stored value will be returned.");
        // </editor-fold>

        Namespace namespace = argumentParser.parseArgsOrFail(args);
        if (namespace == null) {
            System.err.println("Error parsing arguments");
            System.exit(1);
        }

        boolean verbose = false;
        if (namespace.getBoolean("verbose") != null) {
            verbose = namespace.getBoolean("verbose");
        }
        final PROSActions actions = new PROSActions(verbose, System.out, System.err);

        Object handler = namespace.get("handler");
        if (handler != null && handler instanceof Class<?>) {
            try {
                Command command = (Command) ((Class<?>) handler)
                        .getConstructor()
                        .newInstance();
                command.handleArguments(namespace, actions);
            } catch (NoSuchMethodException | InstantiationException | InvocationTargetException | IllegalAccessException e) {
                e.printStackTrace();
            }
        }
    }

    private static URI getUpdateSite(PROSActions actions) {
        URI updateSite = actions.getUpdateSite();
        if (updateSite == null) {
            System.out.println("Update site is not set.");
            updateSite = actions.suggestUpdateSite();
            if (updateSite != null) {
                System.out.printf("What should the update site be? [%s] ", updateSite.toString());
                String response = (new Scanner(System.in)).nextLine();
                if (!response.isEmpty()) {
                    try {
                        actions.setUpdateSite(response);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                    updateSite = actions.getUpdateSite();
                } else {
                    try {
                        actions.setUpdateSite(actions.suggestUpdateSite().toString());
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            } else {
                System.out.printf("Where should the update site be? ");
                String response = (new Scanner(System.in)).nextLine();
                if (!response.isEmpty()) {
                    try {
                        actions.setUpdateSite(response);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                    updateSite = actions.getUpdateSite();
                }
            }
        }
        return updateSite;
    }


    private static void checkLocalKernelRepository(PROSActions actions) {
        Path localKernelRepository = actions.getLocalRepositoryPath();
        if (localKernelRepository == null || localKernelRepository.toString().isEmpty()) {
            System.out.println("The local kernel directory is not set.");
            localKernelRepository = actions.suggestLocalKernelRepository();
            if (localKernelRepository != null) {
                System.out.printf("Where should local kernels be stored? [%s] ", localKernelRepository.toString());
                String response = new Scanner(System.in).nextLine();
                if (!response.isEmpty()) {
                    localKernelRepository = Paths.get(response);
                }

            } else {
                System.out.printf("Where should local kernels be stored? ");
                String response = new Scanner(System.in).nextLine();
                if (!response.isEmpty() && Files.isWritable(Paths.get(response))) {
                    localKernelRepository = Paths.get(response);
                } else {
                    System.out.println("Not a valid location");
                    System.exit(-1);
                }
            }
            try {
                actions.setLocalKernelRepository(localKernelRepository);
                System.out.println("Local kernels will be stored at " + actions.getLocalRepositoryPath().toString());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
