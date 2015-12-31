package edu.purdue.sigbots.ros.cli;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

public class SimpleFileCopier extends SimpleFileVisitor<Path> {
    protected boolean verbose;
    protected PrintStream out;
    protected Path sourcePath;
    protected Path destinationPath;

    public SimpleFileCopier(boolean verbose, PrintStream out, Path sourcePath, Path destinationPath) {
        this.verbose = verbose;
        this.out = out;
        this.sourcePath = sourcePath;
        this.destinationPath = destinationPath;
    }

    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
        Path destinationDirectory = destinationPath.resolve(sourcePath.relativize(dir));
        if (verbose) {
            out.printf("Creating directory %s%s\r\n", destinationPath.relativize(destinationDirectory),
                    System.getProperty("file.separator"));
        }
        if (Files.notExists(destinationDirectory)) {
            Files.createDirectories(destinationDirectory);
        }
        return FileVisitResult.CONTINUE;
    }

    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
        if (verbose) {
            out.printf("Copying file %s\r\n", sourcePath.relativize(file));
        }
        Path destinationFile = destinationPath.resolve(sourcePath.relativize(file));
        if (Files.notExists(destinationFile)) {
            Files.createDirectories(destinationFile.getParent());
            Files.createFile(destinationFile);
        }
        Files.copy(file, destinationFile, StandardCopyOption.REPLACE_EXISTING);
        return FileVisitResult.CONTINUE;
    }
}
