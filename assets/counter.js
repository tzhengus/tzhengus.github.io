/*
 * Counter.dev tracking client, vendored from:
 * https://github.com/ihucos/counter.dev/blob/a431dec7c91ad0da7451d0f3f9a56cbd6df5b542/docs/script.js
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Served locally because the site's representative DNS filter sinkholes
 * cdn.counter.dev. The data-server attribute points at the reachable
 * counter.dev host; Counter.dev's /track and /trackpage endpoints were
 * verified there before deployment.
 */
(function () {
    if (sessionStorage.getItem("doNotTrack") || localStorage.getItem("doNotTrack")) {
        return;
    }
    var id = document.currentScript.getAttribute("data-id");
    var utcoffset = document.currentScript.getAttribute("data-utcoffset");
    var server = document.currentScript.getAttribute("data-server") || "https://t.counter.dev";

    if (!sessionStorage.getItem("_swa") && !document.referrer.startsWith(location.protocol + "//" + location.host)) {
        setTimeout(function () {
            sessionStorage.setItem("_swa", "1");
            fetch(
                server +
                    "/track?" +
                    new URLSearchParams({
                        referrer: document.referrer,
                        screen: screen.width + "x" + screen.height,
                        id: id,
                        utcoffset: utcoffset,
                    }),
            );
        }, 4500);
    }
    navigator.sendBeacon(
        server + "/trackpage",
        new URLSearchParams({
            id: id,
            page: window.location.pathname,
        }),
    );
})();
