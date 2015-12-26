package edu.purdue.sigbots.purdueros.cli.commands;

import edu.purdue.sigbots.purdueros.cli.kernels.Loader;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

public class CreateCommand extends Command {
    public CreateCommand(Namespace namespace) {
        super(namespace);
    }

    @Override
    public void handleArgs() {
        if (verbose) System.out.printf("Resolving kernel version '%s'\r\n", namespace.getString("kernel"));
        String kernel = resolveKernel(namespace.getString("kernel"));
        if (verbose) System.out.printf("Resolved kernel to '%s'\r\n", kernel);

        if (verbose) System.out.printf("Resolving directory path '%s'\r\n", namespace.getString("directory"));
        Path projectDirectory = null;
        try {
            projectDirectory = createPathIfNotExists(namespace.getString("directory"));
        } catch (IOException e) {
            System.err.printf("Unable to resolve directory '%s'\r\n", namespace.getString("directory"));
            e.printStackTrace();
            System.exit(-1);
        }
        if (verbose) System.out.printf("Project path is '%s'\r\n", projectDirectory);

        // Double check everything is OK with projectDirectory Path
        if (projectDirectory == null) {
            System.err.printf("Unable to resolve directory '%s'\r\n", namespace.getString("directory"));
            System.err.println("Directory path is null.");
            System.exit(-1);
        }
        File projectDirectoryFile = new File(projectDirectory.toString());
        if (!projectDirectoryFile.isDirectory()) {
            if (namespace.getBoolean("force")) {
                if (!projectDirectoryFile.delete()) {
                    System.err.println("Error deleting existing file despite --force flag. " +
                            "Delete the file then try again.");
                    System.exit(-1);
                } else {
                    if (verbose) System.out.printf("'%s' was a file. Deleted and creating a directory.\r\n", kernel);
                    try {
                        projectDirectory = createPathIfNotExists(namespace.getString("directory"));
                    } catch (IOException e) {
                        System.err.printf("Unable to resolve directory '%s'\r\n", namespace.getString("directory"));
                        e.printStackTrace();
                        System.exit(-1);
                    }
                }
            } else {
                System.err.println("Error: directory is a file. Delete it first or use --force flag.");
                System.exit(-1);
            }
        }

        try {
            Loader kernelLoader = (Loader) getKernelLoader(kernel)
                    .getConstructor(Path.class, Path.class, List.class)
                    .newInstance(projectDirectory, new File(getLocalKernelRepository(), kernel).toPath(), namespace.getList("environments"));
            kernelLoader.createProject(namespace.getBoolean("force"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private String resolveKernel(String kernel) {
        if (kernel.equalsIgnoreCase("latest")) {
            try {
                File[] kernels = getLocalKernelRepository().listFiles(File::isDirectory);
                Arrays.sort(kernels);
                return kernels[kernels.length - 1].getName();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return kernel;
    }
}
