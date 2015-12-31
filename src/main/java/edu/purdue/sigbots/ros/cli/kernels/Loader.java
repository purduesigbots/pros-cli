package edu.purdue.sigbots.ros.cli.kernels;

import com.sun.istack.internal.Nullable;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;

public abstract class Loader {
    protected final boolean verbose;
    protected final PrintStream out;
    protected final PrintStream err;

    public Loader(Boolean verbose, PrintStream out, PrintStream err) {
        this.verbose = verbose;
        this.out = out;
        this.err = err;
    }

    public abstract void createProject(Path kernelPath, Path projectPath, @Nullable List<String> environments) throws IOException;

    public abstract void upgradeProject(Path kernelPath, Path projectPath, @Nullable List<String> environments) throws IOException;

    public abstract Set<String> getAvailableEnvironments(Path kernelPath) throws IOException;
}
