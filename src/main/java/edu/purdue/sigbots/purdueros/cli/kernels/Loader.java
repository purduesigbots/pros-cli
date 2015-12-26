package edu.purdue.sigbots.purdueros.cli.kernels;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

public abstract class Loader {
    protected final static String FILE_SEP = System.getProperty("file.separator");
    protected Path projectPath;
    protected Path kernelPath;
    protected List<String> environments;

    public Loader(Path projectPath, Path kernelPath, List<String> environments) {
        this.projectPath = projectPath;
        this.kernelPath = kernelPath;
        this.environments = environments;
    }

    /**
     * Creates a project
     *
     * @param force When set to true, will overwrite existing files.
     *              Otherwise, when a duplicate file is discovered,
     *              the project creation is aborted
     */
    public abstract void createProject(boolean force) throws IOException;

    /**
     * Upgrades a project
     *
     * @param force When set to true, will blindly copy files over and
     *              not check if project is a valid PROS project
     */
    public abstract void upgradeProject(boolean force) throws IOException;

    public abstract List<String> listAvailableEnvironments();
}
