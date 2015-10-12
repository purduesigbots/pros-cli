package edu.purdue.sigbots.purdueros.cli.kernels;

import java.io.IOException;

public abstract class Loader {
    protected String projectPath;
    protected String kernelPath;
    protected String projectName;

    public Loader(String projectPath, String kernelPath, String projectName) {
        this.projectPath = projectPath;
        this.kernelPath = kernelPath;
        this.projectName = projectName;
    }

    public abstract void createProject() throws IOException;

    public abstract void upgradeProject() throws IOException;

    public abstract boolean isUpgradeableProject() throws IOException;
}
