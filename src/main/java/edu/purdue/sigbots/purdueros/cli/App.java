package edu.purdue.sigbots.purdueros.cli;

import edu.purdue.sigbots.purdueros.cli.kernels.DefaultLoader;
import edu.purdue.sigbots.purdueros.cli.kernels.Loader;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.action.StoreArgumentAction;
import net.sourceforge.argparse4j.impl.action.StoreTrueArgumentAction;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

@SuppressWarnings({"ResultOfMethodCallIgnored", "unchecked"})
class App {
    private static final String OS_WINDOWS = "windows";
    private static final String OS_NIX = "nix";
    private static final String OS_OSX = "osx";
    private static final String FILE_SEP = System.getProperty("file.separator");

    public static void main(String[] arguments) throws Exception {
        ArgumentParser parser;
        if (arguments.length == 0)
            parser = ArgumentParsers.newArgumentParser("pros");
        else
            parser = ArgumentParsers.newArgumentParser(arguments[0]);
        parser.defaultHelp(true);
        parser.description("Create and upgrade PROS projects.");

        parser.addArgument("-v", "--version", "-k", "--kernel").nargs(1).metavar("V")
                .help("Kernel version to create or upgrade project to.");
        parser.addArgument("directory").nargs("?").setDefault(System.getProperty("user.dir"))
                .help("Directory to create or upgrade. Defaults to current directory.");
        parser.addArgument("-s", "--site").metavar("SITE")
                .setDefault("https://raw.githubusercontent.com/edjubuh/purdueros-kernels/master")
                .help("Use a different site to pull kernels from.");
        parser.addArgument("-d", "--download").action(new StoreTrueArgumentAction())
                .help("Forces a redownload of the kernel\\' template. Works even when --kernel is not provided.");
        parser.addArgument("-f", "--force").action(new StoreTrueArgumentAction())
                .help("Deletes all contents in the directory and fills it with a new PROS template.");
        parser.addArgument("-n", "--name", "--project-name").nargs(1).metavar("NAME")
                .help("Name of the project used by the IDE (if applicable). " +
                        "Defaults to the name of the current directory if not specified or discovered");
        parser.addArgument("-l", "--list-kernels").action(new StoreTrueArgumentAction())
                .help("Lists all available kernels, either downloaded or available online.");
        parser.addArgument("-e", "--env", "--environment").action(new StoreArgumentAction()).nargs("*").metavar("ENV")
                .help("Sets environments to set up for. May mix and match options." +
                        "Choices determined by kernel loader. Default ones are 'eclipse', 'vs-code', 'sublime'. " +
                        "Blank or 'none' sets up no default environments - none trumps all.")
                .setDefault("none");


        parser.addArgument("--verbose").action(new StoreTrueArgumentAction()).help("Prints verbose debug information");

        Namespace args = null;
        try {
            args = parser.parseArgs(arguments);
        } catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }

        boolean verbose = args.getBoolean("verbose");
        String site = args.getString("site");
        if (site.endsWith("/")) site = site.substring(0, site.length() - 1);

        String os = determineOS();

        File kernelRepository = findKernelRepository(os);
        if (verbose) System.out.println("Kernel directory is " + kernelRepository.toString());

        if (args.getBoolean("list_kernels")) {
            System.out.println("Downloading and checking locally available kernels...");
            String[] availableKernels = getAvailableKernels(site, kernelRepository);
            System.out.println(Arrays.toString(availableKernels));
            System.exit(0);
        }

        String kernel = args.getString("version");
        if (kernel == null || kernel.isEmpty()) kernel = "[]";
        kernel = determineKernel(kernel.substring(1, kernel.length() - 1), site, kernelRepository, verbose);

        // Give up if we don't have a target kernel
        if (kernel == null || kernel.isEmpty()) {
            System.err.println("Error: Could not determine a target kernel.");
            System.exit(1);
        }


        String[] kernelDirectories = getLocalKernelDirectories(kernelRepository);

