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

public abstract class Command {
    protected static File localKernelRepository;
    protected Namespace namespace;
    protected boolean verbose;

    public Command(Namespace namespace) {
        this.namespace = namespace;
        if (namespace.get("verbose") != null)
            verbose = namespace.getBoolean("verbose");
    }

    protected static Path createPathIfNotExists(String path) throws IOException {
        try {
            return Paths.get(path).toRealPath();
        } catch (NoSuchFileException e) {
            File file = new File(path);
            file.mkdirs();
            return file.toPath().toRealPath();
        }
    }

    public abstract void handleArgs();

    protected File getLocalKernelRepository() throws Exception {
        if (localKernelRepository != null) return localKernelRepository;

        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win"))
            return createPathIfNotExists("C:\\ProgramData\\PROS\\kernels").toFile();
        else if (os.contains("mac"))
            throw new Exception("OS X is not yet a supported operating system. Please wait patiently.");
        else if (os.contains("nix") || os.contains("nux") || os.contains("aix"))
            return createPathIfNotExists(String.format("/home/%s/pros/kernels", System.getProperty("user.name")))
                    .toFile();

        throw new Exception("Unrecognized Operating System. Please use *nix, OSX, or Windows.");
    }

    protected Class<?> getKernelLoader(String kernel) {
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

        return kernelLoaderClass;
    }
}
