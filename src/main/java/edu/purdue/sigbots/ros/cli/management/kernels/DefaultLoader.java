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

package edu.purdue.sigbots.ros.cli.management.kernels;

import edu.purdue.sigbots.ros.cli.management.SimpleFileCopier;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.stream.Collectors;

public class DefaultLoader extends Loader {
    private static final String ENVIRONMENTS_LOCATION = "=environments=";
    private static final String TEMPLATE_PROJECT_NAME = "Default_VeX_Cortex";
    private static final List<Path> UPGRADE_FILES = Arrays.asList(
            Paths.get("common.mk"),
            Paths.get("firmware"),
            Paths.get("include", "API.h")
    );

    public DefaultLoader(Boolean verbose, PrintStream out, PrintStream err) {
        super(verbose, out, err);
    }

    @Override
    public void createProject(Path kernelPath, Path projectPath, List<String> environments) throws IOException {
        // fix environments
        if (environments == null) {
            environments = Collections.singletonList("none");
        }

        out.printf("Creating project at %s from %s targeting %s environment(s)\r\n",
                projectPath.toString(),
                kernelPath.toString(),
                environments.toString());

        Files.createDirectories(projectPath);

        System.out.print("Copying base files");
        Files.walkFileTree(kernelPath, new SimpleFileCopier(verbose, out, kernelPath, projectPath) {
            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attributes) throws IOException {
                if (dir.getFileName().toString().equals(ENVIRONMENTS_LOCATION)) {
                    return FileVisitResult.SKIP_SUBTREE;
                }
                return super.preVisitDirectory(dir, attributes);
            }
        });
        System.out.println("\rCopied base files ");

        for (String environment : environments) {
            if (getAvailableEnvironments(kernelPath).contains(environment) && !environment.equals("none")) {
                out.printf("Copying files for %s environment", environment);
                Path environmentPath = kernelPath.resolve(Paths.get(ENVIRONMENTS_LOCATION, environment));
                Files.walkFileTree(environmentPath, new SimpleFileCopier(verbose, out, environmentPath, projectPath) {
                    @Override
                    public FileVisitResult visitFile(Path file, BasicFileAttributes attributes) throws IOException {
                        if (verbose) {
                            out.printf("Copying file '%s'\r\n", environmentPath.relativize(file));
                        }
                        Path projectFilePath = projectPath.resolve(environmentPath.relativize(file));
                        if (Files.notExists(projectFilePath)) {
                            Files.createDirectories(projectFilePath.getParent());
                            Files.createFile(projectFilePath);
                        }
                        List<String> lines = Files.readAllLines(file);
                        lines.replaceAll(s -> s.replaceAll(TEMPLATE_PROJECT_NAME, projectPath.getFileName().toString()));
                        Files.write(projectFilePath, lines);
                        return FileVisitResult.CONTINUE;
                    }
                });
                out.printf("\rCopied files for %s environment \r\n", environment);
            }
        }
    }

    @Override
    public void upgradeProject(Path kernelPath, Path projectPath, List<String> environments) throws IOException {
        out.println("Upgrading project at " + projectPath.toString());

        out.print("Upgrading base files");
        for (Path sourcePath : UPGRADE_FILES) {
            Path destinationPath = projectPath.resolve(sourcePath);
            Path originPath = kernelPath.resolve(sourcePath);
            if (Files.isDirectory(originPath)) {
                Files.walkFileTree(originPath, new SimpleFileCopier(verbose, out, originPath, destinationPath));
            } else {
                if (Files.notExists(destinationPath)) {
                    Files.createDirectories(destinationPath.getParent());
                    Files.createFile(destinationPath);
                }
                Files.copy(originPath, destinationPath, StandardCopyOption.REPLACE_EXISTING);
                if (verbose) {
                    out.printf("Copying file %s\r\n", sourcePath);
                }
            }
        }
        out.println("Upgraded base files ");

        // fix environments
        if (environments == null) {
            environments = Collections.singletonList("none");
        } else if (environments.size() == 0) {
            for (String environment : getAvailableEnvironments(kernelPath)) {
                Path environmentPath = kernelPath.resolve(ENVIRONMENTS_LOCATION);
                if (Files.exists(projectPath.resolve(Files.list(environmentPath).collect(Collectors.toList()).get(0)))) {
                    // first file or directory in kernel target environment directory should exist in project directory
                    environments.add(environment);
                }
            }
        }

        for (String environment : environments) {
            if (getAvailableEnvironments(kernelPath).contains(environment)
                    && !environment.equals("none")) {
                out.printf("Copying files for %s environment", environment);
                Path environmentPath = kernelPath.resolve(Paths.get(ENVIRONMENTS_LOCATION, environment));
                Files.walkFileTree(environmentPath, new SimpleFileCopier(verbose, out, environmentPath, projectPath) {
                    @Override
                    public FileVisitResult visitFile(Path file, BasicFileAttributes attributes) throws IOException {
                        if (verbose) {
                            out.printf("Copying file '%s'\r\n", environmentPath.relativize(file));
                        }
                        Path projectFile = projectPath.resolve(environmentPath.relativize(file));
                        if (Files.notExists(projectFile)) {
                            Files.createDirectories(projectFile.getParent());
                            Files.createFile(projectFile);
                        }
                        List<String> fileOutput = Files.readAllLines(file);
                        fileOutput.replaceAll(s -> s.replaceAll(TEMPLATE_PROJECT_NAME, projectPath.getFileName().toString()));
                        Files.write(projectFile, fileOutput);
                        return FileVisitResult.CONTINUE;
                    }
                });
                out.printf("Copied files for %s environment \r\n", environment);
            }
        }
    }

    @Override
    public Set<String> getAvailableEnvironments(Path kernelPath) throws IOException {
        Set<String> environments = new HashSet<>();
        environments.add("none");
        Path environmentsPath = kernelPath.resolve(ENVIRONMENTS_LOCATION);
        if (Files.exists(environmentsPath) && Files.isDirectory(environmentsPath)) {
            environments.addAll(Files.list(environmentsPath).map(p -> p.getFileName().toString()).collect(Collectors.toList()));
        }
        return environments;
    }
}