        // determine if we have the downloaded kernel, if not: download it
        if (!Arrays.asList(kernelDirectories).contains(kernel)) {
            if (verbose) System.out.println(kernel + " must be downloaded");
            URL url = new URL(site + "/" + kernel + ".zip");
            try {
                ZipInputStream zipInputStream = new ZipInputStream(url.openStream());
                File kernelDir = new File(kernelRepository, kernel);
                if (!kernelDir.exists()) kernelDir.mkdirs();
                ZipEntry zipEntry;
                while ((zipEntry = zipInputStream.getNextEntry()) != null) {
                    // Decompress downloaded zip entry by entry
                    if (zipEntry.getName().endsWith("/")) continue; // skip folders, they will be created from the files

                    File newFile = new File(kernelDir, zipEntry.getName());
                    if (verbose) {
                        System.out.format("Decompressing %s to %s\n", zipEntry.getName(), kernelDir.toPath().toString());
                    }

                    new File(newFile.getParent()).mkdirs(); // make directory structure to the file

                    FileOutputStream fileOutputStream = new FileOutputStream(newFile);

                    // write to the file
                    int len;
                    byte[] buffer = new byte[1024];
                    while ((len = zipInputStream.read(buffer)) > 0) {
                        fileOutputStream.write(buffer, 0, len);
                    }

                    fileOutputStream.close();
                }

                zipInputStream.closeEntry();
                zipInputStream.close();
            } catch (IOException e) {
                System.out.println("Unable to download requested kernel at " + url.toString());
            }
        }
        if (Arrays.asList(kernelDirectories).contains(kernel)) {
            if (verbose) {
                System.out.println(kernel + " is available locally.");
            }
        } else { // give up we don't have a kernel or a locally available kernel yet
            System.err.println("Error: Could not obtain kernel " + kernel + ". Unable to download and not avaialable locally.");
            System.exit(2);
        }

        if (verbose) System.out.println("Kernel directory is " + kernelRepository + FILE_SEP + kernel + "\n");

        // Resolve directory. Create the path if it doesn't exist.
        Path projectDirectory;
        boolean directoryExisted = true;
        try {
            projectDirectory = createPathIfNotExists(args.getString("directory"));
        } catch (NoSuchFileException e) {
            System.err.print("Directory not found. Creating...");
            directoryExisted = false;
            File file = new File(args.getString("directory"));
            file.mkdirs();
            projectDirectory = file.toPath().toRealPath();
            System.out.println("\rDirectory not found. Created...");
        }

        // Resolve project name
        String projectName = args.getString("name");
        if (projectName == null || projectName.isEmpty())
            projectName = projectDirectory.getFileName().toString();

        Class kernelLoaderClass = DefaultLoader.class;
        try {
            String classFileName = String.format("Kernel%sLoader", kernel);
            URL url = new File(kernelRepository + FILE_SEP + kernel + FILE_SEP)
                    .toURI()
                    .toURL();
            ClassLoader loader = new URLClassLoader(new URL[]{url});
            kernelLoaderClass = loader.loadClass("edu.purdue.sigbots.purdueros.cli.kernels." + classFileName);
            // if (!kernelLoaderClass.isAssignableFrom(Loader.class)) throw new Exception();
        } catch (Exception e) { // If the class didn't load properly, use the default class
            if (verbose) System.out.println("Could not find custom kernel loader.");
        }

        Loader kernelLoader = (Loader) kernelLoaderClass
                .getConstructor(String.class, String.class, String.class, String.class)
                .newInstance(projectDirectory.toString(),
                        kernelRepository + FILE_SEP + kernel,
                        projectName,
                        args.getString("env"));

        if (verbose) {
            System.out.println("Using " + kernelLoader.getClass().getTypeName() + " kernel loader");
            System.out.println("Project directory is " + new File(projectDirectory.toUri()).getAbsolutePath());
            System.out.println();
        }

