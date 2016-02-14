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

package edu.purdue.sigbots.ros.cli.management.updatesite;

import edu.purdue.sigbots.ros.cli.management.PROSActions;
import edu.purdue.sigbots.ros.cli.management.SimpleFileDeleter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class URLUpdateSiteProvider implements UpdateSiteProvider {

    public URLUpdateSiteProvider() {

    }

    @Override
    public boolean claimsURIString(String string, PROSActions caller) {
        return false;
    }

    @Override
    public URI reformURIString(String string, PROSActions caller) {
        return URI.create(string);
    }

    @Override
    public boolean canHandleURI(URI uri, PROSActions caller) {
        try {
            //noinspection ResultOfMethodCallIgnored
            uri.toURL();
            URL kernelsListURL = new URL(uri.toURL().toExternalForm() + "/kernels.list");
            URLConnection urlConnection = kernelsListURL.openConnection();
            urlConnection.setAllowUserInteraction(true);
            urlConnection.connect();
            return true;
        } catch (MalformedURLException | IllegalArgumentException e) {
            return false;
        } catch (IOException e) {
            return e instanceof UnknownHostException;
        }
    }

    @Override
    public List<String> getAvailableKernels(URI uri, PROSActions caller) throws IOException {
        try {
            URL kernelsListURL = new URL(uri.toURL().toExternalForm() + "/kernels.list");
            URLConnection urlConnection = kernelsListURL.openConnection();
            urlConnection.connect();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
            ArrayList<String> kernelList = new ArrayList<>();
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                kernelList.add(line);
            }
            return kernelList;
        } catch (MalformedURLException e) {
            return Collections.emptyList();
        }
    }

    @Override
    public String getLatestKernel(URI uri, PROSActions caller) throws IOException {
        URL latestKernelURL = new URL(uri.toURL().toExternalForm() + "/latest.kernel");
        URLConnection urlConnection = latestKernelURL.openConnection();
        urlConnection.connect();
        try (BufferedReader bufferedReader =
                     new BufferedReader(new InputStreamReader(urlConnection.getInputStream()))) {
            return bufferedReader.readLine();
        }

    }

    @Override
    public void downloadKernel(String kernel, PROSActions caller) throws IOException {
        URL kernelUrl = new URL(String.format("%s/%s.zip", caller.getUpdateSite().toString(), kernel));
        Path localKernel = caller.getLocalRepositoryPath().resolve(kernel);

        if (Files.exists(localKernel)) { // delete already existing kernel template
            Files.walkFileTree(localKernel, new SimpleFileDeleter(localKernel, caller.isVerbose()));
        }

        URLConnection urlConnection = kernelUrl.openConnection();
        urlConnection.connect();
        try (ZipInputStream zipInputStream = new ZipInputStream(urlConnection.getInputStream())) {
            ZipEntry zipEntry;
            while ((zipEntry = zipInputStream.getNextEntry()) != null) {
                if (caller.isVerbose()) {
                    caller.getOut().printf("Extracting %s\r\n", zipEntry.getName());
                }

                Path zipEntryPath = localKernel.resolve(zipEntry.getName());
                if (zipEntry.isDirectory()) {
                    Files.createDirectories(zipEntryPath);
                } else {
                    Files.createDirectories(zipEntryPath.getParent());
                    Files.copy(zipInputStream, zipEntryPath);
                }
            }
        }
    }
}
