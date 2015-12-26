package edu.purdue.sigbots.purdueros.cli.commands;

import edu.purdue.sigbots.purdueros.cli.kernels.Loader;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.io.FileUtils;

import java.io.*;
import java.net.URL;
import java.nio.file.Path;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class FetchCommand extends Command {

    public FetchCommand(Namespace namespace) {
        super(namespace);
    }

    @Override
    public void handleArgs() {
        if (verbose) System.out.printf("Resolving kernel '%s'\r\n", namespace.getString("kernel"));
        final String kernel = resolveKernel(namespace.getString("kernel"), namespace.getString("site"));
        if (verbose) System.out.printf("Kernel resolved to '%s'\r\n", kernel);

        if (namespace.getBoolean("download")) {
            try {
                List<String> onlineKernels = Arrays.asList(
                        downloadString(new URL(namespace.getString("site") + "/kernels.list")).split("\n"));
                onlineKernels.stream().filter(onlineKernel -> !onlineKernel.matches(kernel)).forEach(onlineKernels::remove);
                for (String onlineKernel : onlineKernels) {
                    System.out.printf("Downloading '%s'\r\n", onlineKernel);
                    downloadKernel(onlineKernel, namespace.getString("site"));
                }
                if (onlineKernels.size() == 0)
                    System.out.println("No matching kernels found at " + namespace.getString("site"));
            } catch (IOException e) {
                System.err.println("Unable to connect to site " + e.getMessage());
                if (verbose) e.printStackTrace();
            }
            return;
        } else if (namespace.getBoolean("environments")) {
            String environmentKernel = null;
            try {
                if (verbose) System.out.printf("Checking kernels that match '%s' locally.", kernel);
                List<File> localKernels = Arrays.asList(getLocalKernelRepository().listFiles(f -> f.isDirectory() && f.getName().matches(kernel)));
                if (localKernels.size() == 0) {
                    System.out.println("No local kernels matching " + kernel + " found.");
                    System.exit(-1);
                } else if (localKernels.size() > 1) {
                    System.err.println("More than one kernels match " + kernel);
                    System.err.println(localKernels.toString());
                    System.exit(-1);
                } else {
                    assert localKernels.size() == 1;
                    environmentKernel = localKernels.get(0).getName();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            if (verbose) System.out.println("Determining environments available for " + environmentKernel);
            try {
                Loader kernelLoader = (Loader) getKernelLoader(kernel)
                        .getConstructor(Path.class, Path.class, List.class)
                        .newInstance(null, null, null);
                System.out.printf("Environments available to %s:\r\n", kernel);
                kernelLoader.listAvailableEnvironments().forEach(System.out::println);
            } catch (Exception e) {
                e.printStackTrace();
            }
            return;
        } else if (namespace.getBoolean("clean")) {
            try {
                List<File> localKernels = Arrays.asList(getLocalKernelRepository().listFiles(f -> f.isDirectory() && f.getName().matches(kernel)));
                System.out.printf("Will delete the following directories: %s? [y/N] ", localKernels.toString());
                if (new Scanner(System.in).nextLine().equalsIgnoreCase("y")) {
                    System.out.println("Deleting...");
                    for (File localKernel : localKernels)
                        FileUtils.deleteDirectory(localKernel);
                } else {
                    System.out.println("Did not delete directories.");
                }
                System.exit(1);
            } catch (Exception e) {
                e.printStackTrace();
                System.exit(1);
            }
        }

        try {
            List<File> localKernels = Arrays.asList(getLocalKernelRepository().listFiles(f -> f.isDirectory() && f.getName().matches(kernel)));

            List<String> onlineKernels = new ArrayList<>();
            try {
                onlineKernels = Arrays.asList(
                        downloadString(new URL(namespace.getString("site") + "/kernels.list")).split("\n"));
                onlineKernels.stream().filter(onlineKernel -> !onlineKernel.matches(kernel)).forEach(onlineKernels::remove);
            } catch (IOException e) {
                System.err.println("Unable to connect to site " + e.getMessage());
                if (verbose) e.printStackTrace();
            }

            for (File localKernel : localKernels)
                if (onlineKernels.contains(localKernel.getName())) {
                    System.out.println(localKernel.getName() + " [local+online]");
                    onlineKernels.remove(localKernel.getName());
                } else {
                    System.out.println(localKernel.getName() + " [local]");
                }
            for (String onlineKernel : onlineKernels)
                System.out.println(onlineKernel + " [online]");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void downloadKernel(String kernel, String site) {
        if (verbose) System.out.println(kernel + " must be downloaded");
        try {
            URL url = new URL(site + "/" + kernel + ".zip");
            ZipInputStream zipInputStream = new ZipInputStream(url.openStream());
            File kernelDir = new File(getLocalKernelRepository(), kernel);
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
            System.out.println("Unable to download requested kernel at " + site + "/" + kernel + ".zip");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private String resolveKernel(String kernel, String site) {
        if (kernel.equalsIgnoreCase("latest")) {
            try {
                HashSet<String> kernels = new HashSet<>();
                for (File localKernel : getLocalKernelRepository().listFiles(File::isDirectory))
                    kernels.add(localKernel.getName());
                try {
                    Collections.addAll(kernels, downloadString(new URL(site)).split("\n"));
                } catch (IOException e) {
                    System.err.println("Unable to connect to site " + e.getMessage());
                    if (verbose) e.printStackTrace();
                }

                String[] kernelArray = kernels.toArray(new String[kernels.size()]);
                Arrays.sort(kernelArray);
                return kernelArray[kernelArray.length - 1];
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        if (kernel.equalsIgnoreCase("all"))
            return ".+";
        return kernel;
    }

    private String downloadString(URL url) throws IOException {
        String result = "";
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()))) {
            String s;
            while ((s = reader.readLine()) != null)
                result += s + "\n";
        }
        return result;
    }
}
