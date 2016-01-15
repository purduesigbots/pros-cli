/*******************************************************************************
 * Copyright (c) 2016, Purdue University ACM SIG BOTS.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Purdue University ACM SIG BOTS nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 ******************************************************************************/

package edu.purdue.sigbots.ros.cli.updater;

import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

/* TODO: PROSSettings should serialize to JSON */
class PROSSettings implements Serializable {
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

    public void setKernelDirectory(Path kernelDirectory) {
        this.kernelDirectory = kernelDirectory.toAbsolutePath().toString();
    }

    private void setKernelDirectory(String kernelDirectory) {
        this.kernelDirectory = kernelDirectory;
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
