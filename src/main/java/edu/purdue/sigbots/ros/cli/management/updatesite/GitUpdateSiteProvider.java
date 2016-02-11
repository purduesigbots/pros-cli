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
import org.eclipse.jgit.api.FetchCommand;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.MergeCommand;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.Constants;
import org.eclipse.jgit.lib.Ref;
import org.eclipse.jgit.merge.MergeStrategy;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.eclipse.jgit.transport.FetchResult;
import org.eclipse.jgit.transport.RefSpec;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

public class GitUpdateSiteProvider implements UpdateSiteProvider {
    private static final ProcessBuilder processBuilder = new ProcessBuilder();
    private final String uriRegex = "(https?|ftp|ssh)://(-\\.)?([^\\s/?\\.#-]+\\.?)+(/[^\\s]*)?";

    public GitUpdateSiteProvider() {
    }

    @Override
    public boolean claimsURIString(String string, PROSActions caller) {
        return string.matches("^git clone .*$");
    }

    @Override
    public URI reformURIString(String string, PROSActions caller) {
        return URI.create(string.matches("^git clone .*$") ? string.replaceFirst("^git clone ", "") : string);
    }

    @Override
    public boolean canHandleURI(URI uri, PROSActions caller) {
        String scheme = uri.getScheme();
        String path = uri.getPath();
        return (scheme.equalsIgnoreCase("git") || scheme.equalsIgnoreCase("ssh") || path.endsWith(".git"));

    }

    @Override
    public List<String> getAvailableKernels(URI uri, PROSActions caller) throws IOException {
        pullLatestGitRepository(uri, caller);

        return Files.list(caller.getLocalRepositoryPath())
                .filter(f -> Files.isDirectory(f) && !f.getFileName().toString().startsWith("."))
                .map(p -> p.getFileName().toString())
                .collect(Collectors.toList());
    }

    @Override
    public String getLatestKernel(URI uri, PROSActions caller) throws IOException {
        List<String> availableKernels = getAvailableKernels(uri, caller);
        availableKernels.sort(String::compareTo);
        return availableKernels.get(availableKernels.size() - 1);
    }

    @Override
    public void downloadKernel(String kernel, PROSActions caller) {

    }

    private void pullLatestGitRepository(URI uri, PROSActions caller) throws IOException {
        Path directory = caller.getLocalRepositoryPath();

        // Wire up JGit with ssh-agent/pageant whatever
        // Implementation based off of https://gist.github.com/quidryan/5449155
//        SshSessionFactory sshSessionFactory = new JschConfigSessionFactory() {
//            @Override
//            protected void configure(OpenSshConfig.Host host, Session session) {
//                session.setConfig("StrictHostKeyChecking", "false");
//            }
//
//            @Override
//            protected JSch createDefaultJSch(FS fs) throws JSchException {
//                Connector connector = null;
//                try {
//                    if (SSHAgentConnector.isConnectorAvailable()) {
//                        USocketFactory uSocketFactory = new JNAUSocketFactory();
//                        connector = new SSHAgentConnector(uSocketFactory);
//                    }
//                } catch (AgentProxyException e) {
//                    e.printStackTrace();
//                }
//
//                final JSch jsch = super.createDefaultJSch(fs);
//
//                if (connector != null) {
//                    JSch.setConfig("PreferredAuthentications", "publickey");
//                    IdentityRepository identityRepository = new RemoteIdentityRepository(connector);
//                    jsch.setIdentityRepository(identityRepository);
//                }
//
//                return jsch;
//            }
//        };
//        SshSessionFactory.setInstance(sshSessionFactory);

        // GOAL: Get git directory or create/initialize it if it doesn't exist
        Files.createDirectories(directory);
        Git git;
        try {
            if (!Files.exists(directory.resolve(".git"))) {
                if (caller.isVerbose()) {
                    caller.getOut().println("Initializing git repository in ~/.pros/kernels");
                }
                git = Git.init().setDirectory(directory.toFile()).call();
            } else {
                if (caller.isVerbose()) {
                    caller.getOut().println("Loading git repository in ~/.pros.kernels");
                }
                git = new Git(new FileRepositoryBuilder().setGitDir(directory.resolve(".git").toFile()).setMustExist(true).readEnvironment().findGitDir().build());
            }
            Ref ref = git.getRepository().findRef(Constants.HEAD);
            if (ref == null) {
                git.add().addFilepattern(".").call();
                git.commit().setMessage("Dummy commit for PROS CLI").setCommitter("PROS CLI", "pros_development@purdue.edu").call();
            }

            if (caller.isVerbose()) {
                caller.getOut().println("Fetching remote.");
            }

            FetchCommand fetchCommand = git.fetch();
//            if (uri.getScheme().equals("ssh")) {
//                fetchCommand.setTransportConfigCallback(transport -> ((SshTransport) transport).setSshSessionFactory(sshSessionFactory));
//            }
            fetchCommand.setRemote(uri.toString());
            fetchCommand.setRefSpecs(new RefSpec().setSource("HEAD").setDestination("refs/remotes/origin/HEAD"));
            FetchResult fetchResult = fetchCommand.call();
            fetchCommand.getRepository().close();

            if (caller.isVerbose()) {
                caller.getOut().println("Merging with local HEAD");
            }

            MergeCommand mergeCommand = git.merge();
            mergeCommand.include(fetchResult.getAdvertisedRef("HEAD"));
            mergeCommand.setStrategy(MergeStrategy.THEIRS);
            mergeCommand.call();

            if (caller.isVerbose()) {
                caller.getOut().println("Cleaning up");
            }

            mergeCommand.getRepository().close();
            git.getRepository().close();
            git.close();
        } catch (GitAPIException e) {
            e.printStackTrace();
            throw new IOException(e);
        }
    }

//    private void executeProcessCommand(PROSActions actions, String... command) throws IOException {
//        processBuilder.directory(actions.getLocalRepositoryPath().toFile());
//        processBuilder.command(command);
//        Process process = processBuilder.start();
//        if (actions.isVerbose()) {
//            (new StreamGobbler(process.getInputStream(), actions.getOut())).start();
//            (new StreamGobbler(process.getErrorStream(), actions.getErr())).start();
//        }
//        while (process.isAlive()) {
//            try {
//                Thread.sleep(10);
//            } catch (InterruptedException ignored) {
//            }
//        }
//    }
}
