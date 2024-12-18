function modifyDocumentElement() {
  const documentElement = document.querySelector('[role="document"]');
  if (documentElement) {
    documentElement.style.overflowY = "unset";

    const pElement = documentElement.querySelector("p");
    if (pElement) {
      const boldText = pElement.querySelector("b");
      if (boldText && boldText.textContent === "Sentence:") {
        boldText.remove();

        const originalText = pElement.textContent;
        const modifiedText = originalText.replace(/\s+/g, "");
        pElement.textContent = modifiedText;

        pElement.style.fontSize = "24px";

        pElement.contentEditable = "true";
        pElement.setAttribute("contenteditable", "true");
      }
    }

    const flexColElement = document.querySelector('[class="flex flex-col gap-2"]');
    if (flexColElement) {
      flexColElement.classList.remove('flex-col');
      flexColElement.classList.add('flex-row');

      const pElement = flexColElement.querySelector("p");
      const buttons = flexColElement.querySelectorAll("button");

      const rightContainer = document.createElement("div");
      Object.assign(rightContainer.style, {
        display: "flex",
        flexDirection: "column",
      });
      if (rightContainer) {
        rightContainer.appendChild(pElement);
        rightContainer.appendChild(buttons[0]);
        rightContainer.appendChild(buttons[1]);

        flexColElement.appendChild(rightContainer);

        const buttonsContainer = document.createElement("div");
        buttonsContainer.style.display = "flex";
        buttonsContainer.style.gap = "0.5rem";
        buttonsContainer.style.justifyContent = "center";
        buttonsContainer.style.minWidth = "340px";

        buttonsContainer.appendChild(buttons[0]);
        buttonsContainer.appendChild(buttons[1]);

        rightContainer.appendChild(buttonsContainer);

        var cDiv = buttonsContainer.children;
        for (var i = 0; i < cDiv.length; i++) {
          if (cDiv[i].tagName == "BUTTON") {
            cDiv[i].style.width = '50%';
          }
        }
      }
    }
  }

  const dialogElement = document.querySelector('[role="dialog"]');
  if (dialogElement) {
    const topBar = document.querySelector('[class="bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-700 divide-gray-200 dark:divide-gray-700 flex justify-between items-center p-4 rounded-t border-b"]');
    if (topBar) {
      topBar.remove();
    }
  }

  const overlayElement = document.querySelector('[class="flex relative max-w-2xl w-full max-h-full"]');
  if (overlayElement) {
    overlayElement.style.maxWidth = "55rem";
  }

  const svelteAnnouncer = document.getElementById('svelte-announcer');
  if (svelteAnnouncer) {
    svelteAnnouncer.remove();
  }
}

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      modifyDocumentElement();
    }
  }
});

observer.observe(document.body, { childList: true, subtree: true });

modifyDocumentElement();
