package edu.purdue.sigbots.ros.cli.updater;

import com.sun.istack.internal.NotNull;
import com.sun.istack.internal.Nullable;
import edu.purdue.sigbots.ros.cli.SimpleFileDeleter;
import edu.purdue.sigbots.ros.cli.kernels.DefaultLoader;
import edu.purdue.sigbots.ros.cli.kernels.Loader;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.net.URLConnection;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class PROSActions {
    protected static final Path SETTINGS_PATH = Paths.get(System.getProperty("user.home"), ".pros", "cli.settings");
    protected final boolean verbose;
    private final PrintStream out;
    private final PrintStream err;

    private Path localKernelRepository;
    private URL updateSite;

    // <editor-fold desc="Constructors">

    /**
     * Creates a default PROSActions object without verbose output and prints to System.out/System.err
     */
    public PROSActions() {
        this(false, System.out, System.err);
    }

    /**
     * Creates a PROSActions object
     *
     * @param verbose sets on or off verbose output
     * @param out     output stream (typically System.out)
     * @param err     error stream (typically System.err)
     */
    public PROSActions(boolean verbose, PrintStream out, PrintStream err) {
        this.verbose = verbose;
        this.out = out;
        this.err = err;
    }

    /**
     * @param updateSite A temporary updateSite that overrides the default updateSite URL
     */
    public PROSActions(boolean verbose, PrintStream out, PrintStream err, URL updateSite) {
        this(verbose, out, err);
        this.updateSite = updateSite;
    }
    // </editor-fold>

    // <editor-fold desc="Update Site Methods">

    /**
     * @return Lazily-loaded or cached update site
     */
    public URL getUpdateSite() {
        if (updateSite != null) {
            return updateSite;
        }

        PROSSettings settings = new PROSSettings(SETTINGS_PATH);
        return updateSite = settings.getUpdateSite();
    }

    /**
     * Sets and serializes the update site
     *
     * @throws IOException An IOException is thrown if there is an issue serializing the settings
     */
    public void setUpdateSite(URL updateSite) throws IOException {
        PROSSettings settings = new PROSSettings(SETTINGS_PATH);
        settings.setUpdateSite(updateSite);
        try {
            settings.serialize();
        } finally {
            this.updateSite = updateSite;
        }
    }

    /**
     * Sets and optionally serializes the update site
     *
     * @param updateSite New update site to be used by this PROSActions
     * @param serialize  Determines whether or not to serialize the new value
     * @throws IOException Thrown if and only if serialized. May be safely ignored if set to false
     */
    public void setUpdateSite(URL updateSite, boolean serialize) throws IOException {
        if (serialize) {
            setUpdateSite(updateSite);
        } else {
            this.updateSite = updateSite;
        }
    }

    /**
     * @return A suggested/default update site. Not used by PROSActions except as a suggestion.
     */
    public URL suggestUpdateSite() {
        try {
            return new URL("https://raw.githubusercontent.com/edjubuh/purdueros-kernels/master");
        } catch (MalformedURLException ignored) {
            return null;
        }
    }

    /**
     * Downloads a specified kernel.
     * Prints a line to the output stream each time for every file/directory to extract (if verbose)
     *
     * @param kernel A valid kernel string
     * @throws IOException An IOException is thrown if the kernel did not exist at the update site
     *                     or if there was an issue extracting the kernel to the local kernel repository
     * @implNote It is recommended to verify that the kernel exists at the update site before calling this method
     * use <code>resolveKernelUpdateRequest(kernel)</code> to determine if kernel is valid
     */
    public void downloadKernel(String kernel) throws IOException {
        URL kernelUrl = new URL(String.format("%s/%s.zip", getUpdateSite().toString(), kernel));
        Path localKernel = getLocalKernelRepository().resolve(kernel);
        if (Files.exists(localKernel)) {
            Files.walkFileTree(localKernel, new SimpleFileDeleter());
        }
        URLConnection urlConnection = kernelUrl.openConnection();
        urlConnection.connect();
        try (ZipInputStream zipInputStream = new ZipInputStream(urlConnection.getInputStream())) {
            ZipEntry zipEntry;
            while ((zipEntry = zipInputStream.getNextEntry()) != null) {
                if (verbose) {
                    out.printf("Extracting %s\r\n", zipEntry.getName());
                }
                Path zipEntryPath = localKernel.resolve(zipEntry.getName());
                if (zipEntry.isDirectory()) {
                    Files.createDirectories(zipEntryPath);
                } else {
                    Files.createDirectories(zipEntryPath.getParent());
                    Files.copy(zipInputStream, zipEntryPath);
                }
            }
        }
    }

    public void deleteKernel(String kernel) throws IOException {
        if (kernel == null || kernel.isEmpty()) {
            return;
        }
        if (kernel.equalsIgnoreCase("all")) {
            kernel = ".*";
        }

        for (String k : resolveKernelLocalRequest(kernel)) {
            Files.walkFileTree(findKernelDirectory(k), new SimpleFileDeleter());
        }
    }
    // </editor-fold>

    // <editor-fold desc="Local Kernel Repository Methods">

    /**
     * @return Lazily-loaded or cached local kernel repository Path
     */
    public Path getLocalKernelRepository() {
        if (localKernelRepository != null) {
            return localKernelRepository;
        }

        PROSSettings settings = new PROSSettings(SETTINGS_PATH);
        return localKernelRepository = settings.getKernelDirectory();
    }

    /**
     * Sets and serializes the local kernel repository
     *
     * @throws IOException An IOException is thrown if there is an issue serializing the settings
     */
    public void setLocalKernelRepository(Path localKernelRepository) throws IOException {
        PROSSettings settings = new PROSSettings(SETTINGS_PATH);
        settings.setKernelDirectory(localKernelRepository);
        Files.createDirectories(localKernelRepository);
        try {
            settings.serialize();
        } finally {
            this.localKernelRepository = localKernelRepository;
        }
    }

    /**
     * Sets and optionally serializes the local kernel repository
     *
     * @param localKernelRepository New local kernel repository to be used by this PROSActions
     * @param serialize             Determines whether or not to serialize the new value
     * @throws IOException Thrown if and only if serialized. May be safely ignored if set to false
     */
    public void setLocalKernelRepository(Path localKernelRepository, boolean serialize) throws IOException {
        if (serialize) {
            setLocalKernelRepository(localKernelRepository);
        } else {
            this.localKernelRepository = localKernelRepository;
        }
    }

    /**
     * @return A suggested/default local kernel repository. Not used by PROSActions except as a suggestion.
     */
    public Path suggestLocalKernelRepository() {
        return Paths.get(System.getProperty("user.home"), ".pros", "kernels");
    }
    // </editor-fold>

    // <editor-fold desc="Listing Kernels Methods">

    /**
     * @return Returns a list of the names of the directories (kernels) inside the local kernel repository
     */
    public List<String> getLocalKernels() {
        try {
            Files.createDirectories(getLocalKernelRepository());
            return Files.list(getLocalKernelRepository())
                    .filter(f -> Files.isDirectory(f))
                    .map(p -> p.getFileName().toString())
                    .collect(Collectors.toList()); // :) lambdas
        } catch (IOException e) {
            e.printStackTrace(err);
        }
        return null;
    }

    /**
     * @return Returns a list of the names of kernels available on the update site, as determined by the kernels.list
     * @throws IOException An IOException is thrown if there was an error downloading the kernels.list
     */
    @NotNull
    public List<String> getOnlineKernels() throws IOException {
        URL kernelsListURL = new URL(getUpdateSite().toExternalForm() + "/kernels.list");
        URLConnection urlConnection = kernelsListURL.openConnection();
        urlConnection.connect();
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
        ArrayList<String> kernelList = new ArrayList<>();
        String line;
        while ((line = bufferedReader.readLine()) != null)
            kernelList.add(line);
        return kernelList;
    }

    /**
     * @return Returns a map of Strings to KernelAvailabilityFlag values. Each String corresponds to an available kernel
     * anywhere. The associated value with each string is a composite KernelAvailabilityFlag. See implementation note.
     * @throws IOException Thrown if there was an issue fetching the online kernels (See <code>getOnlineKernels</code>
     * @implNote Use <code>KernelAvailabilityFlag.getFlags</code> on the value of each String to get a set of all attributes on the
     * kernel (available online, available locally, or both). To map these flags to a different type than the
     * KernelAvailabilityFlag (i.e. a String), use <code>KernelAvailabilityFlags.valueToMappedSet</code> where the Map parameter maps
     * a KernelAvailabilityFlag to a different type. <code>getSuggestedKernelMapping</code> returns a default mapping
     * to Strings.
     */
    @NotNull
    public Map<String, Integer> getAllKernels() throws IOException {
        HashMap<String, Integer> map = new HashMap<>();
        getLocalKernels().forEach(k -> map.put(k,
                map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_LOCAL.getValue()));
        getOnlineKernels().forEach(k -> map.put(k,
                map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_ONLINE.getValue()));
        return map;
    }

    @NotNull
    public Map<String, Integer> getAllKernels(String kernel) throws IOException {
        if (kernel == null || kernel.equalsIgnoreCase("all") || kernel.matches(" *")) {
            kernel = ".*";
        }
        Map<String, Integer> map = getAllKernels();
        if (kernel.equalsIgnoreCase("latest")) {
            String[] array = map.keySet().toArray(new String[map.keySet().size()]);
            Arrays.sort(array);
            return Collections.singletonMap(array[array.length - 1], map.get(array[array.length - 1]));
        }
        final String finalKernel = kernel;
        map.keySet().stream().filter(k -> !k.matches(finalKernel)).forEach(map::remove);
        return map;
    }

    /**
     * Resolves kernel requests into a set of valid Strings that can be requested
     * according to kernels.list (or latest.kernel)
     *
     * @param request A regular expression to find kernels.
     *                If request is "latest" (non-case matching), then the first line of latest.kernel is returned. A singleton is guaranteed.
     *                If request is "all", then the set of all kernels from <code>getOnlineKernels()</code> is returned.
     * @return A set of valid Strings representing kernels that can be downloaded
     * @throws IOException An IOException if there was a problem fetching either latest.kernel or executing getOnlineKernels
     */
    @NotNull
    public Set<String> resolveKernelUpdateRequest(@NotNull String request) throws IOException {
        HashSet<String> set = new HashSet<>();
        if (request.equalsIgnoreCase("latest")) {
            URL latestKernelURL = new URL(getUpdateSite().toExternalForm() + "/latest.kernel");
            URLConnection urlConnection = latestKernelURL.openConnection();
            urlConnection.connect();
            try (BufferedReader bufferedReader =
                         new BufferedReader(new InputStreamReader(urlConnection.getInputStream()))) {
                set.add(bufferedReader.readLine());
            }
        } else if (request.equalsIgnoreCase("all")) {
            set.addAll(getOnlineKernels());
        } else {
            getOnlineKernels().forEach(s -> {
                if (s.matches(request)) {
                    set.add(s);
                }
            });
        }
        return set;
    }

    /**
     * Resolves kernel requests into a set of valid Strings that can be targeted according to the
     * local kernel repository
     *
     * @param request A regular expression to find kernels.
     *                If request is "latest", then the highest alphanumeric kernel is returned. A singleton is guaranteed.
     * @return A set of valid Strings representing kernels that can be targeted
     * @throws IOException An IOException is thrown if there was a problem accessing the local kernel repository (see getLocalKernels)
     */
    @NotNull
    public Set<String> resolveKernelLocalRequest(@Nullable String request) throws IOException {
        if (request == null || request.isEmpty()) {
            return Collections.emptySet();
        }
        if (request.equalsIgnoreCase("all")) {
            request = ".*";
        }
        HashSet<String> set = new HashSet<>();
        if (request.equalsIgnoreCase("latest")) {
            List<String> kernels = getLocalKernels();
            kernels.sort(String::compareTo);
            if (kernels.size() == 0) {
                return Collections.emptySet();
            }
            set.add(kernels.get(kernels.size() - 1));
        } else {
            final String finalRequest = request;
            getLocalKernels().forEach(s -> {
                if (s.matches(finalRequest)) {
                    set.add(s);
                }
            });
        }
        return set;
    }
    // </editor-fold>

    // <editor-fold desc="Kernel Loader Helper Methods">
    private Class<? extends Loader> findKernelLoader(Path kernelDirectory) {
        Class<?> kernelLoaderClass = DefaultLoader.class;
        try {
            URL kernelUrl = kernelDirectory.toUri().toURL();
            ClassLoader classLoader = new URLClassLoader(new URL[]{kernelUrl});
            kernelLoaderClass = classLoader.loadClass(
                    String.format("%s.%s", this.getClass().getPackage().toString(), kernelDirectory.getFileName())
            );
            if (!kernelLoaderClass.isAssignableFrom(Loader.class)) {
                if (verbose) {
                    err.printf("The class found, %s, does not extend the Loader abstract class. " +
                            "Contact custom loader developer.", kernelLoaderClass.getName());
                }
                kernelLoaderClass = DefaultLoader.class;
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            if (verbose) {
                out.println("Could not find a custom kernel loader.");
            }
        }
        if (verbose) {
            out.printf("Using %s kernel loader\r\n", kernelLoaderClass.getSimpleName());
        }
        return (Class<? extends Loader>) kernelLoaderClass;
    }

    public Loader createLoader(Class<? extends Loader> kernelLoaderClass)
            throws NoSuchMethodException, IllegalAccessException, InvocationTargetException, InstantiationException {
        return kernelLoaderClass.getConstructor(Boolean.class, PrintStream.class, PrintStream.class).newInstance(verbose, out, err);
    }

    public Path findKernelDirectory(String kernel) {
        return getLocalKernelRepository().resolve(kernel);
    }
    // </editor-fold>

    // <editor-fold desc="Project load methods">
    public void createProject(String kernel, Path projectLocation, List<String> environments) throws IOException {
        createProject(findKernelDirectory(kernel), projectLocation, environments);
    }

    public void createProject(Path kernelDirectory, Path projectLocation, List<String> environments) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelDirectory);
        try {
            createLoader(kernelLoaderClass).createProject(kernelDirectory, projectLocation, environments);
        } catch (InstantiationException | NoSuchMethodException | InvocationTargetException | IllegalAccessException e) {
            e.printStackTrace(err);
        }

    }

    public void upgradeProject(String kernel, Path projectPath, List<String> environments) throws IOException {
        upgradeProject(findKernelDirectory(kernel), projectPath, environments);
    }

    public void upgradeProject(Path kernelDirectory, Path projectLocation, List<String> environments) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelDirectory);
        try {
            createLoader(kernelLoaderClass).upgradeProject(kernelDirectory, projectLocation, environments);
        } catch (NoSuchMethodException | InstantiationException | InvocationTargetException | IllegalAccessException e) {
            e.printStackTrace();
        }
    }

    public Map<String, Set<String>> listEnvironments(String kernel) throws IOException {
        Map<String, Set<String>> environmentsMap = new HashMap<>();
        if (verbose) {
            System.out.printf("Resolved %s to %s\r\n", kernel, resolveKernelLocalRequest(kernel));
        }
        for (String k : resolveKernelLocalRequest(kernel)) {
            Class<? extends Loader> kernelLoaderClass = findKernelLoader(findKernelDirectory(k));
            try {
                environmentsMap.put(k,
                        createLoader(kernelLoaderClass).getAvailableEnvironments(findKernelDirectory(k)));
            } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException | InstantiationException e) {
                e.printStackTrace();
            }
        }
        return environmentsMap;
    }

    public Set<String> listEnvironments(Path kernelPath) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelPath);
        try {
            return createLoader(kernelLoaderClass).getAvailableEnvironments(kernelPath);
        } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException | InstantiationException e) {
            e.printStackTrace();
        }
        return null;
    }


    // </editor-fold>
}
