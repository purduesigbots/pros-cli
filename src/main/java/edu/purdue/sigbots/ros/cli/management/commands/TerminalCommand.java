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

package edu.purdue.sigbots.ros.cli.management.commands;

import edu.purdue.sigbots.ros.cli.management.PROSActions;
import jssc.SerialPortList;
import net.sourceforge.argparse4j.impl.action.StoreTrueArgumentAction;
import net.sourceforge.argparse4j.inf.Namespace;
import net.sourceforge.argparse4j.inf.Subparser;

import java.util.Arrays;

public class TerminalCommand extends Command {
    public static void createArgs(Subparser subparser) {
        subparser.defaultHelp(true)
                .setDefault("handler", TerminalCommand.class);
        subparser.addArgument("port")
                .nargs("?")
                .setDefault("auto")
                .help("Specify a port to connect to. If specified port is not detected as a " +
                        "VEX COM port, will continue to try to connect anyway.");
        subparser.addArgument("-l", "--list")
                .action(new StoreTrueArgumentAction())
                .help("Use this flag to get a list of all valid VEX COM ports connected to this computer.");
        subparser.addArgument("-v", "--verbose")
                .action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
    }

    @Override
    public void handleArguments(Namespace arguments, PROSActions actions) {
        if (arguments.getBoolean("list")) {
            System.out.println("Listing serial ports: ");
            System.out.println(Arrays.toString(SerialPortList.getPortNames()));
        }
    }
}
