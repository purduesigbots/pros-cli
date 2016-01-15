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

package edu.purdue.sigbots.ros.cli.kernels;

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;

public abstract class Loader {
    final boolean verbose;
    final PrintStream out;
    final PrintStream err;

    public Loader(Boolean verbose, PrintStream out, PrintStream err) {
        this.verbose = verbose;
        this.out = out;
        this.err = err;
    }

    /**
     * Creates a project, overwriting any existing files that were previously there, but does not delete extra files
     *
     * @param kernelPath   A valid path to a kernel directory
     * @param projectPath  A valid directory representing the project
     * @param environments A list of environments that may be empty or null (in which case no environments will be targeted)
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public abstract void createProject(Path kernelPath, Path projectPath, List<String> environments) throws IOException;

    /**
     * Upgrades a project, overwriting any existing files that were previously there, but does not delete extra files
     *
     * @param kernelPath   A valid path to a kernel directory
     * @param projectPath  A valid directory representing the project
     * @param environments A list of environments that may be null (in which case no environments will be targeted)
     *                     or empty (in which case the Loader should find the previously targeted environments and upgrade those)
     * @throws IOException Thrown if there was an exception copying the project.
     *                     The copying process is non-transactional and an exception may be thrown in the middle of the copying
     *                     process, so some files may have been copied while others have not.
     */
    public abstract void upgradeProject(Path kernelPath, Path projectPath, List<String> environments) throws IOException;

    /**
     * @param kernelPath A valid path to a kernel directory
     * @return A set of valid environments that can be targeted by this loader. Should always contain at least 'none'
     * @throws IOException Thrown if there was an exception accessing the kernel directory
     */
    public abstract Set<String> getAvailableEnvironments(Path kernelPath) throws IOException;
}