        if (directoryExisted) {
            if (args.getBoolean("force")) {
                if (verbose) {
                    System.out.println("Overwriting folder structure in " + projectDirectory.toString());
                }
                System.out.println("Overwriting directory.");
                kernelLoader.createProject();
            } else if (kernelLoader.isUpgradeableProject()) {
                if (verbose) {
                    System.out.println("Upgrading project in " + projectDirectory.toString());
                }
                kernelLoader.upgradeProject();
            } else { // directory is not a valid PROS project (likely missing libccos.a)
                System.err.println("Unable to upgrade this project. " +
                        "Use force (-f, --force) to overwrite existing folder structure");
                System.exit(4);
            }
        } else {
            if (verbose) {
                System.out.println("Creating project in " + projectDirectory.toString());
            }
            kernelLoader.createProject();
        }
    }


    /**
     * Returns a Path, and creates it if does not exist. The Path returned is evaluated by toRealPath()
     *
     * @param path Path to crate
     * @return A valid real Path
     * @throws IOException
     */
    private static Path createPathIfNotExists(String path) throws IOException {
        try {
            return Paths.get(path).toRealPath();
        } catch (NoSuchFileException e) {
            File file = new File(path);
            file.mkdirs();
            return file.toPath().toRealPath();
        }
    }

    private static String downloadString(URL url) throws IOException {
        String string = "";
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()))) {
            String s;
            while ((s = reader.readLine()) != null)
                string += s + "\n";
        }
        return string;
    }

    private static String determineOS() throws Exception {
        // Determine OS for later file operations
        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win"))
            os = OS_WINDOWS;
        else if (os.contains("mac"))
            os = OS_OSX;
        else if (os.contains("nix") || os.contains("nux") || os.contains("aix"))
            os = OS_NIX;
        else
            throw new Exception("Unrecognized Operating System. Please use *nix, OSX, or Windows.");
        return os;
    }

    private static File findKernelRepository(String os) throws Exception {
        File kernelDirectory;
        switch (os) {
            case OS_WINDOWS:
                kernelDirectory = createPathIfNotExists("C:\\ProgramData\\PROS\\kernels").toFile();
                break;
            case OS_NIX:
                kernelDirectory = createPathIfNotExists(
                        String.format("/home/%s/pros/kernels", System.getProperty("user.name")))
                        .toFile();
                break;
            /* TODO: OS_OSX support for kernel directory */
            default:
                throw new Exception("Unknown or unsupported OS. Could not find or locate a kernels repository.");
        }
        return kernelDirectory;
    }

    private static String[] getAvailableKernels(String site, File kernelDirectory) throws IOException {
        URL url = new URL(site + "/kernels.list");
        HashSet<String> kernels = new HashSet<>();
        try {
            Collections.addAll(kernels, downloadString(url).split("\r\n"));
        } catch (IOException ignored) {
        }

        Collections.addAll(kernels, kernelDirectory.list(((dir, name) -> new File(dir, name).isDirectory())));
        return kernels.toArray(new String[kernels.size()]);
    }

    private static String determineKernel(String kernel, String site, File kernelRepository, boolean verbose) throws MalformedURLException {
        // Try to fetch the latest kernel version online if kernel is undefined
        if (kernel == null || kernel.isEmpty()) {
            if (verbose) System.out.println("Determining latest kernel from internet");
            URL url = new URL(site + "/latest.kernel");
            try {
                kernel = downloadString(url).trim();
                if (verbose) System.out.println("Latest kernel version is " + kernel);
            } catch (IOException e) {
                if (verbose) System.out.println("Unable to fetch kernel from " + url.toExternalForm());
            }
        }

        // Couldn't fetch latest online, look for highest (alphabetically) local kernel
        String[] kernelDirectories = getLocalKernelDirectories(kernelRepository);
        if (kernel == null || kernel.isEmpty()) {
            if (verbose) System.out.println("All local kernels: " + Arrays.toString(kernelDirectories));
            if (kernelDirectories.length > 0)
                kernel = kernelDirectories[kernelDirectories.length - 1];
        }
        return kernel;
    }

    private static String[] getLocalKernelDirectories(File kernelRepository) {
        String[] kernelDirectories = kernelRepository.list(((dir, name) -> new File(dir, name).isDirectory()));
        Arrays.sort(kernelDirectories);
        return kernelDirectories;
    }
}
