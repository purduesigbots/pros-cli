package edu.purdue.sigbots.purdueros.cli.commands;

import edu.purdue.sigbots.purdueros.cli.kernels.DefaultLoader;
import edu.purdue.sigbots.purdueros.cli.kernels.Loader;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;

public class UpgradeCommand extends Command {
    public UpgradeCommand(Namespace namespace) {
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
            projectDirectory = Paths.get(namespace.getString("directory")).toRealPath();
        } catch (NoSuchFileException e) {
            System.err.println("Project does not exist. Cannot upgrade.");
            System.exit(1);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Double check everything is OK with projectDirectory Path
        if (projectDirectory == null) {
            System.err.printf("Unable to resolve directory '%s'\r\n", namespace.getString("directory"));
            System.err.println("Directory path is null.");
            System.exit(-1);
        }
        if (!new File(projectDirectory.toString()).isDirectory()) {
            System.err.println("Error: directory is a file.");
            System.exit(-1);
        }

        if (verbose) System.out.printf("Finding kernel loader for '%s'\r\n", kernel);
        Class<?> kernelLoaderClass = DefaultLoader.class;
        try {
            URL url = new File(getLocalKernelRepository(), kernel).toURI().toURL();
            ClassLoader classLoader = new URLClassLoader(new URL[]{url});
            kernelLoaderClass = classLoader.loadClass(
                    String.format("edu.purdue.sigbots.purdueros.cli.kernels.Kernel%sLoader", kernel)
            );
            if (!kernelLoaderClass.isAssignableFrom(Loader.class)) throw new Exception();
        } catch (Exception e) {
            if (verbose) System.out.println("Could not find custom kernel loader.");
        }
        if (verbose) System.out.printf("Using %s kernel loader.\r\n", kernelLoaderClass.getSimpleName());

        try {
            Loader kernelLoader = (Loader) kernelLoaderClass
                    .getConstructor(Path.class, Path.class, List.class)
                    .newInstance(projectDirectory, new File(getLocalKernelRepository(), kernel).toPath(), namespace.getList("environments"));
            kernelLoader.upgradeProject(namespace.getBoolean("force"));
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
