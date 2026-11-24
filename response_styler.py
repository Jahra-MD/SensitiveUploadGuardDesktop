
RESPONSE_STYLE_SCRIPT = r"""
(function () {

    const RESPONSE_COLOR = "#22c55e";

    let previousCount = -1;

    function applyResponseColor() {

        let selectors;

        if (location.hostname === "chatgpt.com") {

            selectors = [
                '[data-message-author-role="assistant"]',
                '[data-message-author-role="assistant"] *',

                '[data-assistant-markdown]',
                '[data-assistant-markdown] *',

                '[data-assistant-markdown-root]',
                '[data-assistant-markdown-root] *',

                '[data-dil-response]',
                '[data-dil-response] *',

                '[data-dil-response] [data-d-component="text"]'
            ];

        } else if (
            location.hostname === "perplexity.ai" ||
            location.hostname.endsWith(".perplexity.ai")
        ) {

            selectors = [
                '.prose',
                '.prose *'
            ];

        } else {
            return;
        }

        const elements = document.querySelectorAll(
            selectors.join(",")
        );

        elements.forEach(element => {

            if (element.closest(
                "button, svg, input, textarea, " +
                "[role='button'], [contenteditable='true']"
            )) {
                return;
            }

            element.style.setProperty(
                "color",
                RESPONSE_COLOR,
                "important"
            );

            element.style.setProperty(
                "--x-color",
                RESPONSE_COLOR,
                "important"
            );

            element.style.setProperty(
                "--d-inherited-text-color",
                RESPONSE_COLOR,
                "important"
            );

            element.style.setProperty(
                "-webkit-text-fill-color",
                RESPONSE_COLOR,
                "important"
            );

        });

        if (elements.length !== previousCount) {

            previousCount = elements.length;

            console.log(
                "[SensitiveUploadGuard] " +
                location.hostname +
                " | Styled elements: " +
                elements.length
            );
        }
    }

    if (window.__guardResponseObserver) {
        window.__guardResponseObserver.disconnect();
    }

    if (window.__guardStyleTimer) {
        clearInterval(window.__guardStyleTimer);
    }

    const observer = new MutationObserver(() => {
        applyResponseColor();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    window.__guardResponseObserver = observer;

    // Reapply styles if the website resets them.
    window.__guardStyleTimer = setInterval(
        applyResponseColor,
        1500
    );

    applyResponseColor();

    console.log(
        "[SensitiveUploadGuard] Response styling enabled"
    );

})();
"""
