package edu.purdue.sigbots.ros.cli.updater;

import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

public class PROSSettings implements Serializable {
    private String kernelDirectory;
    private URL updateSite;
    private transient Path location;

    public PROSSettings() {
    }

    public PROSSettings(Path location) {
        this.location = location;
        try {
            InputStream inputStream = Files.newInputStream(location, StandardOpenOption.READ);
            ObjectInputStream objectInputStream = new ObjectInputStream(inputStream);
            PROSSettings settings = (PROSSettings) objectInputStream.readObject();
            this.setKernelDirectory(settings.getKernelDirectory());
            this.setUpdateSite(settings.getUpdateSite());
        } catch (ClassNotFoundException | IOException ignored) {
        }
    }

    public Path getKernelDirectory() {
        if (kernelDirectory == null || kernelDirectory.isEmpty()) {
            return Paths.get("");
        }
        return Paths.get(kernelDirectory);
    }

    private void setKernelDirectory(String kernelDirectory) {
        this.kernelDirectory = kernelDirectory;
    }

    public void setKernelDirectory(Path kernelDirectory) {
        this.kernelDirectory = kernelDirectory.toAbsolutePath().toString();
    }

    public URL getUpdateSite() {
        return updateSite;
    }

    public void setUpdateSite(URL updateSite) {
        this.updateSite = updateSite;
    }

    public void serialize() throws IOException {
        serialize(location);
    }

    private void serialize(Path location) throws IOException {
        Files.createDirectories(location.getParent());
        if (Files.isDirectory(location)) {
            throw new IOException(String.format("%s is a directory.", location.toString()));
        }
        if (Files.notExists(location)) {
            Files.createFile(location);
        }
        OutputStream outputStream = Files.newOutputStream(location);
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(outputStream);
        objectOutputStream.writeObject(this);
    }
}
