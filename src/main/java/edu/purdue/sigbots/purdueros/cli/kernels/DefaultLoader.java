package edu.purdue.sigbots.purdueros.cli.kernels;

import org.apache.commons.io.FileUtils;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

@SuppressWarnings("ResultOfMethodCallIgnored")
public class DefaultLoader extends Loader {
    private static final String TEMPLATE_TEXT = "Default_VeX_Cortex";
    private final String[] upgradeFiles = new String[]{
            "firmware" + FILE_SEP + "libccos.a", // this file must exist in order for isUpgradeableProject to pass
            "firmware" + FILE_SEP + "uniflash.jar",
            "include" + FILE_SEP + "API.h",
            "src" + FILE_SEP + "Makefile",
            "Makefile",
            "common.mk"
    };
    private final String[] eclipseFiles = new String[]{
            ".project",
            ".cproject"
    };
    private final String[] templatedFiles = new String[]{

    };

    public DefaultLoader(String projectPath, String kernelPath, String projectName, String environments) {
        super(projectPath, kernelPath, projectName, environments);
    }

    @Override
    public void createProject() throws IOException {
        File projectFile = new File(projectPath);
        if (projectFile.exists())
            FileUtils.deleteDirectory(projectFile);

        FileUtils.copyDirectory(new File(kernelPath), projectFile);

        if (!environments.contains("eclipse")) {
            for (String eclipseFile : eclipseFiles)
                FileUtils.deleteQuietly(new File(projectPath, eclipseFile));
        } else {
            replaceTextInFile(projectPath + ".project", TEMPLATE_TEXT, projectName);
        }

        /* TODO: support the other environments */

        for (String templateFile : templatedFiles) {
            replaceTextInFile(projectPath + templateFile, TEMPLATE_TEXT, projectName);
        }

        System.out.println("Created project!");
    }

    @Override
    public void upgradeProject() throws IOException {
        for (String file : upgradeFiles) {
            System.out.println("Upgrading " + file);
            InputStream inputStream = new FileInputStream(kernelPath + file);
            Path filePath = new File(projectPath + file).toPath();
            new File(filePath.toString()).mkdirs();
            Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
        }
        if (!environments.contains("eclipse")) {
            for (String file : eclipseFiles) {
                System.out.println("Upgrading " + file);
                InputStream inputStream = new FileInputStream(kernelPath + file);
                Path filePath = new File(projectPath + file).toPath();
                new File(filePath.toString()).mkdirs();
                Files.copy(inputStream, filePath, StandardCopyOption.REPLACE_EXISTING);
            }
            replaceTextInFile(projectPath + ".project", TEMPLATE_TEXT, projectName);
        }
        System.out.println("\nUpgraded project to " + new File(kernelPath).getName());
    }

    @Override
    public boolean isUpgradeableProject() throws IOException {
        return new File(projectPath + upgradeFiles[0]).exists();
    }

    private void replaceTextInFile(String path, String original, String replacement) throws IOException {
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
