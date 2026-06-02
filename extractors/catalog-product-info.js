(() => {
  const marker = "window.__NUXT__=";

  for (const script of document.scripts) {
    const text = script.textContent || "";
    const index = text.indexOf(marker);
    if (index === -1) {
      continue;
    }

    let expression = text.slice(index + marker.length).trim();
    if (expression.endsWith(";")) {
      expression = expression.slice(0, -1);
    }

    const payload = Function('"use strict"; return (' + expression + ')')();
    const product = payload?.useState?.uniquePseudoAsyncDataStateKey?.product ?? null;
    return {
      data: JSON.stringify(product),
      type: "json",
    };
  }

  return {
    data: "null",
    type: "json",
  };
})()
