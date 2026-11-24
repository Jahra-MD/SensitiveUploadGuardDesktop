
RESPONSE_STYLE_SCRIPT = r"""
(function () {

    const RESPONSE_COLOR = "#22c55e";

    let previousCount = -1;

    function applyResponseColor() {

        let selectors;

        if (location.hostname.includes("chatgpt.com")) {

            selectors = [
                '[data-assistant-markdown]',
                '[data-assistant-markdown] *',
                '[data-assistant-markdown-root]',
                '[data-assistant-markdown-root] *',
                '[data-message-author-role="assistant"] .markdown',
                '[data-message-author-role="assistant"] .markdown *'
            ];

        } else if (
            location.hostname.includes("perplexity.ai")
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
                "button, svg, input, textarea"
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

    const observer = new MutationObserver(() => {
        applyResponseColor();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    window.__guardResponseObserver = observer;

    applyResponseColor();

    console.log(
        "[SensitiveUploadGuard] Response styling enabled"
    );

})();
"""
