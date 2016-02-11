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

package edu.purdue.sigbots.ros.cli.management;

import org.junit.Before;
import org.junit.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.net.URI;
import java.nio.file.Paths;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class PROSActionsTest {

    @Before
    public void setUp() {
        Class<PROSActions> prosActionsClass = PROSActions.class;
        try {
            Field settingsPathField = prosActionsClass.getDeclaredField("SETTINGS_PATH");
            settingsPathField.setAccessible(true);

            Field modifiersField = Field.class.getDeclaredField("modifiers");
            modifiersField.setAccessible(true);
            modifiersField.setInt(settingsPathField, settingsPathField.getModifiers() & ~Modifier.FINAL);

            settingsPathField.set(null, Paths.get("out", "test", "cli-settings.json"));
        } catch (NoSuchFieldException | IllegalAccessException e) {
            e.printStackTrace();
        }

    }

    @Test
    public void testGetUpdateSite() throws Exception {
        URI testURI = URI.create("test://pros");
        PROSActions actions = new PROSActions();
        Field updateSiteField = PROSActions.class.getDeclaredField("updateSite");
        updateSiteField.setAccessible(true);
        updateSiteField.set(actions, testURI);
        assertEquals(testURI, actions.getUpdateSite());
    }

    @Test
    public void testSetUpdateSite() throws Exception {
        String testURI = "test://pros";
        PROSActions actions = new PROSActions();
        actions.setUpdateSite(testURI);
        assertEquals(URI.create(testURI), actions.getUpdateSite());
    }

    @Test
    public void testSuggestUpdateSite() throws Exception {
        assertNotNull((new PROSActions()).suggestUpdateSite());
    }

    @Test
    public void testGetLocalRepositoryPath() throws Exception {

        PROSActions actions = new PROSActions();
        actions.getLocalRepositoryPath();
    }

    @Test
    public void testSetLocalKernelRepository() throws Exception {

    }

    @Test
    public void testSetLocalKernelRepository1() throws Exception {

    }

    @Test
    public void testSuggestLocalKernelRepository() throws Exception {

    }

    @Test
    public void testGetAllKernels() throws Exception {

    }

    @Test
    public void testGetAllKernels1() throws Exception {

    }

    @Test
    public void testGetAllKernelsForce() throws Exception {

    }

    @Test
    public void testResolveKernelUpdateRequest() throws Exception {

    }

    @Test
    public void testResolveKernelLocalRequest() throws Exception {

    }

    @Test
    public void testCreateLoader() throws Exception {

    }

    @Test
    public void testFindKernelDirectory() throws Exception {

    }

    @Test
    public void testCreateProject() throws Exception {

    }

    @Test
    public void testCreateProject1() throws Exception {

    }

    @Test
    public void testUpgradeProject() throws Exception {

    }

    @Test
    public void testUpgradeProject1() throws Exception {

    }

    @Test
    public void testListEnvironments() throws Exception {

    }

    @Test
    public void testListEnvironments1() throws Exception {

    }

    @Test
    public void testDownloadKernel() throws Exception {

    }

    @Test
    public void testDeleteKernel() throws Exception {

    }

    @Test
    public void testDeleteKernel1() throws Exception {

    }
}
