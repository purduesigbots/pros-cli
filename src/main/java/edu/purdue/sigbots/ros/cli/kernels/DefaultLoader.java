package edu.purdue.sigbots.ros.cli.kernels;

import edu.purdue.sigbots.ros.cli.SimpleFileCopier;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
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
        out.printf("Creating project at %s from %s targeting %s environment(s)\r\n",
                projectPath.toString(),
                kernelPath.toString(),
                environments.toString());

        Files.createDirectories(projectPath);

        Files.walkFileTree(kernelPath, new SimpleFileCopier(verbose, out, kernelPath, projectPath) {
            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
                if (dir.getFileName().toString().equals(ENVIRONMENTS_LOCATION)) {
                    return FileVisitResult.SKIP_SUBTREE;
                }
                return super.preVisitDirectory(dir, attrs);
            }
        });

        for (String environment : environments) {
            if (getAvailableEnvironments(kernelPath).contains(environment)
                    && !environment.equals("none")) {
                out.printf("Copying files for %s environment\r\n", environment);
                Path environmentPath = kernelPath.resolve(Paths.get(ENVIRONMENTS_LOCATION, environment));
                Files.walkFileTree(environmentPath, new SimpleFileCopier(verbose, out, environmentPath, projectPath) {
                    @Override
                    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
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
            }
        }
    }

    @Override
    public void upgradeProject(Path kernelPath, Path projectPath, List<String> environments) throws IOException {
        out.println("Upgrading project at " + projectPath.toString());

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
            }
        }

        for (String environment : environments) {
            if (getAvailableEnvironments(kernelPath).contains(environment)
                    && !environment.equals("none")) {
                out.printf("Copying files for %s environment\r\n", environment);
                Path environmentPath = kernelPath.resolve(Paths.get(ENVIRONMENTS_LOCATION, environment));
                Files.walkFileTree(environmentPath, new SimpleFileCopier(verbose, out, environmentPath, projectPath) {
                    @Override
                    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
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
