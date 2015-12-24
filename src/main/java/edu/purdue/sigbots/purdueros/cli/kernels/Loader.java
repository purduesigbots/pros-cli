package edu.purdue.sigbots.purdueros.cli.kernels;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

public abstract class Loader {
    final static String FILE_SEP = System.getProperty("file.separator");
    String projectPath;
    String kernelPath;
    String projectName;
    List<String> environments;

    Loader(String projectPath, String kernelPath, String projectName, String environments) {
        this.projectPath = projectPath;
        this.kernelPath = kernelPath;
        this.projectName = projectName;
        this.environments = Arrays.asList(environments.split(" "));

        if (!projectPath.endsWith(FILE_SEP)) this.projectPath += FILE_SEP;
        if (!kernelPath.endsWith(FILE_SEP)) this.kernelPath += FILE_SEP;
        if (this.projectName == null) this.projectPath = "";
    }

    /**
     * Duplicates template project one-for-one and will delete any existing contents if it exists
     *
     * @throws IOException
     */
    public abstract void createProject() throws IOException;

    /**
     * Upgrades all relevant files in the project
     *
     * @throws IOException
     */
    public abstract void upgradeProject() throws IOException;

    /**
     * Determines if project is valid for upgrade by checking directory for some known file
     * @throws IOException
     */
    public abstract boolean isUpgradeableProject() throws IOException;
}
