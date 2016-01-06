/*******************************************************************************
 * Copyright (c) 2015, Purdue University ACM SIG BOTS.
 * All rights reserved.
 * <p>
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * <p>
 * * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * * Neither the name of the Purdue University ACM SIG BOTS nor the
 * names of its contributors may be used to endorse or promote products
 * derived from this software without specific prior written permission.
 * <p>
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

package edu.purdue.sigbots.ros.cli.updater;

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

@SuppressWarnings("WeakerAccess")
public class PROSActions {
    private static final Path SETTINGS_PATH = Paths.get(System.getProperty("user.home"), ".pros", "cli.settings");
    private final boolean verbose;
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
        setUpdateSite(updateSite, true);
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
            PROSSettings settings = new PROSSettings(SETTINGS_PATH);
            settings.setUpdateSite(updateSite);
            try {
                settings.serialize();
            } finally {
                this.updateSite = updateSite;
            }
        } else {
            this.updateSite = updateSite;
        }
    }

    /**
     * @return A suggested/default update site. Not used by PROSActions except as a suggestion.
     */
    public URL suggestUpdateSite() {
        try {
            return new URL("https://raw.githubusercontent.com/purduesigbots/purdueros-kernels/master");
        } catch (MalformedURLException ignored) { // shouldn't happen, ever.
            return null;
        }
    }
    // </editor-fold>

    // <editor-fold desc="Local Kernel Repository Methods">

    /**
     * @return Lazily-loaded or cached local kernel repository Path
     */
    public Path getLocalRepositoryPath() {
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
        setLocalKernelRepository(localKernelRepository, true);
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
            PROSSettings settings = new PROSSettings(SETTINGS_PATH);
            settings.setKernelDirectory(localKernelRepository);
            Files.createDirectories(localKernelRepository);
            try {
                settings.serialize();
            } finally {
                this.localKernelRepository = localKernelRepository;
            }
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
     * @throws IOException an IOException is thrown if there was an exception accessing the local repository
     */
    private List<String> getLocalKernels() throws IOException {
        Files.createDirectories(getLocalRepositoryPath());
        return Files.list(getLocalRepositoryPath())
                .filter(f -> Files.isDirectory(f))
                .map(p -> p.getFileName().toString())
                .collect(Collectors.toList());
    }

    /**
     * @return Returns a list of the names of kernels available on the update site, as determined by the kernels.list
     * @throws IOException An IOException is thrown if there was an error downloading the kernels.list
     */
    private List<String> getOnlineKernels() throws IOException {
        URL kernelsListURL = new URL(getUpdateSite().toExternalForm() + "/kernels.list");
        URLConnection urlConnection = kernelsListURL.openConnection();
        urlConnection.connect();
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
        ArrayList<String> kernelList = new ArrayList<>();
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            kernelList.add(line);
        }
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
    public Map<String, Integer> getAllKernels() throws IOException {
        HashMap<String, Integer> map = new HashMap<>();
        getLocalKernels().forEach(k -> map.put(k,
                map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_LOCAL.getValue()));
        getOnlineKernels().forEach(k -> map.put(k,
                map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_ONLINE.getValue()));
        return map;
    }

    /**
     * @param kernel A regular expression to match kernels to
     * @return Returns a map of Strings to KernelAvailabilityFlag values. Each String corresponds to an available kernel
     * anywhere. The associated value with each string is a composite KernelAvailabilityFlag. See implementation note.
     * @throws IOException Thrown if there was an issue fetching the online kernels (See <code>getOnlineKernels</code>
     * @implNote See implementation note for getAllKernels()
     */
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
     * Silently fails to add all local or all update site kernels. May result in only local, only update site, or no
     * kernels to be in the map.
     *
     * @return Returns a map of Strings to KernelAvailabilityFlag values. Each String corresponds to an available kernel
     * anywhere. The associated value with each string is a composite KernelAvailabilityFlag. See implementation note
     * @implNote See implementation note for getAllKernels()
     */
    public Map<String, Integer> getAllKernelsForce() {
        Map<String, Integer> map = new HashMap<>();
        try {
            getLocalKernels().forEach(k -> map.put(k,
                    map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_LOCAL.getValue()));
        } catch (IOException e) {
            e.printStackTrace(err);
        }
        try {
            getOnlineKernels().forEach(k -> map.put(k,
                    map.getOrDefault(k, 0) | KernelAvailabilityFlag.KERNEL_AVAILABLE_ONLINE.getValue()));
        } catch (IOException e) {
            e.printStackTrace(err);
        }
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
    public Set<String> resolveKernelUpdateRequest(String request) throws IOException {
        HashSet<String> set = new HashSet<>();
        if (request == null || request.isEmpty() || request.equalsIgnoreCase("all")) {
            set.addAll(getOnlineKernels());
        } else if (request.equalsIgnoreCase("latest")) {
            URL latestKernelURL = new URL(getUpdateSite().toExternalForm() + "/latest.kernel");
            URLConnection urlConnection = latestKernelURL.openConnection();
            urlConnection.connect();
            try (BufferedReader bufferedReader =
                         new BufferedReader(new InputStreamReader(urlConnection.getInputStream()))) {
                set.add(bufferedReader.readLine());
            }
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
     *                <p>
     *                If request is "latest", then the highest alphanumeric kernel is returned.
     *                A singleton is guaranteed in this case.
     * @return A set of valid Strings representing kernels that can be targeted (may be empty)
     */
    public Set<String> resolveKernelLocalRequest(String request) throws IOException {
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

    /**
     * Finds an appropriate Loader for the given kernel directory. The class is expected to be
     * edu.purdue.sigbots.ros.cli.kernels.2b10Loader where 2b10 is the name of the kernel directory (the kernel version)
     *
     * @param kernelDirectory A path to a kernel directory
     * @return A class object that extends Loader
     */
    private Class<? extends Loader> findKernelLoader(Path kernelDirectory) {
        Class<?> kernelLoaderClass = DefaultLoader.class;
        try {
            URL kernelUrl = kernelDirectory.toUri().toURL();
            ClassLoader classLoader = new URLClassLoader(new URL[]{kernelUrl});
            kernelLoaderClass = classLoader.loadClass(
                    String.format("%s.%sLoader", this.getClass().getPackage().toString(), kernelDirectory.getFileName())
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
        // Should be able to safely ignore the unchecked warning as kernelLoaderClass.isAssignableFrom ensures it is ok to cast
        //noinspection unchecked
        return (Class<? extends Loader>) kernelLoaderClass;
    }

    /**
     * Create a Loader object
     *
     * @param kernelLoaderClass A class that extends Loader usually found by findKernelLoader
     * @return A Loader object, or, if something went wrong, null (the stack trace will be printed to err if verbose is set to true)
     */
    public Loader createLoader(Class<? extends Loader> kernelLoaderClass) {
        try {
            return kernelLoaderClass.getConstructor(Boolean.class, PrintStream.class, PrintStream.class).newInstance(verbose, out, err);
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            if (verbose) {
                e.printStackTrace(err);
            }
            return null;
        }
    }

    /**
     * @param kernel A valid kernel string
     * @return Returns a resolved path with the kernel appended and does not check if the directory actually exists
     */
    public Path findKernelDirectory(String kernel) {
        return getLocalRepositoryPath().resolve(kernel);
    }
    // </editor-fold>

    // <editor-fold desc="Project load methods">

    /**
     * Creates a project at the specified project location. Any files that already exist will be overwritten
     *
     * @param kernel          A valid kernel string that will be automatically passed to findKernelDirectory
     * @param projectLocation A valid path that is accessible
     * @param environments    A list of strings that specifies the environments to target.
     *                        It is safe to have extra environments in this list.
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public void createProject(String kernel, Path projectLocation, List<String> environments) throws IOException {
        createProject(findKernelDirectory(kernel), projectLocation, environments);
    }

    /**
     * Creates a project at the specified project location. Any files that already exist will be overwritten
     *
     * @param kernelDirectory A valid kernel directory
     * @param projectLocation A valid path that is accessible
     * @param environments    A list of strings that specifies the environments to target.
     *                        It is safe to have extra environments in this list.
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public void createProject(Path kernelDirectory, Path projectLocation, List<String> environments) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelDirectory);
        Loader loader = createLoader(kernelLoaderClass);
        if (loader != null) {
            loader.createProject(kernelDirectory, projectLocation, environments);
        } else {
            out.printf("Error loading %s. Turn on the verbose option to debug\r\n", kernelLoaderClass.getName());
        }
    }

    /**
     * Upgrades a project at the specified project location.
     *
     * @param kernel           A valid kernel string that is passed to findKernelDirectory
     * @param projectDirectory A valid path that is accessible
     * @param environments     A list of strings that specifies the environments to target.
     *                         It is safe to have extra environments in this list.
     *                         If the list is empty, then the desired action of the Loader is to determine which
     *                         environments were previously targeted and upgrade those. May or may not have been
     *                         implemented by the loader.
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public void upgradeProject(String kernel, Path projectDirectory, List<String> environments) throws IOException {
        upgradeProject(findKernelDirectory(kernel), projectDirectory, environments);
    }

    /**
     * Upgrades a project at the specified project location.
     *
     * @param kernelDirectory  A valid kernel directory
     * @param projectDirectory A valid path that is accessible
     * @param environments     A list of strings that specifies the environments to target.
     *                         It is safe to have extra environments in this list.
     *                         If the list is empty, then the desired action of the Loader is to determine which
     *                         environments were previously targeted and upgrade those. May or may not have been
     *                         implemented by the loader.
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public void upgradeProject(Path kernelDirectory, Path projectDirectory, List<String> environments) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelDirectory);
        Loader loader = createLoader(kernelLoaderClass);
        if (loader != null) {
            createLoader(kernelLoaderClass).upgradeProject(kernelDirectory, projectDirectory, environments);
        } else {
            out.printf("Error loading %s. Turn on the verbose option to debug\r\n", kernelLoaderClass.getName());
        }
    }

    /**
     * Lists all environments available for the kernel loader to target
     *
     * @param kernel A valid kernel string that is passed to findKernelDirectory
     * @return A map of string and set of strings where the key is a kernel and the value is a set of targetable environment strings
     * @throws IOException Thrown if there was an issue creating the Loader or accessing the kernel directory
     */
    public Map<String, Set<String>> listEnvironments(String kernel) throws IOException {
        Map<String, Set<String>> environmentsMap = new HashMap<>();
        if (verbose) {
            System.out.printf("Resolved %s to %s\r\n", kernel, resolveKernelLocalRequest(kernel));
        }
        for (String k : resolveKernelLocalRequest(kernel)) {
            environmentsMap.put(k, listEnvironments(findKernelDirectory(k)));
        }
        return environmentsMap;
    }

    /**
     * Lists all environments available for the kernel loader to target
     *
     * @param kernelPath A valid local kernel path
     * @return A map of string and set of strings where the key is a kernel and the value is a set of targetable environment strings
     * @throws IOException Thrown if there was an issue creating the Loader or accessing the kernel directory
     */
    public Set<String> listEnvironments(Path kernelPath) throws IOException {
        Class<? extends Loader> kernelLoaderClass = findKernelLoader(kernelPath);
        Loader loader = createLoader(kernelLoaderClass);
        if (loader != null) {
            return createLoader(kernelLoaderClass).getAvailableEnvironments(kernelPath);
        } else {
            out.printf("Error loading %s. Turn on the verbose option to debug\r\n", kernelLoaderClass.getName());
            return null;
        }
    }
    // </editor-fold>

    // <editor-fold desc="Local kernel management methods">

    /**
     * Downloads a specified kernel. This method does not check if kernel is on kernels.list
     * <p>
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
        Path localKernel = getLocalRepositoryPath().resolve(kernel);

        if (Files.exists(localKernel)) { // delete already existing kernel template
            Files.walkFileTree(localKernel, new SimpleFileDeleter(localKernel, verbose));
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

    /**
     * Recursively deletes local kernel directory(s).
     *
     * @param kernel A regular expression to match local kernels to.
     * @throws IOException Thrown if there was an error resolving the kernel request or deleting the directory
     */
    public void deleteKernel(String kernel) throws IOException {
        if (kernel == null || kernel.isEmpty()) {
            return;
        }

        for (String k : resolveKernelLocalRequest(kernel)) {
            deleteKernel(findKernelDirectory(k));
        }
    }

    /**
     * Recursively deletes a local kernel directory (or really any directory)
     *
     * @param kernelDirectory A path to a local kernel directory
     * @throws IOException Thrown if there was an error deleting the directory
     */
    public void deleteKernel(Path kernelDirectory) throws IOException {
        Files.walkFileTree(kernelDirectory, new SimpleFileDeleter(kernelDirectory, verbose));
    }
    // </editor-fold>
}
