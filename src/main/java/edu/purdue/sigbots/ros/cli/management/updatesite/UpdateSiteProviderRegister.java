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

import java.net.URI;
import java.util.*;

public final class UpdateSiteProviderRegister {
    private static Set<UpdateSiteProvider> updateSiteProviders;
    private static Map<URI, UpdateSiteProvider> uriCache = new HashMap<>();

    private UpdateSiteProviderRegister() {
    }

    public static void registerUpdateSiteProvider(UpdateSiteProvider provider) {
        if (updateSiteProviders == null) {
            updateSiteProviders = new LinkedHashSet<>();
        }

        updateSiteProviders.add(provider);
    }

    public static Set<UpdateSiteProvider> getUpdateSiteProviders() {
        return updateSiteProviders;
    }

    public static void replaceUpdateSiteProviders(Set<UpdateSiteProvider> providersList) {
        updateSiteProviders = providersList;
    }

    public static UpdateSiteProvider findUpdateSiteProvider(URI uri, PROSActions caller) {
        if (uriCache.containsKey(uri)) {
            return uriCache.get(uri);
        }
        if (updateSiteProviders == null) {
            throw new NoSuchElementException("Could not resolve a URI handler as the list has not been initialized.");
        }
        for (UpdateSiteProvider provider : updateSiteProviders) {
            if (provider.canHandleURI(uri, caller)) {
                uriCache.put(uri, provider);
                return provider;
            }
        }
        throw new NoSuchElementException("Could not resolve a URI handler for this request (" + uri.toASCIIString() + ")");
    }

    public static UpdateSiteProvider getClaimingUpdateSiteProvider(String string, PROSActions caller) {
        if (updateSiteProviders == null) {
            return null;
        }
        for (UpdateSiteProvider provider : updateSiteProviders) {
            if (provider.claimsURIString(string, caller)) {
                return provider;
            }
        }
        return null;
    }
}
