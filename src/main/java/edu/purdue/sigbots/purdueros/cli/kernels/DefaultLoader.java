package edu.purdue.sigbots.purdueros.cli.kernels;

import org.apache.commons.io.FileUtils;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

@SuppressWarnings("ResultOfMethodCallIgnored")
public class DefaultLoader implements LoaderInterface {
    private static final String FILE_SEP = System.getProperty("file.separator");
    private static final String TEMPLATE_TEXT = "Default_VeX_Cortex";
    String[] upgradeFiles = new String[]{
            "firmware" + FILE_SEP + "libccos.a",
            "firmware" + FILE_SEP + "uniflash.jar",
            "include" + FILE_SEP + "API.h",
            "src" + FILE_SEP + "Makefile",
            "Makefile"
    };
    String[] templatedFiles = new String[]{
            ".project"
    };

    @Override
    public void createProject(String projectPath, String kernelPath, String projectName) throws IOException {
        if (!projectPath.endsWith(FILE_SEP)) projectPath += FILE_SEP;
        if (!kernelPath.endsWith(FILE_SEP)) kernelPath += FILE_SEP;
        if (projectName == null) projectName = "";

        File projectFile = new File(projectPath);
        if (projectFile.exists())
            FileUtils.deleteDirectory(projectFile);

        FileUtils.copyDirectory(new File(kernelPath), projectFile);

        for (String templateFile : templatedFiles) {
            replaceTextInFile(projectPath + templateFile, TEMPLATE_TEXT, projectName);
        }
        System.out.println("Creating project!");
    }

    @Override
    public void upgradeProject(String projectPath, String kernelPath, String projectName) throws IOException {
        if (!projectPath.endsWith(FILE_SEP)) projectPath += FILE_SEP;
        if (!kernelPath.endsWith(FILE_SEP)) kernelPath += FILE_SEP;
        System.out.println("Upgrading project!");
        for (String file : upgradeFiles) {
            System.out.println("Upgrading " + file);
            InputStream inputStream = new FileInputStream(kernelPath + file);
            Path filePath = new File(projectPath + file).toPath();
            new File(filePath.toString()).mkdirs();
            Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
        }
        System.out.println("\nUpgraded project to " + new File(kernelPath).getName());
    }

    void replaceTextInFile(String path, String original, String replacement) throws IOException {
        File tempFile = File.createTempFile(path, null);
        try (FileWriter writer = new FileWriter(tempFile)) {
            try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
                String s;
                while ((s = reader.readLine()) != null) {
                    s = s.replace(original, replacement);
                    writer.write(s + "\r\n");
                }
            }
        }
        Files.copy(tempFile.toPath(), new File(path).toPath(), StandardCopyOption.REPLACE_EXISTING);
    }
}
