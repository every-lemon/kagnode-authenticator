/* Styled, keyboard-operated choices; the underlying select owns form values. */
(() => {
  const instances = new Map();
  function enhance(root = document) {
    root.querySelectorAll("select").forEach((select) => {
      if (instances.has(select)) return;
      const wrap = document.createElement("div");
      wrap.className = "custom-select";
      select.before(wrap);
      wrap.append(select);
      select.tabIndex = -1;
      select.setAttribute("aria-hidden", "true");
      const trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className = "select-trigger";
      trigger.setAttribute("role", "combobox");
      trigger.setAttribute("aria-haspopup", "listbox");
      trigger.setAttribute("aria-expanded", "false");
      const label =
        select.getAttribute("aria-label") ||
        document
          .querySelector(`label[for="${select.id}"]`)
          ?.textContent.trim() ||
        "Choose an option";
      trigger.setAttribute("aria-label", label);
      const text = document.createElement("span");
      trigger.append(text);
      trigger.insertAdjacentHTML(
        "beforeend",
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
      );
      const list = document.createElement("div");
      list.id = `${select.id}-options`;
      list.className = "select-options";
      list.hidden = true;
      list.setAttribute("role", "listbox");
      list.setAttribute("aria-label", label);
      trigger.setAttribute("aria-controls", list.id);
      wrap.append(trigger, list);
      const buttons = [...select.options].map((option, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "select-option";
        button.setAttribute("role", "option");
        button.textContent = option.textContent;
        button.disabled = option.disabled;
        button.addEventListener("click", () => {
          select.selectedIndex = index;
          select.dispatchEvent(new Event("change", { bubbles: true }));
          sync();
          close();
          trigger.focus();
        });
        list.append(button);
        return button;
      });
      function sync() {
        text.textContent = select.selectedOptions[0]?.textContent || "";
        trigger.disabled = select.disabled;
        buttons.forEach((b, i) =>
          b.setAttribute("aria-selected", String(select.selectedIndex === i)),
        );
      }
      function close() {
        list.hidden = true;
        trigger.setAttribute("aria-expanded", "false");
      }
      function open() {
        instances.forEach((item) => item.close());
        sync();
        list.hidden = false;
        trigger.setAttribute("aria-expanded", "true");
        const bottom =
          select.closest("dialog")?.getBoundingClientRect().bottom ||
          innerHeight;
        wrap.classList.toggle(
          "opens-up",
          bottom - trigger.getBoundingClientRect().bottom <
            Math.min(260, buttons.length * 44 + 16),
        );
        buttons[select.selectedIndex]?.focus();
      }
      trigger.addEventListener("click", () => (list.hidden ? open() : close()));
      trigger.addEventListener("keydown", (event) => {
        if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
          event.preventDefault();
          open();
          if (event.key === "Home") buttons[0].focus();
          if (event.key === "End") buttons.at(-1).focus();
        }
      });
      list.addEventListener("keydown", (event) => {
        const index = buttons.indexOf(document.activeElement);
        let next;
        if (event.key === "ArrowDown") next = (index + 1) % buttons.length;
        if (event.key === "ArrowUp")
          next = (index - 1 + buttons.length) % buttons.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = buttons.length - 1;
        if (next !== undefined) {
          event.preventDefault();
          buttons[next].focus();
        }
        if (event.key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          close();
          trigger.focus();
        }
        if (event.key === "Tab") close();
      });
      select.addEventListener("change", sync);
      instances.set(select, { sync, close, wrap });
      sync();
    });
  }
  document.addEventListener("pointerdown", (event) =>
    instances.forEach((item) => {
      if (!item.wrap.contains(event.target)) item.close();
    }),
  );
  document.addEventListener("focusin", (event) =>
    instances.forEach((item) => {
      if (!item.wrap.contains(event.target)) item.close();
    }),
  );
  window.KagNodeControls = {
    enhance,
    sync() {
      enhance();
      instances.forEach((item) => item.sync());
    },
    close() {
      instances.forEach((item) => item.close());
    },
  };
})();
