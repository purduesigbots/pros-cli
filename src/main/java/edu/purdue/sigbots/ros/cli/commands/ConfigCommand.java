/*******************************************************************************
 * Copyright (c) 2015, Purdue University ACM SIG BOTS.
 * All rights reserved.
 * <p>
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * <p>
 * * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * * Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * * Neither the name of the Purdue University ACM SIG BOTS nor the
 * names of its contributors may be used to endorse or promote products
 * derived from this software without specific prior written permission.
 * <p>
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

package edu.purdue.sigbots.ros.cli.commands;

import edu.purdue.sigbots.ros.cli.updater.PROSActions;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.IOException;
import java.net.URL;
import java.nio.file.Paths;

public class ConfigCommand extends Command {
    @Override
    public void handleArguments(Namespace arguments, PROSActions actions) {
        String variable = arguments.getString("variable");
        String value = arguments.get("value");
        if (variable.equalsIgnoreCase("updateSite") || variable.equalsIgnoreCase("update-site")) {
            if (value != null && !value.isEmpty()) {
                try {
                    actions.setUpdateSite(new URL(value));
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            System.out.printf("Update site is set to: %s\r\n", actions.getUpdateSite());
        } else if (variable.equalsIgnoreCase("localRepository") || variable.equalsIgnoreCase("local-repository")) {
            if (value != null && !value.isEmpty()) {
                try {
                    actions.setLocalKernelRepository(Paths.get(value));
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            System.out.printf("Local kernel repository is set to: %s", actions.getLocalRepositoryPath());
        }
    }
}
