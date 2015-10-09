package edu.purdue.sigbots.purdueros.cli.kernels;

import java.io.IOException;

public interface LoaderInterface {
    void createProject(String projectPath, String kernelPath, String projectName) throws IOException;

    void upgradeProject(String projectPath, String kernelPath, String projectName) throws IOException;
}
