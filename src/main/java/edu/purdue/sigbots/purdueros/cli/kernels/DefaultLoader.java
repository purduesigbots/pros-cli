package edu.purdue.sigbots.purdueros.cli.kernels;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;


public class DefaultLoader extends Loader {
    public DefaultLoader(Path projectPath, Path kernelPath, List<String> environments) {
        super(projectPath, kernelPath, environments);
    }

    @Override
    public void createProject(boolean force) throws IOException {
        System.out.printf("Creating project in %s from template at %s\r\n", projectPath.toString(), kernelPath.toString());
    }

    @Override
    public void upgradeProject(boolean force) throws IOException {
        System.out.printf("Upgrading project in %s from template at %s\r\n", projectPath.toString(), kernelPath.toString());

    }

    @Override
    public List<String> listAvailableEnvironments() {
        return Arrays.asList("none", "eclipse");
    }
}
