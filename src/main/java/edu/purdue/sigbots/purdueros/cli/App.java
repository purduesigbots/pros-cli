package edu.purdue.sigbots.purdueros.cli;

import edu.purdue.sigbots.purdueros.cli.kernels.DefaultLoader;
import edu.purdue.sigbots.purdueros.cli.kernels.Loader;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.action.StoreTrueArgumentAction;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.*;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

@SuppressWarnings({"ResultOfMethodCallIgnored", "unchecked"})
public class App {
    private static final String OS_WINDOWS = "windows";
    private static final String OS_NIX = "nix";
    private static final String OS_OSX = "osx";
    private static final String FILE_SEP = System.getProperty("file.separator");

    public static void main(String[] arguments) throws Exception {
        ArgumentParser parser = ArgumentParsers.newArgumentParser("pros")
                .defaultHelp(true)
                .description("Create and upgrade PROS projects.");
        parser.addArgument("-v", "--version", "-k", "--kernel").nargs(1).metavar("V")
                .help("Kernel version to create or upgrade project to.");
        parser.addArgument("directory").nargs("?").setDefault(System.getProperty("user.dir"))
                .help("Directory to create or upgrade. Defaults to current directory");
        parser.addArgument("-s", "--site").metavar("SITE")
                .setDefault("https://raw.githubusercontent.com/edjubuh/purdueros-kernels/master")
                .help("Use a different site to pull kernels from.");
        parser.addArgument("-d", "--download").action(new StoreTrueArgumentAction())
                .help("Forces a redownload of the kernel\\' template. Works even when --kernel is not provided.");
        parser.addArgument("-f", "--force").action(new StoreTrueArgumentAction())
                .help("Deletes all contents in the directory and fills it with a new PROS template.");
        parser.addArgument("-n", "--name", "--project-name").nargs(1).metavar("NAME")
                .help("Name of the project. Defaults to the name of the current directory");
        parser.addArgument("-l", "--list-kernels").action(new StoreTrueArgumentAction())
                .help("Lists all available kernels, either downloaded or available online.");

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

        // Determine and create if needed the local kernel repository
        File kernelDirectory;
        switch (os) {
            case OS_WINDOWS:
                kernelDirectory = createPathIfNotExists("C:\\ProgramData\\PROS\\kernels").toFile();
                break;
            case OS_NIX:
                kernelDirectory = createPathIfNotExists(String.format("/home/%s/pros/kernels",
                        System.getProperty("user.name"))).toFile();
                break;
            default:
                throw new Exception("Unknown OS. Could not find or locate a kernels repository.");
        }

        if (verbose) System.out.println("Kernel directory is " + kernelDirectory.toString());

        // List kernels only if requested.
        if (args.getBoolean("list_kernels")) {
            String text = "Downloading and checking locally...";
            System.out.print(text);
            URL url = new URL(site + "/kernels.list");
            System.out.println("\r" + text.replaceAll("(?s).", " ") + "\r" + downloadString(url));
            System.exit(0);
        }

        // Start the kernel determination process
        String kernel = args.getString("kernel");

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
        String[] subdirs = kernelDirectory.list((dir, name) -> new File(dir, name).isDirectory());
        Arrays.sort(subdirs);
        if (kernel == null || kernel.isEmpty()) {
            if (verbose) System.out.println("All local kernels: " + Arrays.toString(subdirs));
            if (subdirs.length > 0)
                kernel = subdirs[0];
        }

        // Give up if we still don't have a target kernel
        if (kernel == null || kernel.isEmpty()) {
            System.err.println("Error: Could not determine a target kernel.");
            System.exit(1);
        }

        // determine if we have the downloaded kernel, if not: download it
        if (!Arrays.asList(subdirs).contains(kernel)) {
            if (verbose) System.out.println(kernel + " must be downloaded");
            URL url = new URL(site + "/" + kernel + ".zip");
            try {
                // Make the URL input stream a zip input stream
                ZipInputStream zipInputStream = new ZipInputStream(url.openStream());
                File kernelDir = new File(kernelDirectory, kernel);
                if (!kernelDir.exists()) kernelDir.mkdirs();
                ZipEntry zipEntry;
                while ((zipEntry = zipInputStream.getNextEntry()) != null) { // Decompress downloaded zip entry by entry
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
        if (Arrays.asList(subdirs).contains(kernel)) {
            if (verbose) {
                System.out.println(kernel + " is available locally.");
            }
        } else { // give up we don't have a kernel or a locally available kernel yet
            System.err.println("Error: Could not obtain kernel " + kernel + ". Unable to download and not avaialable locally.");
        }

        if (verbose) System.out.println("Kernel directory is " + kernelDirectory + FILE_SEP + kernel + "\n");

        // Resolve directory. Create the path if it doesn't exist.
        Path directory;
        try {
            directory = createPathIfNotExists(args.getString("directory"));
        } catch (NoSuchFileException e) {
            System.err.print("Directory not found. Creating...");
            File file = new File(args.getString("directory"));
            file.mkdirs();
            directory = file.toPath().toRealPath();
            System.out.println("\rDirectory not found. Created...");
        }

        // Resolve project name
        String projectName = args.getString("name");
        if (projectName == null || projectName.isEmpty())
            projectName = directory.getFileName().toString();

        Class kernelLoaderClass = DefaultLoader.class;
        try {
            URL url = new File(kernelDirectory + FILE_SEP + kernel + FILE_SEP + kernel + ".class").toURI().toURL();
            ClassLoader loader = new URLClassLoader(new URL[]{url});
            kernelLoaderClass = loader.loadClass("edu.purdue.sigbots.purdueros.kernels.loaders." + kernel);
            if (!kernelLoaderClass.isAssignableFrom(Loader.class)) throw new Exception();
        } catch (Exception e) { // If the class didn't load properly, use the default class
        }

        Loader kernelLoader = (Loader) kernelLoaderClass
                .getConstructor(String.class, String.class, String.class)
                .newInstance(directory.toString(), kernelDirectory + FILE_SEP + kernel, projectName);

        if (new File(directory.toUri()).exists()) {
            if (args.getBoolean("force")) {
                if (verbose) {
                    System.out.println("Overwriting folder structure in " + directory.toString());
                }
                kernelLoader.createProject();
            } else if (kernelLoader.isUpgradeableProject()) {
                if (verbose) {
                    System.out.println("Upgrading project in " + directory.toString());
                }
                kernelLoader.upgradeProject();
            } else {
                System.out.println("Unable to upgrade this project. " +
                        "Use force (-f, --force) to overwrite existing folder structure");
            }
        } else {
            if (verbose) {
                System.out.println("Creating project in " + directory.toString());
            }
            kernelLoader.createProject();
        }
    }

    /**
     * Returns a Path, and creates it if does not exist. The Path returned is evaluated by toRealPath()
     *
     * @param path Path to crate
     * @return A valid Path
     * @throws IOException
     */
    static Path createPathIfNotExists(String path) throws IOException {
        try {
            return Paths.get(path).toRealPath();
        } catch (NoSuchFileException e) {
            File file = new File(path);
            file.mkdirs();
            return file.toPath().toRealPath();
        }
    }

    static String downloadString(URL url) throws IOException {
        String string = "";
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()))) {
            String s;
            while ((s = reader.readLine()) != null)
                string += s + "\n";
        }
        return string;
    }
}
